"""
Stateful Agent Processor for the Intake Example in: https://github.com/pipecat-ai/pipecat/blob/6071920c45a95089707ad40570f4d81f01d70e99/examples/patient-intake
"""
from loguru import logger
from pipecat.processors.frame_processor import FrameDirection
from pipecat.services.openai import (
    OpenAILLMContext,
    OpenAILLMContextFrame,
    OpenAILLMService
)
from datetime import datetime, timedelta


class IntakeProcessor:
    def __init__(
        self,
        context: OpenAILLMContext,
        llm: OpenAILLMService,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self._context: OpenAILLMContext = context
        self._llm = llm
        print(f"Initializing context from IntakeProcessor")
        self._context.add_message({"role": "system", "content": "You are Jessica, a magic assistant created by the best minds of UPC. You are 42 years old. You work at 2066 Crist Drive in Los Altos, California. Your job is to collect important information from the user before their doctor visit. You should help the user and be polite and professional. You're not a medical professional, so you shouldn't provide any advice. Keep your responses short. Your job is to help schedule an appointment for the doctor. Don't make assumptions about what values to plug into functions. Ask for clarification if a user response is ambiguous. Start by introducing yourself. Then, ask the user to confirm their identity by telling you their birthday, including the year. When they answer with their birthday, call the verify_birthday function."})
        self._context.set_tools([
            {
                "type": "function",
                "function": {
                    "name": "verify_birthday",
                    "description": "Use this function to verify the user has provided their correct birthday.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "birthday": {
                                "type": "string",
                                "description": "The user's birthdate, including the year. The user can provide it in any format, but convert it to YYYY-MM-DD format to call this function.",
                            }},
                    },
                },
            }])
        # Create an allowlist of functions that the LLM can call
        self._functions = [
            "verify_birthday",
            "make_appointment",
        ]

        llm.register_function("verify_birthday", self.verify_birthday)
        llm.register_function(
            "make_appointment", self.make_appointment)

    async def verify_birthday(self, llm, args):
        print("VERIFYING BIRTHDAY")

        try:
            year, month, day = [int(x) for x in args["birthday"].split("-")]
            if (year + month + day) % 3 == 0:
                return [{"role": "system", "content": "The user provided a birthday that is not validated. Tell the user that the records were not found in the system and end the conversation."}]
            today = datetime.today()
            cutoff_date = today.replace(year=today.year - 18)
            if datetime.strptime(args["birthday"], "%Y-%m-%d") > cutoff_date:
                return [{"role": "system", "content": "The user is too young (below 18). Tell that to the user and end the conversation."}]
            self._context.set_tools(
                [
                    {
                        "type": "function",
                        "function": {
                            "name": "make_appointment",
                            "description": "Once the user has provided a day and hour for an appointment call this function.",
                                "parameters": {
                                    "type": "object",
                                    "properties": {
                                            "appointment_day": {
                                                "type": "string",
                                                "description": "The user requested day for the appointment. The user can provide it in any format, but convert it to MM-DD format to call this function.",
                                            },
                                            "appointment_hour": {
                                                "type": "string",
                                                "description": "The user requested hour for the appointment. The user can provide it in any format, but convert it to HH:MM in 24 hour format to call this function.",
                                            },
                                        },
                                },
                        },
                    }])
            
            return [{"role": "system", "content": "Next, thank the user for confirming their birthday, then tell the user that the doctor availability is Monday 7/22 at 12pm Tuesday 7/23 a 3pm and any date and time after Tuesday. Today is "
                      + today.strftime("%m/%d") +
                     ". When the user tells his/her prefered time call make_apointment function."}]

        except Exception as e:
            print("ERROR in verify birthday call")
            print(f"Exception type: {type(e).__name__}")
            print(f"Exception message: {e}")
            return []
        

    async def make_appointment(self, llm, args):
        print("MAKING APP")
        month, day = [int(x) for x in args["appointment_day"].split("-")]
        hour, minute = [int(x) for x in args["appointment_hour"].split(":")]
        if not self.check_possible_apointment(month, day, hour, minute):
                return [{"role": "system", "content": "The user provided a non-possible appointment, ask the user to book another time."}]
        self._context.set_tools([])
        return [{"role": "system", "content": "The user booked an appointment. Remember the user the day and time of the appointment and say good bye."}]

    
    def check_possible_apointment(self, month, day, hour, minute):
        if [month, day, hour, minute] in [[7,22,12,0], [7,23,15,0]]:
            return True
        minute = 60*hour + minute
        if minute < 540 or minute > 1140:
            return False
        if month > 7 or (month == 7 and day >= 24):
            return True
        return False
    
    async def start_visit_reasons(self, llm):
        print("!!! doing start visit reasons")
        # move to finish call
        self._context.set_tools([])
        self._context.add_message({"role": "system",
                                   "content": "Now, thank the user and end the conversation."})
        await llm.process_frame(OpenAILLMContextFrame(self._context), FrameDirection.DOWNSTREAM)

    async def save_data(self, llm, args):
        logger.info(f"!!! Saving data: {args}")
        # Since this is supposed to be "async", returning None from the callback
        # will prevent adding anything to context or re-prompting
        return None
    

