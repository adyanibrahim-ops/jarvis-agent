
import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog
import threading
import json
import os
from datetime import datetime

import pystray
from PIL import Image, ImageDraw

from .agent import ask_jarvis
from .memory import (
    init_memory,
    save_memory,
    get_memories,
    delete_memory
)
from .tools import (
    calculate,
    get_system_info,
    list_files
)


# =========================================================
# INITIALIZE
# =========================================================

init_memory()

HISTORY_FILE = "jarvis_conversations.json"


# =========================================================
# CONVERSATION STORAGE
# =========================================================

def load_conversations():

    if not os.path.exists(HISTORY_FILE):
        return []

    try:

        with open(
            HISTORY_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            return json.load(file)

    except Exception:

        return []


def save_conversations(conversations):

    try:

        with open(
            HISTORY_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                conversations,
                file,
                indent=2,
                ensure_ascii=False
            )

    except Exception:
        pass


# =========================================================
# JARVIS UI
# =========================================================

class JarvisUI(tk.Tk):

    def __init__(self):

        super().__init__()

        # -------------------------------------------------
        # WINDOW
        # -------------------------------------------------

        self.title("JARVIS")

        self.geometry(
            "1280x800"
        )

        self.minsize(
            950,
            620
        )

        self.configure(
            bg="#080c11"
        )

        # Prevent immediate destruction when X is pressed.
        self.protocol(
            "WM_DELETE_WINDOW",
            self.hide_to_tray
        )


        # -------------------------------------------------
        # COLORS
        # -------------------------------------------------

        self.bg = "#080c11"

        self.panel = "#10161e"

        self.panel2 = "#141c25"

        self.input_bg = "#18222d"

        self.border = "#263442"

        self.text = "#e8f1f8"

        self.secondary = "#8495a6"

        self.green = "#66e3a4"

        self.blue = "#79b8ff"

        self.yellow = "#f0c674"

        self.red = "#ff7070"


        # -------------------------------------------------
        # STATE
        # -------------------------------------------------

        self.conversations = load_conversations()

        self.current_conversation = None

        self.thinking = False

        self.thinking_step = 0

        self.tray_icon = None

        self.tray_thread = None

        self.is_exiting = False


        # -------------------------------------------------
        # BUILD
        # -------------------------------------------------

        self.create_header()

        self.create_main()

        self.create_shortcuts()


        # -------------------------------------------------
        # START CHAT
        # -------------------------------------------------

        if self.conversations:

            self.current_conversation = (
                self.conversations[-1]
            )

            self.load_current_conversation()

        else:

            self.new_chat(
                initial=True
            )


        self.after(
            200,
            self.focus_input
        )


        # -------------------------------------------------
        # START SYSTEM TRAY
        # -------------------------------------------------

        self.start_tray()


    # =====================================================
    # SYSTEM TRAY
    # =====================================================

    def create_tray_image(self):

        """
        Creates a simple JARVIS tray icon.
        No external .ico file is required.
        """

        image = Image.new(
            "RGBA",
            (64, 64),
            (8, 12, 17, 255)
        )

        draw = ImageDraw.Draw(image)

        # Outer circle
        draw.ellipse(
            (7, 7, 57, 57),
            outline=(102, 227, 164, 255),
            width=4
        )

        # Inner circle
        draw.ellipse(
            (23, 23, 41, 41),
            fill=(102, 227, 164, 255)
        )

        return image


    def start_tray(self):

        image = self.create_tray_image()

        menu = pystray.Menu(
            pystray.MenuItem(
                "Show JARVIS",
                self.tray_show
            ),
            pystray.MenuItem(
                "Hide JARVIS",
                self.tray_hide
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "Exit JARVIS",
                self.tray_exit
            )
        )

        self.tray_icon = pystray.Icon(
            "JARVIS",
            image,
            "JARVIS",
            menu
        )

        self.tray_thread = threading.Thread(
            target=self.tray_icon.run,
            daemon=True
        )

        self.tray_thread.start()


    def tray_show(self, icon=None, item=None):

        self.after(
            0,
            self.show_from_tray
        )


    def tray_hide(self, icon=None, item=None):

        self.after(
            0,
            self.hide_to_tray
        )


    def tray_exit(self, icon=None, item=None):

        self.after(
            0,
            self.exit_jarvis
        )


    def show_from_tray(self):

        self.deiconify()

        self.state("normal")

        self.lift()

        self.attributes(
            "-topmost",
            True
        )

        self.after(
            100,
            lambda: self.attributes(
                "-topmost",
                False
            )
        )

        self.focus_input()


    def hide_to_tray(self):

        if self.is_exiting:
            return

        self.withdraw()


    def exit_jarvis(self):

        if self.is_exiting:
            return

        self.is_exiting = True

        self.save_current()

        if self.tray_icon:

            try:
                self.tray_icon.stop()
            except Exception:
                pass

        self.destroy()


    # =====================================================
    # HEADER
    # =====================================================

    def create_header(self):

        header = tk.Frame(
            self,
            bg=self.panel,
            height=68
        )

        header.pack(
            side="top",
            fill="x"
        )

        header.pack_propagate(False)


        # LOGO

        tk.Label(
            header,
            text="◉",
            bg=self.panel,
            fg=self.green,
            font=("Segoe UI", 22)
        ).pack(
            side="left",
            padx=(22, 8)
        )


        tk.Label(
            header,
            text="JARVIS",
            bg=self.panel,
            fg=self.text,
            font=("Segoe UI", 22, "bold")
        ).pack(
            side="left"
        )


        tk.Label(
            header,
            text="  PERSONAL AI ASSISTANT",
            bg=self.panel,
            fg=self.secondary,
            font=("Segoe UI", 8, "bold")
        ).pack(
            side="left",
            pady=(7, 0)
        )


        # STATUS

        self.status = tk.Label(
            header,
            text="● ONLINE",
            bg=self.panel,
            fg=self.green,
            font=("Segoe UI", 10, "bold")
        )

        self.status.pack(
            side="right",
            padx=25
        )


    # =====================================================
    # MAIN
    # =====================================================

    def create_main(self):

        main = tk.Frame(
            self,
            bg=self.bg
        )

        main.pack(
            fill="both",
            expand=True
        )


        # -------------------------------------------------
        # SIDEBAR
        # -------------------------------------------------

        self.create_sidebar(main)


        # -------------------------------------------------
        # CONTENT
        # -------------------------------------------------

        self.content = tk.Frame(
            main,
            bg=self.bg
        )

        self.content.pack(
            side="left",
            fill="both",
            expand=True
        )


        self.content.grid_rowconfigure(
            0,
            weight=1
        )

        self.content.grid_rowconfigure(
            1,
            weight=0
        )

        self.content.grid_columnconfigure(
            0,
            weight=1
        )


        self.create_chat()

        self.create_input()


    # =====================================================
    # SIDEBAR
    # =====================================================

    def create_sidebar(
        self,
        parent
    ):

        self.sidebar = tk.Frame(
            parent,
            bg=self.panel,
            width=255
        )

        self.sidebar.pack(
            side="left",
            fill="y"
        )

        self.sidebar.pack_propagate(
            False
        )


        tk.Label(
            self.sidebar,
            text="WORKSPACE",
            bg=self.panel,
            fg=self.secondary,
            font=("Segoe UI", 8, "bold")
        ).pack(
            anchor="w",
            padx=18,
            pady=(18, 8)
        )


        self.sidebar_button(
            "＋   New Chat",
            self.new_chat
        )


        tk.Label(
            self.sidebar,
            text="CONVERSATIONS",
            bg=self.panel,
            fg=self.secondary,
            font=("Segoe UI", 8, "bold")
        ).pack(
            anchor="w",
            padx=18,
            pady=(18, 7)
        )


        history_container = tk.Frame(
            self.sidebar,
            bg=self.panel
        )

        history_container.pack(
            fill="both",
            expand=True,
            padx=8
        )


        self.history_list = tk.Listbox(
            history_container,

            bg=self.panel,

            fg=self.text,

            selectbackground="#263746",

            selectforeground="#ffffff",

            relief="flat",

            bd=0,

            highlightthickness=0,

            activestyle="none",

            font=("Segoe UI", 9),

            yscrollcommand=None
        )

        self.history_list.pack(
            fill="both",
            expand=True
        )

        self.history_list.bind(
            "<Double-Button-1>",
            self.rename_conversation
        )

        self.history_list.bind(
            "<ButtonRelease-1>",
            self.history_selected
        )


        bottom = tk.Frame(
            self.sidebar,
            bg=self.panel
        )

        bottom.pack(
            fill="x",
            pady=10
        )


        self.sidebar_button(
            "◉   Memories",
            self.show_memories
        )

        self.sidebar_button(
            "▣   System Info",
            self.show_system_info
        )

        self.sidebar_button(
            "▤   Files",
            self.show_files
        )

        self.sidebar_button(
            "⌘   Help",
            self.show_help
        )

        self.sidebar_button(
            "⚙   Settings",
            self.show_settings
        )


        tk.Label(
            bottom,
            text="JARVIS V0.5",
            bg=self.panel,
            fg=self.secondary,
            font=("Segoe UI", 7)
        ).pack(
            pady=(8, 0)
        )


        self.refresh_history()


    def sidebar_button(
        self,
        text,
        command
    ):

        button = tk.Button(
            self.sidebar,

            text=text,

            command=command,

            bg=self.panel2,

            fg=self.text,

            activebackground="#263746",

            activeforeground="#ffffff",

            relief="flat",

            bd=0,

            anchor="w",

            padx=15,

            pady=9,

            font=("Segoe UI", 9),

            cursor="hand2"
        )

        button.pack(
            fill="x",
            padx=10,
            pady=2
        )


    # =====================================================
    # CHAT
    # =====================================================

    def create_chat(self):

        chat_frame = tk.Frame(
            self.content,
            bg=self.bg
        )

        chat_frame.grid(
            row=0,
            column=0,
            sticky="nsew"
        )


        top = tk.Frame(
            chat_frame,
            bg=self.bg,
            height=42
        )

        top.pack(
            fill="x"
        )

        top.pack_propagate(False)


        tk.Label(
            top,
            text="CONVERSATION",
            bg=self.bg,
            fg=self.secondary,
            font=("Segoe UI", 8, "bold")
        ).pack(
            side="left",
            padx=25
        )


        self.chat = scrolledtext.ScrolledText(
            chat_frame,

            wrap=tk.WORD,

            bg=self.bg,

            fg=self.text,

            insertbackground="#ffffff",

            selectbackground="#263746",

            relief="flat",

            bd=0,

            padx=32,

            pady=18,

            font=("Segoe UI", 11),

            spacing1=2,

            spacing3=8
        )

        self.chat.pack(
            fill="both",
            expand=True
        )

        self.chat.configure(
            state="disabled"
        )


        self.chat.tag_configure(
            "jarvis",
            foreground=self.green,
            font=("Segoe UI", 10, "bold")
        )


        self.chat.tag_configure(
            "user",
            foreground=self.blue,
            font=("Segoe UI", 10, "bold")
        )


        self.chat.tag_configure(
            "message",
            foreground=self.text,
            font=("Segoe UI", 11)
        )


        self.chat.tag_configure(
            "system",
            foreground=self.secondary,
            font=("Segoe UI", 9)
        )


    # =====================================================
    # INPUT
    # =====================================================

    def create_input(self):

        frame = tk.Frame(
            self.content,
            bg=self.panel,
            height=92
        )

        frame.grid(
            row=1,
            column=0,
            sticky="ew"
        )

        frame.grid_propagate(
            False
        )


        self.input = tk.Text(
            frame,

            height=2,

            bg=self.input_bg,

            fg=self.text,

            insertbackground="#ffffff",

            selectbackground="#263746",

            relief="flat",

            bd=0,

            padx=14,

            pady=11,

            font=("Segoe UI", 11),

            wrap=tk.WORD
        )

        self.input.pack(
            side="left",

            fill="both",

            expand=True,

            padx=(18, 8),

            pady=15
        )


        self.send_button = tk.Button(
            frame,

            text="SEND  ➤",

            command=self.send_message,

            bg="#253746",

            fg="#ffffff",

            activebackground="#304858",

            activeforeground="#ffffff",

            relief="flat",

            bd=0,

            font=("Segoe UI", 10, "bold"),

            width=12,

            cursor="hand2"
        )

        self.send_button.pack(
            side="right",

            padx=(0, 18),

            pady=15
        )


        self.input.bind(
            "<Return>",
            self.enter_pressed
        )


    # =====================================================
    # SHORTCUTS
    # =====================================================

    def create_shortcuts(self):

        self.bind(
            "<Control-n>",
            lambda e: self.new_chat()
        )

        self.bind(
            "<Control-l>",
            lambda e: self.clear_current_chat()
        )

        self.bind(
            "<Control-m>",
            lambda e: self.show_memories()
        )

        self.bind(
            "<Escape>",
            lambda e: self.focus_input()
        )


    # =====================================================
    # FOCUS
    # =====================================================

    def focus_input(self):

        if hasattr(self, "input"):

            self.input.focus_force()


    # =====================================================
    # ENTER
    # =====================================================

    def enter_pressed(
        self,
        event
    ):

        if event.state & 0x0001:
            return None

        self.send_message()

        return "break"


    # =====================================================
    # SEND
    # =====================================================

    def send_message(self):

        if self.thinking:
            return


        message = self.input.get(
            "1.0",
            "end-1c"
        ).strip()


        if not message:
            return


        self.input.delete(
            "1.0",
            "end"
        )


        self.write_message(
            "YOU",
            message
        )


        self.add_to_current_conversation(
            "YOU",
            message
        )


        command = message.lower()


        if command == "memories":

            self.show_memories()

            return


        if command == "system info":

            self.show_system_info()

            return


        if command == "list files":

            self.show_files()

            return


        if command.startswith(
            "calculate "
        ):

            expression = message[10:].strip()

            try:

                result = calculate(
                    expression
                )

                response = str(result)

            except Exception as e:

                response = str(e)


            self.write_message(
                "JARVIS",
                response
            )

            self.add_to_current_conversation(
                "JARVIS",
                response
            )

            self.save_current()

            return


        if command.startswith(
            "remember "
        ):

            content = message[9:].strip()

            if content:

                save_memory(
                    content
                )

                response = "Memory saved."

            else:

                response = (
                    "Nothing was provided to remember."
                )


            self.write_message(
                "JARVIS",
                response
            )

            self.add_to_current_conversation(
                "JARVIS",
                response
            )

            self.save_current()

            return


        if command.startswith(
            "forget "
        ):

            try:

                memory_id = int(
                    message[7:].strip()
                )

                delete_memory(
                    memory_id
                )

                response = (
                    f"Memory {memory_id} deleted."
                )

            except ValueError:

                response = (
                    "Please provide a valid memory ID."
                )


            self.write_message(
                "JARVIS",
                response
            )

            self.add_to_current_conversation(
                "JARVIS",
                response
            )

            self.save_current()

            return


        self.start_thinking()


        threading.Thread(
            target=self.ask_ai,
            args=(message,),
            daemon=True
        ).start()


    # =====================================================
    # AI
    # =====================================================

    def ask_ai(
        self,
        message
    ):

        try:

            response = ask_jarvis(
                message
            )

        except Exception as e:

            response = (
                "I couldn't reach Gemini right now.\n\n"
                f"Error: {e}\n\n"
                "Local JARVIS tools are still available."
            )


        self.after(
            0,
            lambda: self.ai_finished(
                response
            )
        )


    def ai_finished(
        self,
        response
    ):

        self.stop_thinking()


        self.write_message(
            "JARVIS",
            response
        )


        self.add_to_current_conversation(
            "JARVIS",
            response
        )


        self.save_current()


    # =====================================================
    # THINKING ANIMATION
    # =====================================================

    def start_thinking(self):

        self.thinking = True

        self.send_button.config(
            state="disabled"
        )

        self.thinking_step = 0

        self.animate_thinking()


    def animate_thinking(self):

        if not self.thinking:
            return


        dots = "." * (
            self.thinking_step % 4
        )


        self.status.config(
            text=f"● THINKING{dots}",
            fg=self.yellow
        )


        self.thinking_step += 1


        self.after(
            450,
            self.animate_thinking
        )


    def stop_thinking(self):

        self.thinking = False

        self.status.config(
            text="● ONLINE",
            fg=self.green
        )

        self.send_button.config(
            state="normal"
        )

        self.focus_input()


    # =====================================================
    # CHAT DISPLAY
    # =====================================================

    def write_message(
        self,
        speaker,
        message
    ):

        self.chat.configure(
            state="normal"
        )


        if speaker == "YOU":

            self.chat.insert(
                "end",
                "\nYOU\n",
                "user"
            )

        else:

            self.chat.insert(
                "end",
                "\nJARVIS\n",
                "jarvis"
            )


        self.chat.insert(
            "end",
            message + "\n",
            "message"
        )


        self.chat.see(
            "end"
        )


        self.chat.configure(
            state="disabled"
        )


    # =====================================================
    # CONVERSATIONS
    # =====================================================

    def new_chat(
        self,
        initial=False
    ):

        conversation = {
            "title": "New Conversation",
            "created": datetime.now().isoformat(),
            "messages": []
        }


        self.conversations.append(
            conversation
        )


        self.current_conversation = conversation


        if not initial:

            self.chat.configure(
                state="normal"
            )

            self.chat.delete(
                "1.0",
                "end"
            )

            self.chat.configure(
                state="disabled"
            )


            self.write_message(
                "JARVIS",
                "New conversation started."
            )


        self.save_current()

        self.refresh_history()

        self.focus_input()


    def refresh_history(self):

        self.history_list.delete(
            0,
            "end"
        )


        for conversation in self.conversations:

            title = conversation.get(
                "title",
                "Conversation"
            )

            self.history_list.insert(
                "end",
                title
            )


        if self.current_conversation:

            try:

                index = self.conversations.index(
                    self.current_conversation
                )

                self.history_list.selection_clear(
                    0,
                    "end"
                )

                self.history_list.selection_set(
                    index
                )

                self.history_list.see(
                    index
                )

            except ValueError:

                pass


    def history_selected(
        self,
        event=None
    ):

        selection = self.history_list.curselection()

        if not selection:
            return


        index = selection[0]


        if index >= len(
            self.conversations
        ):

            return


        self.current_conversation = (
            self.conversations[index]
        )


        self.load_current_conversation()


    def load_current_conversation(self):

        self.chat.configure(
            state="normal"
        )

        self.chat.delete(
            "1.0",
            "end"
        )

        self.chat.configure(
            state="disabled"
        )


        messages = self.current_conversation.get(
            "messages",
            []
        )


        if not messages:

            self.write_message(
                "JARVIS",
                "Online. Local systems initialized."
            )

            return


        for message in messages:

            self.write_message(
                message["speaker"],
                message["message"]
            )


        self.focus_input()


    def add_to_current_conversation(
        self,
        speaker,
        message
    ):

        if not self.current_conversation:
            return


        messages = self.current_conversation.setdefault(
            "messages",
            []
        )


        messages.append(
            {
                "speaker": speaker,
                "message": message,
                "time": datetime.now().isoformat()
            }
        )


        if (
            speaker == "YOU"
            and
            self.current_conversation.get(
                "title"
            )
            == "New Conversation"
        ):

            title = message.strip()

            if len(title) > 32:

                title = title[:32] + "..."

            self.current_conversation["title"] = title

            self.refresh_history()


    def save_current(self):

        save_conversations(
            self.conversations
        )


    def rename_conversation(
        self,
        event=None
    ):

        selection = self.history_list.curselection()

        if not selection:
            return


        index = selection[0]


        conversation = self.conversations[
            index
        ]


        new_name = simpledialog.askstring(
            "Rename Conversation",
            "Enter a new name:",
            initialvalue=conversation.get(
                "title",
                "Conversation"
            ),
            parent=self
        )


        if not new_name:
            return


        conversation["title"] = new_name.strip()


        self.save_current()

        self.refresh_history()


    def clear_current_chat(self):

        if not self.current_conversation:
            return


        self.current_conversation["messages"] = []

        self.save_current()


        self.chat.configure(
            state="normal"
        )

        self.chat.delete(
            "1.0",
            "end"
        )

        self.chat.configure(
            state="disabled"
        )


        self.write_message(
            "JARVIS",
            "Conversation cleared."
        )


    # =====================================================
    # MEMORIES
    # =====================================================

    def show_memories(self):

        memories = get_memories()


        if not memories:

            self.write_message(
                "JARVIS",
                "No saved memories."
            )

            return


        text = "LONG-TERM MEMORY\n\n"


        for memory_id, content, created_at in memories:

            text += (
                f"[{memory_id}] "
                f"{content}\n"
            )


        self.write_message(
            "JARVIS",
            text
        )


    # =====================================================
    # SYSTEM
    # =====================================================

    def show_system_info(self):

        info = get_system_info()


        text = "SYSTEM INFORMATION\n\n"


        for key, value in info.items():

            text += (
                f"{key}: {value}\n"
            )


        self.write_message(
            "JARVIS",
            text
        )


    # =====================================================
    # FILES
    # =====================================================

    def show_files(self):

        try:

            files = list_files(".")


            text = (
                "FILES IN CURRENT DIRECTORY\n\n"
            )


            for item in files:

                text += (
                    f"• {item}\n"
                )


            self.write_message(
                "JARVIS",
                text
            )


        except Exception as e:

            self.write_message(
                "JARVIS",
                str(e)
            )


    # =====================================================
    # HELP
    # =====================================================

    def show_help(self):

        text = """JARVIS COMMANDS

calculate <expression>

remember <something>

memories

forget <id>

system info

list files


KEYBOARD SHORTCUTS

Enter
Send message

Shift + Enter
New line

Ctrl + N
New conversation

Ctrl + L
Clear conversation

Ctrl + M
Show memories

Escape
Focus message box


SYSTEM TRAY

Closing the window hides JARVIS
to the Windows system tray.

Use the JARVIS tray icon to:

Show JARVIS
Hide JARVIS
Exit JARVIS


NORMAL QUESTIONS

Normal questions are sent to Gemini.

JARVIS is currently local-first.
"""


        self.write_message(
            "JARVIS",
            text
        )


    # =====================================================
    # SETTINGS
    # =====================================================

    def show_settings(self):

        window = tk.Toplevel(
            self
        )

        window.title(
            "JARVIS Settings"
        )

        window.geometry(
            "500x420"
        )

        window.configure(
            bg=self.panel
        )


        tk.Label(
            window,
            text="JARVIS SETTINGS",
            bg=self.panel,
            fg=self.text,
            font=("Segoe UI", 18, "bold")
        ).pack(
            anchor="w",
            padx=25,
            pady=(25, 5)
        )


        tk.Label(
            window,
            text="Current configuration",
            bg=self.panel,
            fg=self.secondary,
            font=("Segoe UI", 9)
        ).pack(
            anchor="w",
            padx=25
        )


        info = tk.Frame(
            window,
            bg=self.panel2
        )

        info.pack(
            fill="x",
            padx=25,
            pady=25
        )


        settings = [
            ("AI Model", "Gemini 2.5 Flash"),
            ("Memory", "Enabled"),
            ("Local Tools", "Enabled"),
            ("File Access", "Read-only"),
            ("Web Research", "Gemini Search"),
            ("Architecture", "Local-first"),
            ("System Tray", "Enabled")
        ]


        for key, value in settings:

            row = tk.Frame(
                info,
                bg=self.panel2
            )

            row.pack(
                fill="x",
                padx=15,
                pady=8
            )


            tk.Label(
                row,
                text=key,
                bg=self.panel2,
                fg=self.secondary,
                font=("Segoe UI", 9)
            ).pack(
                side="left"
            )


            tk.Label(
                row,
                text=value,
                bg=self.panel2,
                fg=self.text,
                font=("Segoe UI", 9, "bold")
            ).pack(
                side="right"
            )


        tk.Button(
            window,
            text="CLOSE",
            command=window.destroy,
            bg="#253746",
            fg="#ffffff",
            activebackground="#304858",
            relief="flat",
            bd=0,
            padx=25,
            pady=9,
            cursor="hand2"
        ).pack(
            pady=5
        )


# =========================================================
# START
# =========================================================

if __name__ == "__main__":

    app = JarvisUI()

    app.mainloop()
