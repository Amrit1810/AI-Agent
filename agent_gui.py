import customtkinter
import tkinter as tk
from tkinter import messagebox
import threading
import queue
import agent_logic
import traceback

class AgentApp(customtkinter.CTk):
    PASSWORD = "test"

    def __init__(self):
        super().__init__()
        self.title("AI Agent Interface")
        self.geometry("1200x700")
        customtkinter.set_appearance_mode("System")
        customtkinter.set_default_color_theme("blue")
        self.agent_running = False
        self.log_queue = queue.Queue()
        self.queue_polling_id = None
        self.check_password()

    def check_password(self):
        dialog = customtkinter.CTkInputDialog(
            text="Enter Password:",
            title="Password Required"
        )
        entered_password = dialog.get_input()
        if entered_password == self.PASSWORD:
            self.create_widgets()
        elif entered_password is None:
             print("Login cancelled.")
             self.destroy()
        else:
            messagebox.showerror("Error", "Incorrect Password")
            self.destroy()


    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Choosing Font Size ---
        main_font_size = 13 # Adjust this value as needed
        mono_font_family = "Consolas" # Or "Courier New", etc.
        chat_font_family = "Segoe UI" # Or "Arial", "Calibri", etc.

        # --- Thinking/Logs Pane ---
        self.thinking_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.thinking_frame.grid(row=0, column=0, sticky="nsew")
        self.thinking_frame.grid_rowconfigure(1, weight=1)
        self.thinking_frame.grid_columnconfigure(0, weight=1)
        self.thinking_label = customtkinter.CTkLabel(
            self.thinking_frame, text="Agent Logs",
            font=customtkinter.CTkFont(size=16, weight="bold") # Keep heading size maybe
        )
        self.thinking_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        self.thinking_textbox = customtkinter.CTkTextbox(
            self.thinking_frame,
            wrap=tk.WORD,
            state="disabled",
            # --- UPDATED FONT ---
            font=(mono_font_family, main_font_size)
        )
        self.thinking_textbox.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self._update_textbox(self.thinking_textbox, "AI Agent ready. Waiting for command.")

        # --- Chat Pane ---
        self.chat_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.chat_frame.grid(row=0, column=1, sticky="nsew", padx=(2, 2))
        self.chat_frame.grid_rowconfigure(1, weight=1)
        self.chat_frame.grid_rowconfigure(2, weight=0)
        self.chat_frame.grid_columnconfigure(0, weight=1)
        self.chat_label = customtkinter.CTkLabel(
            self.chat_frame, text="Chat Interface",
            font=customtkinter.CTkFont(size=16, weight="bold") # Keep heading size maybe
        )
        self.chat_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        self.chat_history_textbox = customtkinter.CTkTextbox(
             self.chat_frame,
             wrap=tk.WORD,
             state="disabled",
             # --- ADDED/UPDATED FONT ---
             font=(chat_font_family, main_font_size)
        )
        self.chat_history_textbox.grid(row=1, column=0, padx=10, pady=0, sticky="nsew")
        self.input_frame = customtkinter.CTkFrame(self.chat_frame, fg_color="transparent")
        self.input_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)
        self.message_entry = customtkinter.CTkEntry(
             self.input_frame,
             placeholder_text="Enter your command for the AI Agent...",
             # --- ADDED/UPDATED FONT ---
             font=(chat_font_family, main_font_size)
        )
        self.message_entry.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        self.message_entry.bind("<Return>", self.send_message_event)
        self.send_button = customtkinter.CTkButton(
            self.input_frame, text="Send", width=80, command=self.send_message_event
            # Optionally increase button font size too if desired
            # font=(chat_font_family, main_font_size)
        )
        self.send_button.grid(row=0, column=1, sticky="e")

        # --- Output Pane ---
        self.output_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.output_frame.grid(row=0, column=2, sticky="nsew")
        self.output_frame.grid_rowconfigure(1, weight=1)
        self.output_frame.grid_columnconfigure(0, weight=1)
        self.output_label = customtkinter.CTkLabel(
            self.output_frame, text="Final Output / Result",
            font=customtkinter.CTkFont(size=16, weight="bold") # Keep heading size maybe
        )
        self.output_label.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="w")
        self.output_textbox = customtkinter.CTkTextbox(
            self.output_frame,
            wrap=tk.WORD,
            state="disabled",
            # --- UPDATED FONT ---
            font=(mono_font_family, main_font_size)
        )
        self.output_textbox.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self._update_textbox(self.output_textbox, "No task performed yet.")

    def _update_textbox(self, textbox: customtkinter.CTkTextbox, text: str, append=False):
        try:
            textbox.configure(state="normal")
            text_str = str(text) # Ensure string
            if append:
                # Check if textbox currently ends with a newline
                current_content = textbox.get("1.0", "end-1c")
                if current_content and not current_content.endswith('\n'):
                     textbox.insert(tk.END, "\n" + text_str)
                else:
                     textbox.insert(tk.END, text_str)

            else:
                textbox.delete("1.0", tk.END)
                textbox.insert("1.0", text_str)
            textbox.configure(state="disabled")
            textbox.see(tk.END) # Scroll to show the latest appended text
        except Exception as e:
            print(f"Error updating textbox: {e}")
            try:
                 textbox.configure(state="disabled")
            except:
                 pass

    def _append_chat_history(self, text: str):
         self.chat_history_textbox.configure(state="normal")
         self.chat_history_textbox.insert(tk.END, str(text) + "\n\n")
         self.chat_history_textbox.configure(state="disabled")
         self.chat_history_textbox.see(tk.END)

    def send_message_event(self, event=None):
        if self.agent_running:
            messagebox.showwarning("Busy", "Agent is currently processing a command. Please wait.")
            return

        user_message = self.message_entry.get().strip()
        if not user_message:
            return

        self.message_entry.delete(0, tk.END)
        self._append_chat_history(f"You: {user_message}")

        # Clear previous logs and output before starting
        self._update_textbox(self.thinking_textbox, "") # Clear logs completely
        self._update_textbox(self.output_textbox, "Processing...")

        self.message_entry.configure(state="disabled")
        self.send_button.configure(state="disabled")
        self.agent_running = True

        # Ensure the queue is empty before starting a new task
        while not self.log_queue.empty():
            try:
                self.log_queue.get_nowait()
            except queue.Empty:
                break

        # Start the agent thread, passing the queue
        thread = threading.Thread(
            target=self._run_agent_thread,
            args=(user_message, self.log_queue), # Pass queue here
            daemon=True
        )
        thread.start()

        # Start polling the log queue
        self.process_log_queue()


    def process_log_queue(self):
        """Periodically check the log queue and update the thinking textbox."""
        try:
            messages_processed = 0
            while messages_processed < 10: # Process up to 10 messages per cycle to prevent blocking GUI
                log_entry = self.log_queue.get_nowait()
                # Use append=True for subsequent messages
                is_first_message = self.thinking_textbox.get("1.0", "end-1c") == ""
                self._update_textbox(self.thinking_textbox, log_entry, append=not is_first_message)
                messages_processed += 1

        except queue.Empty:
            pass # No messages currently in queue
        except Exception as e:
            print(f"Error processing log queue: {e}")
            # Optionally log this error to the textbox itself
            self._update_textbox(self.thinking_textbox, f"\n--- GUI Error processing logs: {e} ---", append=True)

        # Reschedule polling only if the agent is still running
        if self.agent_running:
            self.queue_polling_id = self.after(100, self.process_log_queue) # Poll every 100ms


    def _run_agent_thread(self, user_message, log_queue):
        """Runs the agent task in a separate thread."""
        try:
            results = agent_logic.agent_runner_instance.run_task(user_message, log_queue)
            self.after(0, self._update_ui_from_agent, results) # Schedule UI update on main thread
        except Exception as e:
            print(f"Error directly in worker thread execution: {e}\n{traceback.format_exc()}")
            error_message = f"Critical error in agent thread: {e}"
            results_on_error = {
                 "chat_response": "System error in worker thread.",
                 "final_output": f"Failed: {e}"
            }
            # Try to log the error via queue
            try:
                log_queue.put(f"FATAL    [GUI Thread] {error_message}\n{traceback.format_exc()}")
                log_queue.put("--- AGENT TASK FAILED (THREAD CRASH) ---")
            except:
                pass
            # Still schedule UI update
            self.after(0, self._update_ui_from_agent, results_on_error)


    def _update_ui_from_agent(self, results: dict):
        """Called when the agent task function returns (on main thread)."""
        # Stop polling the queue FIRST
        self.agent_running = False
        if self.queue_polling_id:
            self.after_cancel(self.queue_polling_id)
            self.queue_polling_id = None

        # Process any final messages that might have arrived just before stopping
        self.process_log_queue()

        # Update chat and output panes
        chat = results.get("chat_response", "Agent did not provide a chat response.")
        output = results.get("final_output", "No final output received.")

        self._append_chat_history(f"AI: {chat}")
        self._update_textbox(self.output_textbox, output)

        self._enable_input() # Re-enable input fields AFTER everything is done


    def _enable_input(self):
         """Re-enables input fields and ensures polling is stopped."""
         if self.queue_polling_id:
             try:
                 self.after_cancel(self.queue_polling_id)
             except ValueError: # May happen if ID is invalid (already cancelled)
                 pass
             self.queue_polling_id = None
         self.agent_running = False # Ensure state is correct

         # Ensure widgets exist before configuring (safety check)
         if hasattr(self, 'message_entry') and self.message_entry.winfo_exists():
             self.message_entry.configure(state="normal")
             self.message_entry.focus()
         if hasattr(self, 'send_button') and self.send_button.winfo_exists():
             self.send_button.configure(state="normal")


    def destroy(self):
        """Override destroy to ensure polling stops."""
        print("Closing application, stopping queue polling.")
        self.agent_running = False # Prevent rescheduling
        if self.queue_polling_id:
            try:
                self.after_cancel(self.queue_polling_id)
            except ValueError:
                pass
            self.queue_polling_id = None
        super().destroy()


if __name__ == "__main__":
    app = AgentApp()
    app.mainloop()