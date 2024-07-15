"""
Stateful Agent Processor for the Intake Example in: https://github.com/pipecat-ai/pipecat/blob/6071920c45a95089707ad40570f4d81f01d70e99/examples/patient-intake
"""
from loguru import logger
from pipecat.processors.frame_processor import FrameDirection
from pipecat.frames.frames import EndFrame
from pipecat.services.openai import (
    OpenAILLMContext,
    OpenAILLMContextFrame,
    OpenAILLMService
)
from datetime import datetime


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
        from loguru import logger
        logger.info("Initializing context from IntakeProcessor")

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
            "confirm_appointment",
            "end_session",
        ]

        llm.register_function("verify_birthday", self.verify_birthday)
        llm.register_function(
            "make_appointment", self.make_appointment)
        llm.register_function(
            "confirm_appointment", self.confirm_appointment)
        llm.register_function(
            "end_session", self.end_session)
        self.appointment_day = None
        self.appointment_hour = None

    async def verify_birthday(self, llm, args):
        from loguru import logger
        logger.info("VER BIRTH")
        try:
            year, month, day = [int(x) for x in args["birthday"].split("-")]
            if (year + month + day) % 3 == 0:
                self._context.set_tools([{
                            "type": "function",
                            "function": {
                                "name": "end_session",
                                "description": "Call this before saying goodbay to make sure the session ends.",
                            }}])
                return [{"role": "system", "content": "The user provided a birthday that is not validated. Tell the user that the records were not found in the system. Call end_session just before that."}]
            today = datetime.today()
            cutoff_date = today.replace(year=today.year - 18)
            if datetime.strptime(args["birthday"], "%Y-%m-%d") > cutoff_date:
                self._context.set_tools([{
                            "type": "function",
                            "function": {
                                "name": "end_session",
                                "description": "Call this before saying goodbay to make sure the session ends.",
                            }}])
                return [{"role": "system", "content": "The user is too young (below 18). Tell that to the user. Call end_session just before that."}]
            self._context.set_tools(
                [
                    {
                        "type": "function",
                        "function": {
                            "name": "make_appointment",
                            "description": "Once the user has provided a day and hour for an appointment call this function. Make sure that the user is clear in the day and time. If he/she is not clear about it ask again.",
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

            from loguru import logger
            logger.exception("ERROR in verify birthday call")
            logger.exception(f"Exception type: {type(e).__name__}")
            logger.exception(f"Exception message: {e}")
            return []
        

    async def make_appointment(self, llm, args):
        try:
            from loguru import logger
            logger.info("MAKING APP")
            month, day = [int(x) for x in args["appointment_day"].split("-")]
            hour, minute = [int(x) for x in args["appointment_hour"].split(":")]
            if not self.check_possible_apointment(month, day, hour, minute):
                    return [{"role": "system", "content": "The user provided a non-possible appointment, ask the user to book another time."}]
            self._context.set_tools([{
                            "type": "function",
                            "function": {
                                "name": "confirm_appointment",
                                "description": "Call this when the user confirmed the appointment.",
                            }}])
            return [{
                "role": "system",
                "content": "The user booked an appointment. Remember the user the day (" + str(month) + "/" + str(day) + ") and time (" + str(hour) + ":" + str(minute) + ") of the appointment and ask the user to re-confirm the appointment booking. Call confirm_appointment when the user confirmed."
                }]
        except Exception as e:
            from loguru import logger
            logger.exception("ERROR in make_appointment")
            logger.exception(f"Exception type: {type(e).__name__}")
            logger.exception(f"Exception message: {e}")
            return []
        

    async def confirm_appointment(self, llm, args):
        try:
            from loguru import logger
            logger.info("CONF APP")
            self.communicate_appointment_to_server(self.appointment_day, self.appointment_hour)
            self._context.set_tools([{
                            "type": "function",
                            "function": {
                                "name": "end_session",
                                "description": "Call this before saying goodbay to make sure the session ends.",
                            }}])
            return [{
                "role": "system",
                "content": "The user confirmed the appointment. Say good bye. Call end_session just before that."
                }]
        except Exception as e:
            from loguru import logger
            logger.exception("ERROR in confirm_appointment")
            logger.exception(f"Exception type: {type(e).__name__}")
            logger.exception(f"Exception message: {e}")
            return []

    async def end_session(self, llm, args):
        from loguru import logger
        logger.info("END SESS")
        self._context.set_tools([])
        await self._llm.push_frame(EndFrame())
        return [{"role": "system", "content": "Always say goodbye before exiting."}]


    def communicate_appointment_to_server(self, day, hour):
        pass

    def check_possible_apointment(self, month, day, hour, minute):
        if [month, day, hour, minute] in [[7,22,12,0], [7,23,15,0]]:
            return True
        minute = 60*hour + minute
        if minute < 540 or minute > 1140:
            return False
        if month > 7 or (month == 7 and day >= 24):
            return True
        return False
