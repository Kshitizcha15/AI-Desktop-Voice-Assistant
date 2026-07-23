"""Desktop frontend for Friday."""

import threading
import tkinter as tk
from tkinter import messagebox

from core.router import process_command, run_assistant


class FridayApp:
    BACKGROUND = "#0b1020"
    PANEL = "#151d33"
    TEXT = "#eaf1ff"
    MUTED = "#9dabca"
    ACCENT = "#64d7ff"
    SUCCESS = "#42d39b"

    def __init__(self, root):
        self.root = root
        self.root.title("Friday")
        self.root.geometry("760x650")
        self.root.minsize(620, 520)
        self.root.configure(bg=self.BACKGROUND)
        self.stop_event = None
        self.voice_worker = None
        self.status = tk.StringVar(value="Ready — type a message or start voice mode")

        self._build_header()
        self._build_conversation()
        self._build_composer()
        self._build_footer()
        self.add_message("Friday", "Hello. I am Friday. How can I help you?")
        root.protocol("WM_DELETE_WINDOW", self.close)

    def _build_header(self):
        header = tk.Frame(self.root, bg=self.BACKGROUND)
        header.pack(fill="x", padx=30, pady=(25, 14))
        tk.Label(header, text="FRIDAY", font=("Helvetica", 26, "bold"), fg=self.ACCENT,
                 bg=self.BACKGROUND).pack(side="left")
        tk.Label(header, text="● ONLINE", font=("Helvetica", 11, "bold"), fg=self.SUCCESS,
                 bg=self.BACKGROUND).pack(side="right", pady=10)

    def _build_conversation(self):
        panel = tk.Frame(self.root, bg=self.PANEL, highlightthickness=1, highlightbackground="#263354")
        panel.pack(fill="both", expand=True, padx=30, pady=(0, 14))
        self.chat = tk.Text(
            panel, bg=self.PANEL, fg=self.TEXT, relief="flat", borderwidth=0,
            font=("Helvetica", 14), wrap="word", padx=18, pady=16,
            state="disabled", cursor="arrow",
        )
        scroll = tk.Scrollbar(panel, command=self.chat.yview)
        self.chat.configure(yscrollcommand=scroll.set)
        self.chat.tag_configure("Friday", foreground=self.ACCENT, font=("Helvetica", 13, "bold"))
        self.chat.tag_configure("You", foreground=self.SUCCESS, font=("Helvetica", 13, "bold"))
        self.chat.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

    def _build_composer(self):
        composer = tk.Frame(self.root, bg=self.BACKGROUND)
        composer.pack(fill="x", padx=30, pady=(0, 12))
        self.input = tk.Entry(
            composer, bg="#1b2742", fg=self.TEXT, insertbackground=self.TEXT,
            relief="flat", font=("Helvetica", 14),
        )
        self.input.pack(side="left", fill="x", expand=True, ipady=12, padx=(0, 10))
        self.input.bind("<Return>", self.send_message)
        tk.Button(
            composer, text="Send", command=self.send_message, bg=self.ACCENT, fg="#07111f",
            font=("Helvetica", 12, "bold"), relief="flat", padx=20, pady=10,
        ).pack(side="right")

    def _build_footer(self):
        footer = tk.Frame(self.root, bg=self.BACKGROUND)
        footer.pack(fill="x", padx=30, pady=(0, 22))
        tk.Label(footer, textvariable=self.status, bg=self.BACKGROUND, fg=self.MUTED,
                 font=("Helvetica", 11)).pack(side="left")
        self.start_button = tk.Button(
            footer, text="Start voice mode", command=self.start_voice, bg=self.SUCCESS,
            fg="#071a13", font=("Helvetica", 11, "bold"), relief="flat", padx=14, pady=7,
        )
        self.start_button.pack(side="right")
        self.stop_button = tk.Button(
            footer, text="Stop", command=self.stop_voice, state="disabled", bg="#f17474",
            fg="#280707", font=("Helvetica", 11, "bold"), relief="flat", padx=14, pady=7,
        )
        self.stop_button.pack(side="right", padx=(0, 8))

    def set_status(self, message):
        self.root.after(0, self.status.set, message)

    def add_message(self, speaker, message):
        def append():
            self.chat.configure(state="normal")
            self.chat.insert("end", f"{speaker}\n", speaker)
            self.chat.insert("end", f"{message}\n\n")
            self.chat.configure(state="disabled")
            self.chat.see("end")
        self.root.after(0, append)

    def send_message(self, event=None):
        message = self.input.get().strip()
        if not message:
            return
        self.input.delete(0, "end")
        self.set_status("Friday is thinking…")
        threading.Thread(target=self._send_in_background, args=(message,), daemon=True).start()

    def _send_in_background(self, message):
        try:
            process_command(message, self.set_status, self.add_message)
            self.set_status("Ready")
        except Exception as error:
            self.root.after(0, lambda: messagebox.showerror("Friday error", str(error)))
            self.set_status("Could not complete that request")

    def start_voice(self):
        if self.voice_worker and self.voice_worker.is_alive():
            return
        self.stop_event = threading.Event()
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.set_status("Starting voice mode…")
        self.voice_worker = threading.Thread(target=self._run_voice, daemon=True)
        self.voice_worker.start()

    def _run_voice(self):
        try:
            run_assistant(self.stop_event, self.set_status, self.add_message)
        except Exception as error:
            self.root.after(0, lambda: messagebox.showerror("Friday could not start", str(error)))
        finally:
            self.root.after(0, self._voice_stopped)

    def _voice_stopped(self):
        self.status.set("Voice mode is stopped")
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")

    def stop_voice(self):
        if self.stop_event:
            self.stop_event.set()
        self.set_status("Stopping voice mode…")

    def close(self):
        self.stop_voice()
        self.root.destroy()


if __name__ == "__main__":
    window = tk.Tk()
    FridayApp(window)
    window.mainloop()
