"""
 ContextLogger is a FrameProcessor which should print in the console the
 conversation context after each message. Additionally, it could also save
 the conversation transcript to a file. Feel free to get creative here.
"""

from pipecat.processors.frame_processor import FrameProcessor
from pipecat.frames.frames import LLMFullResponseStartFrame, LLMFullResponseEndFrame
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContextFrame
class ContextLogger(FrameProcessor):

    # TODO: Implement the ContextLogger class
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_message = ""
        self.all_messages = None
    
    async def process_frame(self, frame, direction):
        if isinstance(frame, LLMFullResponseStartFrame):
            self.current_message = ""
        elif isinstance(frame, OpenAILLMContextFrame):
            self.current_message += frame.context.get_messages()[-1]['content'][1:]
            self.all_messages = frame.context.get_messages()
        elif isinstance(frame, LLMFullResponseEndFrame):
            print(self.current_message)
            self.print_not_assistant_or_user(self.all_messages)
        else:
            print("Warning: type of context is " + type(frame))
        await super().process_frame(frame, direction)
    def print_not_assistant_or_user(self, messages):
        for message in messages:
            if message['role'] not in ["assistant", "user"]:
                print(message)
    