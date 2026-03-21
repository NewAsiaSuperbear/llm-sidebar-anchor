import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox
import json
import os
from datetime import datetime

class LLMConversationManager:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("LLM对话旁听速记员")
        self.root.geometry("1100x750")
        
        # 数据存储
        self.conversations = []
        self.current_conversation_id = None
        self.last_clipboard_content = ""
        self.is_scribe_mode = tk.BooleanVar(value=False)
        self.is_always_on_top = tk.BooleanVar(value=False)
        self.is_compact_mode = tk.BooleanVar(value=False)
        self.opacity = tk.DoubleVar(value=1.0)
        
        # 界面配色与字体
        self.font_main = ("微软雅黑", 10)
        self.font_bold = ("微软雅黑", 10, "bold")
        self.bg_color = "#f5f6fa"
        self.primary_color = "#3498db"
        
        # 创建主框架
        self.create_widgets()
        
        # 加载现有数据
        self.load_data()
        
        # 启动剪贴板监控
        self.check_clipboard()
        
    def create_widgets(self):
        self.root.configure(bg=self.bg_color)
        
        # 顶部工具栏
        toolbar = tk.Frame(self.root, bd=1, relief=tk.FLAT, bg="white", height=40)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        toolbar.pack_propagate(False)
        
        tk.Checkbutton(toolbar, text="🚀 速记模式 (监控剪贴板)", variable=self.is_scribe_mode, 
                       bg="white", font=self.font_main).pack(side=tk.LEFT, padx=15)
        tk.Checkbutton(toolbar, text="📌 窗口置顶", variable=self.is_always_on_top, 
                       command=self.toggle_always_on_top, bg="white", font=self.font_main).pack(side=tk.LEFT, padx=15)
        tk.Checkbutton(toolbar, text="🤏 紧凑模式", variable=self.is_compact_mode, 
                       command=self.toggle_compact_mode, bg="white", font=self.font_main).pack(side=tk.LEFT, padx=15)
        
        tk.Label(toolbar, text="🫥 透明度:", bg="white", font=self.font_main).pack(side=tk.LEFT, padx=(15, 5))
        self.opacity_scale = tk.Scale(toolbar, from_=0.3, to=1.0, resolution=0.1, orient=tk.HORIZONTAL, 
                                     variable=self.opacity, command=self.change_opacity, 
                                     showvalue=0, length=100, bg="white", highlightthickness=0)
        self.opacity_scale.pack(side=tk.LEFT, padx=5)
        
        # 主容器
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧 - 对话区域
        self.left_frame = tk.Frame(main_frame, bg=self.bg_color)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # 对话显示区域头部
        header_left = tk.Frame(self.left_frame, bg=self.bg_color)
        header_left.pack(fill=tk.X)
        tk.Label(header_left, text="对话实时流", font=("微软雅黑", 12, "bold"), 
                 bg=self.bg_color, fg="#2f3640").pack(side=tk.LEFT, pady=5)
        
        # 对话显示文本框
        self.dialog_text = scrolledtext.ScrolledText(
            self.left_frame, wrap=tk.WORD, font=self.font_main, bg="white", 
            relief=tk.FLAT, padx=10, pady=10, undo=True
        )
        self.dialog_text.pack(fill=tk.BOTH, expand=True)
        
        # 配置文本标签
        self.dialog_text.tag_configure("highlight", background="#fff9c4")
        self.dialog_text.tag_configure("timestamp", foreground="#95a5a6", font=("Consolas", 9))
        self.dialog_text.tag_configure("system", foreground="#3498db", font=self.font_bold)
        
        # 右键菜单
        self.context_menu = tk.Menu(self.dialog_text, tearoff=0)
        self.context_menu.add_command(label="🔖 将选中文本设为摘要", command=self.add_selection_as_summary)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="📋 复制", command=lambda: self.root.event_generate("<<Copy>>"))
        self.context_menu.add_command(label="✂️ 剪切", command=lambda: self.root.event_generate("<<Cut>>"))
        self.context_menu.add_command(label="📋 粘贴", command=lambda: self.root.event_generate("<<Paste>>"))
        
        self.dialog_text.bind("<Button-3>", self.show_context_menu)
        
        # 左侧控制按钮
        btn_frame = tk.Frame(self.left_frame, bg=self.bg_color)
        btn_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(btn_frame, text="💾 保存对话", command=self.save_current_conversation, 
                  bg="white", relief=tk.GROOVE, padx=10).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="🗑️ 清空显示", command=self.clear_dialog, 
                  bg="white", relief=tk.GROOVE, padx=10).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="🔖 标记当前位置为摘要", command=self.add_summary, 
                  bg="#3498db", fg="white", relief=tk.FLAT, padx=10).pack(side=tk.RIGHT, padx=2)
        
        # 右侧 - 摘要管理面板
        self.right_frame = tk.Frame(main_frame, bg="white", width=350, relief=tk.FLAT)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False)
        self.right_frame.pack_propagate(False)
        
        tk.Label(self.right_frame, text="速记摘要 & 快速导航", font=("微软雅黑", 12, "bold"), 
                 bg="white", fg="#2c3e50").pack(pady=15)
        
        # 摘要列表
        list_frame = tk.Frame(self.right_frame, bg="white")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10)
        
        self.summary_listbox = tk.Listbox(list_frame, font=self.font_main, 
                                          relief=tk.FLAT, bg="#f9f9f9", selectmode=tk.SINGLE,
                                          highlightthickness=0, borderwidth=0)
        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.summary_listbox.yview)
        self.summary_listbox.config(yscrollcommand=scrollbar.set)
        
        self.summary_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.summary_listbox.bind('<Double-Button-1>', self.jump_to_conversation)
        
        # 右侧按钮
        control_frame = tk.Frame(self.right_frame, bg="white")
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(control_frame, text="+ 新建主题对话", command=self.new_conversation, 
                  bg="#2ecc71", fg="white", font=self.font_bold, relief=tk.FLAT, pady=5).pack(fill=tk.X, pady=2)
        tk.Button(control_frame, text="❌ 删除选中记录", command=self.delete_selected, 
                  bg="#e74c3c", fg="white", font=self.font_main, relief=tk.FLAT, pady=2).pack(fill=tk.X, pady=2)
        
        # 快速输入
        input_frame = tk.LabelFrame(self.right_frame, text="手动添加摘要点", bg="white", font=self.font_main)
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.summary_entry = tk.Entry(input_frame, font=self.font_main, bg="#f1f2f6", relief=tk.FLAT)
        self.summary_entry.pack(fill=tk.X, padx=5, pady=5)
        tk.Button(input_frame, text="添加标记", command=self.add_summary_from_entry, 
                  bg="#3498db", fg="white", relief=tk.FLAT).pack(fill=tk.X, padx=5, pady=5)

        # 底部状态栏
        self.status_var = tk.StringVar(value="✨ 欢迎使用旁听速记员")
        status_bar = tk.Label(self.root, textvariable=self.status_var, bd=1, relief=tk.FLAT, 
                              anchor=tk.W, bg="#dfe4ea", font=("微软雅黑", 9))
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def toggle_always_on_top(self):
        self.root.attributes("-topmost", self.is_always_on_top.get())

    def toggle_compact_mode(self):
        """在正常模式和紧凑模式之间切换"""
        if self.is_compact_mode.get():
            # 切换到紧凑模式
            self.root.geometry("400x600")
            # 隐藏一些非核心UI
            self.dialog_text.pack_forget()
            # 只保留摘要列表，占据主要空间
            self.summary_listbox.master.pack_forget() # 整个list_frame
            self.summary_listbox.master.master.pack_forget() # right_frame
            
            # 重新组织：顶部摘要，底部小文本框
            self.right_frame.pack(fill=tk.BOTH, expand=True)
            self.left_frame.pack_forget()
        else:
            # 还原到正常模式
            self.root.geometry("1100x750")
            self.right_frame.pack_forget()
            self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
            self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False)
            self.dialog_text.pack(fill=tk.BOTH, expand=True)

    def change_opacity(self, value):
        self.root.attributes("-alpha", float(value))

    def show_context_menu(self, event):
        self.context_menu.post(event.x_root, event.y_root)

    def add_selection_as_summary(self):
        try:
            selection = self.dialog_text.get(tk.SEL_FIRST, tk.SEL_LAST).strip()
            if selection:
                # 预填充到摘要输入框
                self.summary_entry.delete(0, tk.END)
                self.summary_entry.insert(0, selection[:50] + ("..." if len(selection) > 50 else ""))
                self.add_summary_from_entry()
        except tk.TclError:
            messagebox.showwarning("提示", "请先在文本中选择一段文字作为摘要内容")

    def check_clipboard(self):
        """轮询剪贴板 (每1秒)"""
        if self.is_scribe_mode.get():
            try:
                # 获取剪贴板内容
                content = self.root.clipboard_get()
                if content != self.last_clipboard_content and content.strip():
                    self.last_clipboard_content = content
                    self.auto_append_content(content)
            except Exception:
                # 剪贴板为空或获取失败时忽略
                pass
        self.root.after(1000, self.check_clipboard)

    def auto_append_content(self, content):
        """自动追加内容到对话框"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.dialog_text.insert(tk.END, f"\n--- [{timestamp}] 捕获自剪贴板 ---\n", "timestamp")
        self.dialog_text.insert(tk.END, content + "\n")
        self.dialog_text.see(tk.END)
        self.status_var.set(f"✅ 已捕获新片段 ({timestamp})")
        # 自动保存
        self.save_current_conversation(silent=True)

    def new_conversation(self):
        """创建新的对话主题"""
        # 弹出简单对话框
        title_window = tk.Toplevel(self.root)
        title_window.title("新建主题")
        title_window.geometry("350x150")
        title_window.transient(self.root)
        
        tk.Label(title_window, text="请输入对话主题名称:", font=self.font_main).pack(pady=10)
        entry = tk.Entry(title_window, font=self.font_main, width=30)
        entry.pack(pady=5)
        entry.focus_set()
        
        def confirm():
            title = entry.get().strip() or f"未命名对话 {len(self.conversations)+1}"
            new_conv = {
                'id': len(self.conversations),
                'title': title,
                'content': "",
                'summaries': [],
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.conversations.append(new_conv)
            self.current_conversation_id = new_conv['id']
            self.dialog_text.delete("1.0", tk.END)
            self.update_summary_list()
            self.status_var.set(f"📂 当前主题: {title}")
            title_window.destroy()
            
        tk.Button(title_window, text="确定创建", command=confirm, bg="#2ecc71", fg="white").pack(pady=10)

    def save_current_conversation(self, silent=False):
        """保存当前对话"""
        content = self.dialog_text.get("1.0", tk.END).strip()
        if self.current_conversation_id is not None:
            for conv in self.conversations:
                if conv['id'] == self.current_conversation_id:
                    conv['content'] = content
                    break
        elif content:
            # 自动创建新对话
            new_conv = {
                'id': len(self.conversations),
                'title': f"自动保存 {datetime.now().strftime('%H%M%S')}",
                'content': content,
                'summaries': [],
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.conversations.append(new_conv)
            self.current_conversation_id = new_conv['id']
        
        self.save_data()
        if not silent:
            messagebox.showinfo("成功", "对话内容已成功持久化")

    def add_summary(self):
        """将当前对话框的最后一部分内容标记为摘要"""
        # 简单弹窗询问摘要名称
        self.add_summary_from_entry()   

    def add_summary_from_entry(self):
        """记录当前光标位置作为锚点并添加摘要"""
        summary_text = self.summary_entry.get().strip()
        if not summary_text:
            messagebox.showwarning("提示", "请输入摘要描述文字")
            return
            
        if self.current_conversation_id is None:
            messagebox.showwarning("提示", "请先创建或选择一个对话主题")
            return

        # 获取当前插入光标的位置
        current_pos = self.dialog_text.index(tk.INSERT)
        
        for conv in self.conversations:
            if conv['id'] == self.current_conversation_id:
                timestamp = datetime.now().strftime("%H:%M:%S")
                conv['summaries'].append({
                    'text': summary_text,
                    'timestamp': timestamp,
                    'pos': current_pos
                })
                break
        
        self.summary_entry.delete(0, tk.END)
        self.update_summary_list()
        self.save_data()
        self.status_var.set(f"📍 已添加锚点: {summary_text}")

    def update_summary_list(self):
        """刷新右侧列表"""
        self.summary_listbox.delete(0, tk.END)
        for conv in self.conversations:
            self.summary_listbox.insert(tk.END, f"📁 {conv['title']}")
            for s in conv['summaries']:
                self.summary_listbox.insert(tk.END, f"  └─ 📍 [{s['timestamp']}] {s['text']}")

    def jump_to_conversation(self, event):
        """处理列表双击，实现跳转与高亮"""
        selection = self.summary_listbox.curselection()
        if not selection: return
        
        idx = selection[0]
        item_text = self.summary_listbox.get(idx)
        
        target_conv = None
        target_summary = None
        
        # 溯源对话主题
        search_idx = idx
        while search_idx >= 0:
            text = self.summary_listbox.get(search_idx)
            if text.startswith("📁 "):
                title = text[2:]
                for conv in self.conversations:
                    if conv['title'] == title:
                        target_conv = conv
                        break
                break
            search_idx -= 1
            
        if target_conv:
            # 加载对话内容
            self.current_conversation_id = target_conv['id']
            self.dialog_text.delete("1.0", tk.END)
            self.dialog_text.insert("1.0", target_conv['content'])
            
            # 如果是点击摘要，则跳转
            if "📍" in item_text:
                # 解析出摘要文本
                try:
                    summary_content = item_text.split("] ")[1]
                    for s in target_conv['summaries']:
                        if s['text'] == summary_content:
                            target_summary = s
                            break
                    
                    if target_summary:
                        pos = target_summary['pos']
                        self.dialog_text.tag_remove("highlight", "1.0", tk.END)
                        self.dialog_text.see(pos)
                        # 高亮对应行
                        line_num = pos.split('.')[0]
                        self.dialog_text.tag_add("highlight", f"{line_num}.0", f"{line_num}.end")
                except:
                    pass
            
            self.status_var.set(f"📖 正在查看: {target_conv['title']}")

    def delete_selected(self):
        """删除选中项"""
        selection = self.summary_listbox.curselection()
        if not selection: return
        
        idx = selection[0]
        item_text = self.summary_listbox.get(idx)
        
        if messagebox.askyesno("确认", f"确定要删除选中的项吗？"):
            if item_text.startswith("📁 "):
                # 删除整个主题
                title = item_text[2:]
                self.conversations = [c for c in self.conversations if c['title'] != title]
                if self.current_conversation_id is not None:
                    # 检查当前ID是否还存在
                    ids = [c['id'] for c in self.conversations]
                    if self.current_conversation_id not in ids:
                        self.current_conversation_id = None
                        self.dialog_text.delete("1.0", tk.END)
            else:
                # 删除单个摘要
                # 先找所属主题
                search_idx = idx - 1
                while search_idx >= 0:
                    text = self.summary_listbox.get(search_idx)
                    if text.startswith("📁 "):
                        title = text[2:]
                        for conv in self.conversations:
                            if conv['title'] == title:
                                summary_name = item_text.split("] ")[1]
                                conv['summaries'] = [s for s in conv['summaries'] if s['text'] != summary_name]
                                break
                        break
                    search_idx -= 1
            
            self.update_summary_list()
            self.save_data()

    def clear_dialog(self):
        if messagebox.askyesno("确认", "确定要清空当前的实时记录吗？(不会删除已保存的数据)"):
            self.dialog_text.delete("1.0", tk.END)

    def save_data(self):
        try:
            with open("llm_conversations.json", "w", encoding="utf-8") as f:
                json.dump(self.conversations, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.status_var.set(f"❌ 保存失败: {str(e)}")

    def load_data(self):
        if os.path.exists("llm_conversations.json"):
            try:
                with open("llm_conversations.json", "r", encoding="utf-8") as f:
                    self.conversations = json.load(f)
                if self.conversations:
                    # 默认加载最后一个
                    last_conv = self.conversations[-1]
                    self.current_conversation_id = last_conv['id']
                    self.dialog_text.insert("1.0", last_conv['content'])
                    self.update_summary_list()
                    self.status_var.set(f"📁 已加载 {len(self.conversations)} 条历史对话")
            except:
                self.status_var.set("⚠️ 历史数据读取异常")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = LLMConversationManager()
    app.run()
