import os
import asyncio
import traceback
import logging
import io
import queue
from pydantic import BaseModel, SecretStr
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from browser_use import Agent, Browser, BrowserConfig, Controller

load_dotenv()

# --- Custom Log Handler ---
class QueueHandler(logging.Handler):
    """Sends log records to a queue."""
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue
        # Define formatter within the handler
        self.setFormatter(logging.Formatter('%(levelname)-8s [%(name)s] %(message)s'))
        # Ensure handler processes INFO level messages
        self.setLevel(logging.INFO)

    def emit(self, record):
        self.log_queue.put(self.format(record))

# --- Logger names used by browser_use (based on console output) ---
LOGGER_NAMES = ['agent', 'controller', 'browser', 'browser_use'] # Add 'browser_use' based on initial setup message

class SimpleAgentRunner:

    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.0,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.browser_config = BrowserConfig(
            chrome_instance_path="C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        )
        # Ensure the loggers exist and set level - do this once
        for name in LOGGER_NAMES:
            logging.getLogger(name).setLevel(logging.INFO)
        # Set root level minimally to allow INFO from library to pass through if needed
        logging.getLogger().setLevel(logging.INFO)


    async def _execute_async(self, user_command: str, log_queue: queue.Queue) -> dict:
        log_handler = QueueHandler(log_queue)
        loggers_with_handler = [] # Keep track of which loggers we added the handler to

        browser = None
        final_output = "Task initiated."
        chat_response = "Processing..."

        try:
            # Initial status message
            log_queue.put("INFO     [system] Agent process starting...")

            # Initialize browser_use components
            browser = Browser(config=self.browser_config)
            controller = Controller()
            agent = Agent(
                task=user_command,
                llm=self.llm,
                browser=browser,
                controller=controller,
            )

            # --- Add QueueHandler just before running ---
            log_queue.put("INFO     [system] Attaching log handler...")
            for name in LOGGER_NAMES:
                logger = logging.getLogger(name)
                # Check if handler already exists (prevent duplicates if run multiple times)
                if log_handler not in logger.handlers:
                    logger.addHandler(log_handler)
                    loggers_with_handler.append(logger) # Remember we added it
                    logger.setLevel(logging.INFO) # Ensure level again just in case

            # --- Run the agent ---
            result = await agent.run()
            final_output = result.final_result()
            chat_response = "Task completed."
            log_queue.put("--- AGENT TASK FINISHED ---")

        except Exception as e:
            print(f"Error during agent execution: {e}\n{traceback.format_exc()}")
            error_msg = f"An error occurred: {type(e).__name__}"
            error_log_msg = f"ERROR    [system] Agent execution failed: {error_msg}: {e}"
            log_queue.put(error_log_msg)
            final_output = f"Agent failed.\n{error_msg}: {e}"
            chat_response = "Sorry, I encountered an error."
            log_queue.put("--- AGENT TASK FAILED ---")

        finally:
            # --- Remove QueueHandler ---
            log_queue.put("INFO     [system] Detaching log handler...")
            for logger in loggers_with_handler:
                 logger.removeHandler(log_handler)

            # --- Cleanup Browser ---
            if browser:
                try:
                    await browser.close()
                    log_queue.put("INFO     [system] Browser closed.")
                except Exception as close_e:
                    print(f"Error closing browser: {close_e}")
                    log_queue.put(f"WARNING  [system] Failed to close browser: {close_e}")

        return {
            "chat_response": chat_response,
            "final_output": str(final_output),
        }

    def run_task(self, user_command: str, log_queue: queue.Queue) -> dict:
        try:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self._execute_async(user_command, log_queue))
            return result
        except Exception as e:
             print(f"Error running async task: {e}\n{traceback.format_exc()}")
             error_log_msg = f"FATAL ERROR before/during async execution:\n{type(e).__name__}: {e}\n{traceback.format_exc()}"
             try:
                 log_queue.put(error_log_msg)
                 log_queue.put("--- AGENT TASK FAILED (CRITICAL) ---")
             except:
                 pass

             return {
                 "chat_response": "A critical execution error occurred.",
                 "final_output": f"Failed.\n{e}",
             }

agent_runner_instance = SimpleAgentRunner()

# Keep the __main__ block for standalone testing if desired
if __name__ == '__main__':
    print("Testing simplified agent_logic.py (Targeted Handler Logging)...")
    print("NOTE: Real-time logs require a queue consumer (like the GUI).")
    test_queue = queue.Queue()
    runner = SimpleAgentRunner()
    test_task = "Go to google.com and get the page title"
    print(f"Running test task: {test_task}")

    import threading, time
    def consume_queue_test():
        print("\n--- Captured Logs (Targeted) ---")
        finished = False
        while not finished:
             try:
                 # Use timeout to prevent hanging if queue is empty near the end
                 msg = test_queue.get(timeout=1.0)
                 print(msg)
                 # Check for final messages
                 if "--- AGENT TASK" in msg:
                     finished = True # Allow loop to potentially get Browser closed msg
                 if "Browser closed" in msg and finished:
                      break # Exit after browser closed if task was already finished/failed
             except queue.Empty:
                 print("--- Queue empty, assuming finished ---")
                 break # Stop if queue is empty
             except Exception as e:
                 print(f"Queue consumer error: {e}")
                 break
        print("------------------------------------")


    consumer_thread = threading.Thread(target=consume_queue_test, daemon=True)
    consumer_thread.start()

    result_dict = runner.run_task(test_task, test_queue)

    consumer_thread.join(timeout=3.0) # Wait a bit longer for consumer thread

    print("\n--- Chat Response ---")
    print(result_dict.get('chat_response', 'N/A'))
    print("\n--- Final Output ---")
    print(result_dict.get('final_output', 'N/A'))
    print("\nTest finished.")