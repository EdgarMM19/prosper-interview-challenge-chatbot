"""
 ChatbotTester enables to simulate a conversation with the chatbot through
 text channel in the console. The user can type a message and the chatbot
 will respond with a message.
"""
import os

from pipecat.pipeline.pipeline import Pipeline
from pipecat.processors.aggregators.llm_response import (
    LLMUserContextAggregator,
    LLMAssistantContextAggregator
)
from pipecat.processors.frame_processor import FrameDirection
from pipecat.services.openai import (
    OpenAILLMContext,
    OpenAILLMContextFrame,
    OpenAILLMService,
)
from pipecat.transports.base_transport import TransportParams
from pipecat.transports.local.audio import LocalAudioTransport

from context_logger import ContextLogger
from intake_processor import IntakeProcessor


class Chatbot:

    def __init__(self):
        self._context = OpenAILLMContext(messages=[])

    async def init_session(self):
        """Initialize the session with the pipeline."""

        self._context = OpenAILLMContext(messages=[])

        # 1. User context aggregators
        user_context = LLMUserContextAggregator(self._context)

        # 2. LLM service + States processor
        llm = OpenAILLMService(
            api_key=os.getenv("OPENAI_API_KEY"),
            model="gpt-4o",
        )
        # TODO: change this IntakeProcessor for your own states processor
        # Adds function calling and states to LLM to fit it to the task
        _ = IntakeProcessor(
            context=self._context,
            llm=llm
        )
        # 3. Assistant context aggregators
        assistant_context = LLMAssistantContextAggregator(self._context)

        # 4. Context logger
        self.context_logger = ContextLogger()


        # Pipeline creation
        self._pipeline = Pipeline([
            user_context,
            llm, 
            assistant_context, 
            self.context_logger,
        ])


    async def run_message(self, message_text: str):
        """Run a message through the pipeline and print the context."""
        self._context.add_message({
            "role": "user",
            "content": message_text,
        })
        await self._pipeline.process_frame(
            frame=OpenAILLMContextFrame(self._context),
            direction=FrameDirection.DOWNSTREAM
        )

    async def simulate_conversation(self) -> None:
        """Run a conversation with the chatbot."""
        await self.init_session()
        await self.run_message("YOU: ")
        while True:
            message = input("YOU: ")
            if message == "exit":
                break
            await self.run_message(message)
            if self.context_logger.did_session_end():
                break


if __name__ == '__main__':
    import asyncio
    from loguru import logger
    logger.remove()
    if os.path.exists("logfile.log"):
        os.remove("logfile.log")
    logger.add("logfile.log", level="INFO")
    tester = Chatbot()
    asyncio.run(tester.simulate_conversation())
