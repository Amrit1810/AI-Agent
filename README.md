# Browser AI Agent GUI

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Description

This project implements a browser-operating AI agent system designed to automate web-based tasks through natural language commands. It features a ChatGPT-like operator agent that receives user instructions via a custom GUI and executes them directly within a web browser using the `browser-use` automation library. The AI agent, powered by LangChain and OpenAI's GPT models (specifically configured for GPT-4o), handles tasks such as navigating web pages, retrieving information, and interacting with web elements autonomously, eliminating the need for manual browsing.

The solution integrates a custom GUI built with Tkinter and the CustomTkinter library, providing a user-friendly interface for real-time chat interactions, displaying detailed agent execution logs ("thoughts"), and presenting the final task output. The backend logic manages the connection between the GUI, the AI agent, browser control, asynchronous task execution, logging, and result delivery.

## Features

*   **Natural Language Control:** Interact with the agent using plain English commands.
*   **Browser Automation:** Leverages the `browser-use` library to control a Chrome browser instance.
*   **OpenAI Integration:** Utilizes LangChain and OpenAI (GPT-4o) for intelligent task interpretation and execution planning.
*   **Real-time GUI:** CustomTkinter-based interface with three distinct panes:
    *   **Agent Logs:** Displays the step-by-step actions and thoughts of the agent.
    *   **Chat Interface:** Allows users to input commands and see conversational responses.
    *   **Final Output:** Shows the final result or summary produced by the agent.
*   **Asynchronous Task Handling:** Executes browser tasks in the background without freezing the GUI.
*   **Detailed Logging:** Captures logs from the agent and browser components for debugging and transparency.
*   **Simple Password Protection:** Basic password prompt on startup (currently hardcoded).
*   **Cross-Platform Compatibility:** Runs on systems where Python, Chrome, and the required libraries are installed (Windows path currently hardcoded, requires adjustment for other OS).

## Architecture Overview

1.  **User Input:** The user types a command into the Chat Interface within the GUI (`agent_gui.py`).
2.  **Task Dispatch:** The GUI sends the command to the Agent Logic (`agent_logic.py`).
3.  **Agent Initialization:** An `Agent` instance from `browser-use` is created, configured with the task, an LLM (OpenAI GPT-4o via LangChain), a `Browser` instance, and a `Controller`.
4.  **Task Execution:** The `Agent` runs asynchronously:
    *   It interprets the command using the LLM.
    *   It plans and executes actions (e.g., navigate, click, type, scrape) using the `Controller` and `Browser`.
    *   Logs detailing actions and internal states are generated.
5.  **Logging:** A custom `QueueHandler` directs logs from `agent_logic.py` and `browser-use` components to a queue monitored by the GUI.
6.  **GUI Updates:**
    *   The GUI periodically polls the log queue and displays messages in the "Agent Logs" pane.
    *   Once the agent finishes, the final result is displayed in the "Final Output" pane.
    *   A summary response is added to the "Chat Interface".
7.  **Browser Control:** The `browser-use` library handles the low-level interaction with the Chrome browser process.

## Prerequisites

*   **Python:** Version 3.8 or higher recommended.
*   **Google Chrome:** A standard installation of the Google Chrome browser is required.
*   **pip:** Python package installer (usually comes with Python).
*   **Virtual Environment Tool:** `venv` (recommended, usually comes with Python).

## Setup Instructions

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/Amrit1810/AI-Agent.git
    cd your-repository-name
    ```

2.  **Create and Activate a Virtual Environment (Recommended):**
    *   **Windows:**
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```
    *   **macOS/Linux:**
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```

3.  **Install Dependencies:**
    Create a file named `requirements.txt` in the project's root directory with the following content:

    ```txt
    # Core Libraries
    langchain-openai>=0.1.0,<0.2.0
    browser-use>=0.1.0,<0.2.0
    customtkinter>=5.0.0,<6.0.0
    python-dotenv>=1.0.0,<2.0.0
    pydantic>=2.0.0,<3.0.0

    # Dependencies often pulled in by the above, listed for clarity
    # langchain>=0.1.0,<0.2.0
    # langchain-core>=0.1.0,<0.2.0
    # openai>=1.0.0,<2.0.0
    # tkinter (usually built-in with Python)
    # asyncio (built-in)
    # logging (built-in)
    # queue (built-in)
    # threading (built-in)
    # traceback (built-in)
    # os (built-in)
    ```
    *(Note: Check PyPI for the exact package name and latest stable version for `browser-use` if the current one causes issues. Adjust version specifiers as needed.)*

    Then, install the packages:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure OpenAI API Key:**
    *   Create a file named `.env` in the project's root directory (alongside `agent_logic.py` and `agent_gui.py`).
    *   Add your OpenAI API key to this file:
        ```dotenv
        OPENAI_API_KEY="your_openai_api_key_here"
        ```
    *   Replace `"your_openai_api_key_here"` with your actual secret key from OpenAI.

5.  **Configure Chrome Path:**
    *   Open the `agent_logic.py` file.
    *   Locate the `BrowserConfig` initialization within the `SimpleAgentRunner` class:
        ```python
        self.browser_config = BrowserConfig(
            chrome_instance_path="C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        )
        ```
    *   **IMPORTANT:** Modify the `chrome_instance_path` string to point to the *correct* location of your `chrome.exe` (or the equivalent executable on macOS/Linux) on your specific system.
        *   **macOS Example:** `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`
        *   **Linux Example:** `/usr/bin/google-chrome` (or similar, may vary by distribution)

## Running the Application

1.  Ensure your virtual environment is activated (Step 2 in Setup).
2.  Make sure you have configured your `.env` file (Step 4) and the Chrome path in `agent_logic.py` (Step 5).
3.  Run the GUI script from the project's root directory:
    ```bash
    python agent_gui.py
    ```
4.  A password prompt will appear. Enter the password (`test` by default) and click "OK".

## Using the Application

1.  **Password:** Enter the hardcoded password (`test`) when prompted upon startup.
2.  **Interface:**
    *   **Agent Logs (Left Pane):** Shows real-time logs from the agent and browser automation library as it works through your command. This includes steps like navigation, searching for elements, and potential errors.
    *   **Chat Interface (Middle Pane):**
        *   The top text box displays the conversation history (your commands and the AI's chat responses).
        *   The bottom entry field is where you type your commands for the agent (e.g., "Go to wikipedia.org and search for 'Large Language Models'").
        *   Press `Enter` or click the "Send" button to submit your command.
    *   **Final Output (Right Pane):** Displays the final result extracted or generated by the agent after completing the task (e.g., scraped text, a summary, or confirmation of action).
3.  **Interaction Flow:**
    *   Type your desired task into the message entry box and press Send.
    *   The input fields will disable while the agent is working.
    *   Watch the "Agent Logs" pane for updates on the agent's progress.
    *   Once finished, the agent's chat response will appear in the chat history, the final result will populate the "Final Output" pane, and the input fields will re-enable for your next command.

## Troubleshooting / Notes

*   **Chrome Path Error:** If the application fails to start the browser, double-check the `chrome_instance_path` in `agent_logic.py` and ensure it exactly matches your Chrome installation location. Check file permissions if necessary.
*   **OpenAI API Key Error:** Ensure the `.env` file exists in the correct directory, is named exactly `.env`, and contains a valid `OPENAI_API_KEY`. Check your OpenAI account for API usage limits or billing issues.
*   **`browser-use` Errors:** Ensure Chrome is not already running with a remote debugging port open that conflicts with the library (usually port 9222). Close other Chrome instances or try specifying a different debugging port in `BrowserConfig` if the library supports it. Consult the `browser-use` library's documentation if specific browser control errors occur.
*   **Dependencies:** Always use a virtual environment (`venv`) to avoid conflicts between project dependencies and system-wide Python packages. If you encounter module not found errors, ensure the venv is active and run `pip install -r requirements.txt` again.
*   **Password:** The password "test" is hardcoded in `agent_gui.py`. For any real-world or shared use, implement a more secure authentication method (e.g., environment variables, config files outside the repo, a proper login system).
*   **Resource Usage:** Running a browser and an LLM can be resource-intensive (CPU, RAM). Performance may vary depending on your system and the complexity of the task.

## References

*   **LangChain:** [https://python.langchain.com/](https://python.langchain.com/) - Framework for developing applications powered by language models.
*   **OpenAI:** [https://openai.com/](https://openai.com/) | [API Documentation](https://platform.openai.com/docs) - Provider of the GPT models used.
*   **browser-use:** [https://github.com/browser-use/browser-use](https://github.com/browser-use/browser-use) - The browser automation library.
*   **CustomTkinter:** [https://github.com/TomSchimansky/CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - Python UI library based on Tkinter.
*   **Python:** [https://www.python.org/](https://www.python.org/)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request or open an Issue if you find bugs or have suggestions for improvements.
