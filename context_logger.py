"""
 ContextLogger is a FrameProcessor which should print in the console the
 conversation context after each message. Additionally, it could also save
 the conversation transcript to a file. Feel free to get creative here.
"""
import os
from pipecat.processors.frame_processor import FrameProcessor
from pipecat.frames.frames import (
                                LLMFullResponseStartFrame,
                                LLMFullResponseEndFrame,
                                LLMResponseStartFrame,
                                LLMResponseEndFrame,
                                EndFrame,
                                TextFrame,
                                BotSpeakingFrame
                                )
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContextFrame
from elevenlabs.client import ElevenLabs
from elevenlabs import play

class TalkingMachine():
    def __init__(self):
        self.client = ElevenLabs(
            api_key=  os.getenv("ELEVENLABS_API_KEY")
        )

    def talk(self, msg):
        audio = self.client.generate(
            text=msg,
            voice="Rachel",
            model="eleven_multilingual_v2"
        )
        play(audio)
 

class ContextLogger(FrameProcessor):

    # TODO: Implement the ContextLogger class
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_message = ""
        self.all_messages = None
        self.session_ended = False
        self.talker = TalkingMachine()

    def did_session_end(self):
        return self.session_ended
    
    async def process_frame(self, frame, direction):
        if isinstance(frame, LLMFullResponseStartFrame):
            self.current_message = ""
        elif isinstance(frame, OpenAILLMContextFrame):
            self.current_message += frame.context.get_messages()[-1]['content'][1:]
            self.all_messages = frame.context.get_messages()
        elif isinstance(frame, LLMFullResponseEndFrame):
            await self.communicate_to_user(self.current_message)
            self.print_not_assistant_or_user(self.all_messages)
        elif isinstance(frame, EndFrame):
            self.make_session_end()
        elif isinstance(frame, LLMResponseStartFrame) or isinstance(frame, LLMResponseEndFrame) or \
            isinstance(frame, TextFrame) or isinstance(frame, BotSpeakingFrame):
            pass
        else:
            from loguru import logger
            logger.warning("Warning: type of context is " + str(type(frame)))
        await super().process_frame(frame, direction)

    async def communicate_to_user(self, msg):
        print(msg)
        self.talker.talk(msg)
    def make_session_end(self):
        self.session_ended = True

    def print_not_assistant_or_user(self, messages):
        for message in messages:
            if message['role'] not in ["assistant", "user"]:
                from loguru import logger
                logger.info(message)
    