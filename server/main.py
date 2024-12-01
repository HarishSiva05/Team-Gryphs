from commit_activity.activity import CommitsActivity
from kestra import Kestra
import asyncio

class Orchestrator:
    def __init__(self):
        self.commits_activity_obj = CommitsActivity()
        self.kestra = Kestra()

    async def chat(self):
        print("Chatbot is ready. Type 'exit' to end the conversation.")
        while True:
            user_input = await asyncio.get_event_loop().run_in_executor(None, input, "You: ")
            if user_input.lower() == 'exit':
                print("Ending the conversation.")
                break
            response = await self.process_input(user_input)
            print(f"Bot: {response}")

    async def process_input(self, user_input):
        # Check if the input is related to running a Kestra workflow
        if "run workflow" in user_input.lower():
            return await self.run_kestra_workflow()
        else:
            return self.commits_activity_obj.get_answer(user_input)

    async def run_kestra_workflow(self):
        try:
            # Assuming you have a workflow defined in Kestra
            execution = kestra.run(GitHubLLMWorkflow.workflow())
            return f"Kestra workflow started. Execution ID: {execution.id}"
        except Exception as e:
            return f"Error running Kestra workflow: {str(e)}"

async def main():
    kestra = Kestra()
    await kestra.start_async()
    
    orchestrator = Orchestrator()
    await orchestrator.chat()

if __name__ == '__main__':
    asyncio.run(main())