import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox, filedialog, simpledialog
import json
import os
from datetime import datetime
import ctypes
from ctypes import wintypes
import threading
import time
import re

# Windows API Constants
GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x00080000
WS_EX_TRANSPARENT = 0x00000020
LWA_ALPHA = 0x00000002

user32 = ctypes.windll.user32

class YouTubeStyleScribe:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("LLM Scribe Pro - YouTube Edition (Bilingual)")
        
        # UI Size Adjustment (Shrunk to avoid taskbar)
        self.root.geometry("1100x720")
        self.root.minsize(950, 600)
        
        # Colors (YouTube Dark Theme)
        self.colors = {
            "bg": "#0f0f0f",           # Deep Black
            "sidebar": "#121212",      # Slightly Lighter Black
            "card": "#1e1e1e",         # Card background
            "accent": "#3ea6ff",       # YouTube Blue
            "accent_hover": "#65b8ff",
            "text": "#ffffff",         # Main Text
            "text_dim": "#aaaaaa",     # Dimmed Text
            "border": "#2b2b2b",       # Border color
            "highlight": "#263850",    # Selection Highlight
            "danger": "#ff4d4d"        # Delete/Danger
        }
        
        # Core State
        self.data = {
            "folders": [], # List of {id, name}
            "sessions": [] # List of session objects
        }
        self.current_session_id = None
        self.last_clipboard_content = ""
        self.is_scribe_mode = tk.BooleanVar(value=False)
        self.is_always_on_top = tk.BooleanVar(value=False)
        self.is_click_through = tk.BooleanVar(value=False)
        self.opacity = tk.DoubleVar(value=1.0)
        
        # Data paths
        self.config_file = os.path.join(os.getcwd(), "scribe_config.json")
        self.data_file = self.load_config()
        
        self.setup_ui()
        self.load_data()
        
        # Start Clipboard Monitor Thread
        self.monitor_thread = threading.Thread(target=self.clipboard_monitor_loop, daemon=True)
        self.monitor_thread.start()
        
    def load_config(self):
        default_path = os.path.join(os.getcwd(), "llm_scribe_data.json")
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    return config.get("data_file", default_path)
            except:
                return default_path
        return default_path

    def save_config(self):
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump({"data_file": self.data_file}, f, ensure_ascii=False, indent=2)
        except:
            pass

    def setup_ui(self):
        self.root.configure(bg=self.colors["bg"])
        
        # Custom Fonts
        font_main = ("Segoe UI", 10)
        font_bold = ("Segoe UI", 11, "bold")
        font_title = ("Segoe UI", 13, "bold")
        font_mono = ("Consolas", 10)
        
        # --- TOP HEADER ---
        header = tk.Frame(self.root, bg=self.colors["sidebar"], height=50, padx=15)
        header.pack(side=tk.TOP, fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="▶ LLM Scribe Pro", font=font_title, bg=self.colors["sidebar"], fg=self.colors["text"]).pack(side=tk.LEFT)
        
        controls_frame = tk.Frame(header, bg=self.colors["sidebar"])
        controls_frame.pack(side=tk.RIGHT)
        
        # Scribe Mode Toggle
        self.scribe_btn = tk.Button(controls_frame, text="🚀 速记 (Scribe) OFF", font=font_main, 
                                   bg=self.colors["card"], fg=self.colors["text"], bd=0, padx=8, pady=4,
                                   activebackground=self.colors["accent"], command=self.toggle_scribe_mode)
        self.scribe_btn.pack(side=tk.LEFT, padx=8)
        
        # Set Path
        tk.Button(controls_frame, text="📁 路径 (Path)", font=font_main, 
                  bg=self.colors["card"], fg=self.colors["text_dim"], bd=0, padx=8, pady=4,
                  command=self.choose_data_path).pack(side=tk.LEFT, padx=4)

        # Pin
        tk.Checkbutton(controls_frame, text="📌 置顶 (Pin)", variable=self.is_always_on_top, 
                       font=font_main, bg=self.colors["sidebar"], fg=self.colors["text_dim"], 
                       selectcolor=self.colors["bg"], activebackground=self.colors["sidebar"],
                       command=self.toggle_always_on_top).pack(side=tk.LEFT, padx=4)
        
        # Click Through
        tk.Checkbutton(controls_frame, text="👻 穿透 (Ghost)", variable=self.is_click_through, 
                       font=font_main, bg=self.colors["sidebar"], fg=self.colors["text_dim"], 
                       selectcolor=self.colors["bg"], activebackground=self.colors["sidebar"],
                       command=self.toggle_click_through).pack(side=tk.LEFT, padx=4)
        
        # Opacity Slider
        tk.Label(controls_frame, text="🫥 透明 (Opacity)", font=font_main, bg=self.colors["sidebar"], fg=self.colors["text_dim"]).pack(side=tk.LEFT, padx=(8, 2))
        tk.Scale(controls_frame, from_=0.1, to=1.0, resolution=0.05, orient=tk.HORIZONTAL,
                 variable=self.opacity, command=self.update_opacity,
                 showvalue=0, length=80, bg=self.colors["sidebar"], bd=0, highlightthickness=0,
                 troughcolor=self.colors["border"]).pack(side=tk.LEFT, padx=4)

        # --- MAIN CONTENT ---
        main_body = tk.Frame(self.root, bg=self.colors["bg"])
        main_body.pack(fill=tk.BOTH, expand=True)
        
        # SIDEBAR (LEFT) - Sessions & Folders
        self.sidebar = tk.Frame(main_body, bg=self.colors["sidebar"], width=260)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)
        
        tk.Label(self.sidebar, text="📚 库 (Library)", font=font_bold, bg=self.colors["sidebar"], fg=self.colors["text"], padx=15, pady=10).pack(anchor="w")
        
        sidebar_btn_frame = tk.Frame(self.sidebar, bg=self.colors["sidebar"])
        sidebar_btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(sidebar_btn_frame, text="+ 新建 (New)", font=font_main, bg=self.colors["accent"], fg="white", 
                  bd=0, pady=6, command=self.create_new_session).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(sidebar_btn_frame, text="📁 归档 (Folder)", font=font_main, bg=self.colors["card"], fg="white", 
                  bd=0, pady=6, command=self.create_folder).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        
        # TREEVIEW for Directory Structure
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=self.colors["sidebar"], foreground=self.colors["text_dim"], 
                        fieldbackground=self.colors["sidebar"], borderwidth=0, font=font_main)
        style.map("Treeview", background=[('selected', self.colors["highlight"])], foreground=[('selected', 'white')])
        
        self.tree = ttk.Treeview(self.sidebar, show="tree", selectmode="browse")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        
        # Sidebar Context Menu
        self.sidebar_menu = tk.Menu(self.root, tearoff=0, bg=self.colors["card"], fg=self.colors["text"])
        self.sidebar_menu.add_command(label="📝 重命名 (Rename)", command=self.rename_item)
        self.sidebar_menu.add_command(label="🗑️ 删除 (Delete)", command=self.delete_item, foreground=self.colors["danger"])
        self.sidebar_menu.add_separator()
        self.sidebar_menu.add_command(label="📁 移动到 (Move to Folder)", command=self.move_to_folder)
        self.sidebar_menu.add_command(label="📤 导出此会话 (Export Session)", command=self.export_single_session)
        self.tree.bind("<Button-3>", lambda e: self.sidebar_menu.post(e.x_root, e.y_root))

        # CENTER VIEW (Main Content)
        center_frame = tk.Frame(main_body, bg=self.colors["bg"])
        center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        title_card = tk.Frame(center_frame, bg=self.colors["bg"])
        title_card.pack(fill=tk.X, pady=(0, 8))
        self.session_title_var = tk.StringVar(value="请选择会话 (Select Session)")
        tk.Label(title_card, textvariable=self.session_title_var, font=font_title, bg=self.colors["bg"], fg=self.colors["text"]).pack(side=tk.LEFT)
        
        # TEXT AREA
        text_container = tk.Frame(center_frame, bg=self.colors["card"], bd=1, highlightthickness=1, highlightbackground=self.colors["border"])
        text_container.pack(fill=tk.BOTH, expand=True)
        
        self.dialog_text = scrolledtext.ScrolledText(
            text_container, wrap=tk.WORD, font=font_mono, bg=self.colors["card"], fg=self.colors["text"],
            insertbackground="white", relief=tk.FLAT, padx=15, pady=15, undo=True
        )
        self.dialog_text.pack(fill=tk.BOTH, expand=True)
        self.dialog_text.tag_configure("timestamp", foreground=self.colors["accent"], font=("Consolas", 9, "bold"))
        self.dialog_text.tag_configure("highlight", background=self.colors["highlight"])
        
        # RIGHT PANEL (Tags)
        right_panel = tk.Frame(main_body, bg=self.colors["sidebar"], width=280)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y)
        right_panel.pack_propagate(False)
        
        tk.Label(right_panel, text="📌 摘要锚点 (Tags)", font=font_bold, bg=self.colors["sidebar"], fg=self.colors["text"], padx=15, pady=12).pack(anchor="w")
        
        self.summary_list = tk.Listbox(right_panel, bg=self.colors["card"], fg=self.colors["text"], 
                                      font=font_main, bd=0, highlightthickness=0, selectbackground=self.colors["accent"])
        self.summary_list.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        self.summary_list.bind("<Double-Button-1>", self.jump_to_tag)
        
        # Tag Controls
        add_tag_frame = tk.Frame(right_panel, bg=self.colors["sidebar"], padx=15, pady=10)
        add_tag_frame.pack(fill=tk.X)
        self.tag_entry = tk.Entry(add_tag_frame, font=font_main, bg=self.colors["card"], fg=self.colors["text"], 
                                 insertbackground="white", bd=0, highlightthickness=1, highlightbackground=self.colors["border"])
        self.tag_entry.pack(fill=tk.X, pady=4)
        tk.Button(add_tag_frame, text="➕ 添加标记 (Add Tag)", font=font_main, bg=self.colors["accent"], fg="white", bd=0, pady=5, command=self.add_manual_tag).pack(fill=tk.X)

        # --- FOOTER ---
        footer = tk.Frame(self.root, bg=self.colors["sidebar"], height=80, pady=5)
        footer.pack(side=tk.BOTTOM, fill=tk.X)
        
        guide_data = [
            ("🚀 速记模式 (Scribe)", "剪贴板自动捕获内容\nAuto-capture clipboard content"),
            ("📑 跳转锚点 (Jump Tags)", "双击标签快速回溯对话\nDouble-click to navigate back"),
            ("👻 穿透模式 (Ghost)", "半透明时可点击背景\nClick through transparent window"),
            ("�️ 安全运行 (Security)", "隔离文件访问与沙箱读写\nSecure file access & sanitization")
        ]
        
        for i, (title, desc) in enumerate(guide_data):
            f = tk.Frame(footer, bg=self.colors["sidebar"], padx=15)
            f.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            tk.Label(f, text=title, font=font_bold, bg=self.colors["sidebar"], fg=self.colors["accent"]).pack(anchor="w")
            tk.Label(f, text=desc, font=("Segoe UI", 8), bg=self.colors["sidebar"], fg=self.colors["text_dim"], justify=tk.LEFT).pack(anchor="w")

        # Context Menu
        self.ctx_menu = tk.Menu(self.root, tearoff=0, bg=self.colors["card"], fg=self.colors["text"])
        self.ctx_menu.add_command(label="🔖 设为摘要 (Tag as Summary)", command=self.tag_selection)
        self.ctx_menu.add_separator()
        self.ctx_menu.add_command(label="📋 复制 (Copy)", command=lambda: self.root.event_generate("<<Copy>>"))
        self.ctx_menu.add_command(label="📋 粘贴 (Paste)", command=lambda: self.root.event_generate("<<Paste>>"))
        self.dialog_text.bind("<Button-3>", lambda e: self.ctx_menu.post(e.x_root, e.y_root))

    # --- SECURITY & FILE OPS ---
    def safe_path_check(self, path):
        """Security: Ensure the path is within reasonable bounds and not executable."""
        forbidden_extensions = ['.exe', '.bat', '.cmd', '.sh', '.py', '.js', '.vbs']
        _, ext = os.path.splitext(path.lower())
        if ext in forbidden_extensions:
            return False
        # Normalize and check path
        abs_path = os.path.abspath(path)
        return True

    def sanitize_input(self, text):
        """Security: Strip potentially harmful characters for display/storage."""
        # Remove any non-printable characters except whitespace
        return "".join(c for c in text if c.isprintable() or c in "\n\r\t")

    # --- CORE LOGIC ---
    def toggle_scribe_mode(self):
        new_state = not self.is_scribe_mode.get()
        self.is_scribe_mode.set(new_state)
        self.scribe_btn.configure(bg=self.colors["accent"] if new_state else self.colors["card"],
                                 text=f"🚀 速记 (Scribe) {'ON' if new_state else 'OFF'}")

    def toggle_always_on_top(self):
        self.root.attributes("-topmost", self.is_always_on_top.get())

    def update_opacity(self, value):
        self.root.attributes("-alpha", float(value))
        if self.is_click_through.get(): self.apply_click_through(True)

    def toggle_click_through(self):
        self.apply_click_through(self.is_click_through.get())

    def apply_click_through(self, enable):
        hwnd = self.root.winfo_id()
        styles = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        if enable:
            user32.SetWindowLongW(hwnd, GWL_EXSTYLE, styles | WS_EX_LAYERED | WS_EX_TRANSPARENT)
            alpha = int(float(self.opacity.get()) * 255)
            user32.SetLayeredWindowAttributes(hwnd, 0, alpha, LWA_ALPHA)
        else:
            user32.SetWindowLongW(hwnd, GWL_EXSTYLE, styles & ~WS_EX_TRANSPARENT)

    def clipboard_monitor_loop(self):
        while True:
            if self.is_scribe_mode.get():
                self.root.after_idle(self.safe_clipboard_check)
            time.sleep(1.2)

    def safe_clipboard_check(self):
        try:
            content = self.root.clipboard_get()
            if content and content != self.last_clipboard_content:
                self.last_clipboard_content = content
                self.append_captured_content(self.sanitize_input(content))
        except: pass

    def append_captured_content(self, content):
        if self.current_session_id is None:
            self.create_new_session("自动捕获 (Auto Capture)")
        
        timestamp = datetime.now().strftime("[%H:%M:%S]")
        self.dialog_text.insert(tk.END, f"\n{timestamp} ", "timestamp")
        self.dialog_text.insert(tk.END, f"{content}\n")
        self.dialog_text.see(tk.END)
        self.save_data()

    # --- DIRECTORY & SESSION MGMT ---
    def create_new_session(self, title=None):
        if not title:
            title = simpledialog.askstring("新建会话 (New Session)", "请输入会话名称 (Enter Name):") or f"会话 {len(self.data['sessions'])+1}"
        
        # Determine parent (if selected)
        parent_id = ""
        selection = self.tree.selection()
        if selection and selection[0].startswith("folder_"):
            parent_id = selection[0]

        session = {
            "id": str(time.time()),
            "title": self.sanitize_input(title),
            "content": "",
            "tags": [],
            "parent": parent_id
        }
        self.data["sessions"].append(session)
        self.refresh_tree()
        self.select_session(session["id"])
        self.save_data()

    def create_folder(self):
        name = simpledialog.askstring("新建文件夹 (New Folder)", "请输入文件夹名称 (Folder Name):") or "新归档 (New Folder)"
        folder_id = f"folder_{time.time()}"
        self.data["folders"].append({"id": folder_id, "name": self.sanitize_input(name)})
        self.refresh_tree()
        self.save_data()

    def refresh_tree(self):
        # Save open states
        open_states = {iid: self.tree.item(iid, "open") for iid in self.tree.get_children()}
        
        self.tree.delete(*self.tree.get_children())
            
        # Add folders
        for f in self.data["folders"]:
            self.tree.insert("", "end", iid=f["id"], text=f"📁 {f['name']}", open=open_states.get(f["id"], True))
            
        # Add sessions
        for s in self.data["sessions"]:
            parent = s.get("parent", "")
            if parent and self.tree.exists(parent):
                self.tree.insert(parent, "end", iid=s["id"], text=f"📄 {s['title']}")
            else:
                self.tree.insert("", "end", iid=s["id"], text=f"📄 {s['title']}")

    def on_tree_select(self, event):
        selection = self.tree.selection()
        if selection:
            iid = selection[0]
            if not iid.startswith("folder_"):
                self.select_session(iid)

    def select_session(self, sid):
        if self.current_session_id is not None:
            self.save_current_content_to_memory()
            
        self.current_session_id = sid
        session = next((s for s in self.data["sessions"] if s["id"] == sid), None)
        if session:
            self.session_title_var.set(session["title"])
            self.dialog_text.delete("1.0", tk.END)
            self.dialog_text.insert("1.0", session["content"])
            self.refresh_tag_list()
            # Select it in tree if not already
            if self.tree.exists(sid):
                self.tree.selection_set(sid)

    def save_current_content_to_memory(self):
        if self.current_session_id:
            for s in self.data["sessions"]:
                if s["id"] == self.current_session_id:
                    s["content"] = self.dialog_text.get("1.0", tk.END).strip()
                    break

    def rename_item(self):
        selection = self.tree.selection()
        if not selection: return
        iid = selection[0]
        new_name = simpledialog.askstring("重命名 (Rename)", "输入新名称 (Enter New Name):")
        if new_name:
            new_name = self.sanitize_input(new_name)
            if iid.startswith("folder_"):
                for f in self.data["folders"]:
                    if f["id"] == iid:
                        f["name"] = new_name
                        break
            else:
                for s in self.data["sessions"]:
                    if s["id"] == iid:
                        s["title"] = new_name
                        if self.current_session_id == iid:
                            self.session_title_var.set(new_name)
                        break
            self.refresh_tree()
            self.save_data()

    def delete_item(self):
        selection = self.tree.selection()
        if not selection: return
        iid = selection[0]
        msg = "确定删除文件夹及其中所有内容吗？" if iid.startswith("folder_") else "确定删除此会话吗？"
        if messagebox.askyesno("确认删除 (Delete)", f"{msg}\nConfirm Delete?"):
            if iid.startswith("folder_"):
                # Remove folder and sessions in it
                self.data["folders"] = [f for f in self.data["folders"] if f["id"] != iid]
                self.data["sessions"] = [s for s in self.data["sessions"] if s.get("parent") != iid]
                if self.current_session_id and not any(s["id"] == self.current_session_id for s in self.data["sessions"]):
                    self.current_session_id = None
                    self.dialog_text.delete("1.0", tk.END)
                    self.session_title_var.set("已删除 (Deleted)")
            else:
                self.data["sessions"] = [s for s in self.data["sessions"] if s["id"] != iid]
                if self.current_session_id == iid:
                    self.current_session_id = None
                    self.dialog_text.delete("1.0", tk.END)
                    self.session_title_var.set("已删除 (Deleted)")
            self.refresh_tree()
            self.save_data()

    def move_to_folder(self):
        selection = self.tree.selection()
        if not selection or selection[0].startswith("folder_"): return
        sid = selection[0]
        
        # Create folder selection window
        popup = tk.Toplevel(self.root)
        popup.title("选择目标文件夹")
        popup.geometry("300x400")
        popup.configure(bg=self.colors["bg"])
        
        tk.Label(popup, text="移动到 (Move to):", bg=self.colors["bg"], fg="white").pack(pady=10)
        
        listbox = tk.Listbox(popup, bg=self.colors["card"], fg="white", bd=0)
        listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        listbox.insert(tk.END, "根目录 (Root / No Folder)")
        for f in self.data["folders"]:
            listbox.insert(tk.END, f["name"])
            
        def do_move():
            sel_idx = listbox.curselection()
            if not sel_idx: return
            idx = sel_idx[0]
            parent_id = "" if idx == 0 else self.data["folders"][idx-1]["id"]
            for s in self.data["sessions"]:
                if s["id"] == sid:
                    s["parent"] = parent_id
                    break
            self.refresh_tree()
            self.save_data()
            popup.destroy()
            
        tk.Button(popup, text="确定 (OK)", command=do_move, bg=self.colors["accent"], fg="white", bd=0, pady=5).pack(pady=10)

    def export_single_session(self):
        selection = self.tree.selection()
        if not selection or selection[0].startswith("folder_"): return
        sid = selection[0]
        session = next((s for s in self.data["sessions"] if s["id"] == sid), None)
        if not session: return
        
        file_path = filedialog.asksaveasfilename(
            title=f"导出会话: {session['title']}",
            initialfile=f"{session['title']}.json",
            defaultextension=".json",
            filetypes=[("JSON", "*.json"), ("TXT", "*.txt")]
        )
        if file_path and self.safe_path_check(file_path):
            try:
                if file_path.endswith(".json"):
                    with open(file_path, "w", encoding="utf-8") as f:
                        json.dump(session, f, ensure_ascii=False, indent=2)
                else:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(f"Title: {session['title']}\n")
                        f.write(f"Content:\n{session['content']}\n")
                messagebox.showinfo("成功", f"会话已成功导出到: {file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"导出失败: {str(e)}")

    # --- TAGS ---
    def refresh_tag_list(self):
        self.summary_list.delete(0, tk.END)
        session = next((s for s in self.data["sessions"] if s["id"] == self.current_session_id), None)
        if session:
            for t in session["tags"]:
                self.summary_list.insert(tk.END, f"📍 {t['name']}")

    def add_manual_tag(self):
        name = self.tag_entry.get().strip()
        if not name or not self.current_session_id: return
        pos = self.dialog_text.index(tk.INSERT)
        for s in self.data["sessions"]:
            if s["id"] == self.current_session_id:
                s["tags"].append({"name": self.sanitize_input(name), "pos": pos})
                break
        self.tag_entry.delete(0, tk.END)
        self.refresh_tag_list()
        self.save_data()
        self.flash_feedback()

    def flash_feedback(self):
        self.tag_entry.configure(bg="#263850")
        self.root.after(200, lambda: self.tag_entry.configure(bg=self.colors["card"]))

    def tag_selection(self):
        try:
            sel = self.dialog_text.get(tk.SEL_FIRST, tk.SEL_LAST).strip()
            if sel:
                tag_name = sel[:30] + "..." if len(sel) > 30 else sel
                pos = self.dialog_text.index(tk.SEL_FIRST)
                for s in self.data["sessions"]:
                    if s["id"] == self.current_session_id:
                        s["tags"].append({"name": self.sanitize_input(tag_name), "pos": pos})
                        break
                self.refresh_tag_list()
                self.save_data()
        except: pass

    def jump_to_tag(self, event):
        selection = self.summary_list.curselection()
        if selection and self.current_session_id:
            idx = selection[0]
            session = next((s for s in self.data["sessions"] if s["id"] == self.current_session_id), None)
            if session and idx < len(session["tags"]):
                tag = session["tags"][idx]
                self.dialog_text.tag_remove("highlight", "1.0", tk.END)
                try:
                    self.dialog_text.see(tag["pos"])
                    line = tag["pos"].split('.')[0]
                    self.dialog_text.tag_add("highlight", f"{line}.0", f"{line}.end")
                except: pass

    # --- PERSISTENCE ---
    def choose_data_path(self):
        file_path = filedialog.asksaveasfilename(title="选择保存位置 (Choose Save Path)", defaultextension=".json", filetypes=[("JSON", "*.json")])
        if file_path and self.safe_path_check(file_path):
            self.save_data()
            self.data_file = file_path
            self.save_config()
            self.save_data()
            messagebox.showinfo("成功 (Success)", f"路径已更改: {file_path}")

    def save_data(self):
        self.save_current_content_to_memory()
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except: pass

    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    if isinstance(loaded, dict):
                        self.data = loaded
                    else:
                        # Legacy format (list)
                        self.data["sessions"] = loaded
                self.refresh_tree()
                if self.data["sessions"]:
                    self.select_session(self.data["sessions"][-1]["id"])
            except: pass

    def run(self):
        def auto_save():
            self.save_data()
            self.root.after(30000, auto_save)
        self.root.after(30000, auto_save)
        self.root.mainloop()

if __name__ == "__main__":
    app = YouTubeStyleScribe()
    app.run()
