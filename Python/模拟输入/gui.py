import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from pynput.keyboard import Controller, Key


class AutoTyperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("自动模拟输入工具")
        self.root.geometry("600x500")
        self.root.resizable(True, True)

        # 初始化键盘控制器
        self.keyboard = Controller()

        # 控制变量
        self.is_typing = False
        self.typing_thread = None

        # 文件路径
        self.file_path = ""

        # 创建界面
        self.create_widgets()

    def create_widgets(self):
        # 文件选择区域
        file_frame = tk.LabelFrame(self.root, text="文件选择", padx=10, pady=10)
        file_frame.pack(fill="x", padx=10, pady=5)

        self.file_label = tk.Label(file_frame, text="未选择文件", fg="gray", anchor="w")
        self.file_label.pack(side="left", fill="x", expand=True)

        btn_select = tk.Button(file_frame, text="选择文本文件", command=self.select_file, bg="#4CAF50", fg="white")
        btn_select.pack(side="right", padx=(10, 0))

        # 文件内容预览
        preview_frame = tk.LabelFrame(self.root, text="文件内容预览", padx=10, pady=10)
        preview_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.preview_text = scrolledtext.ScrolledText(preview_frame, height=10, wrap=tk.WORD)
        self.preview_text.pack(fill="both", expand=True)

        # 参数设置
        settings_frame = tk.LabelFrame(self.root, text="输入设置", padx=10, pady=10)
        settings_frame.pack(fill="x", padx=10, pady=5)

        # 延迟设置
        delay_row = tk.Frame(settings_frame)
        delay_row.pack(fill="x", pady=5)

        tk.Label(delay_row, text="字符间隔 (秒):").pack(side="left")
        self.delay_var = tk.DoubleVar(value=0.05)
        delay_scale = tk.Scale(delay_row, from_=0.01, to=0.5, resolution=0.01,
                               orient="horizontal", variable=self.delay_var, length=200)
        delay_scale.pack(side="left", padx=(10, 0))
        self.delay_label = tk.Label(delay_row, text="0.05 秒")
        self.delay_label.pack(side="left", padx=(10, 0))

        # 延迟实时显示
        def update_delay_label(*args):
            self.delay_label.config(text=f"{self.delay_var.get():.2f} 秒")

        self.delay_var.trace_add("write", update_delay_label)

        # 启动延迟设置
        start_row = tk.Frame(settings_frame)
        start_row.pack(fill="x", pady=5)

        tk.Label(start_row, text="启动倒计时 (秒):").pack(side="left")
        self.countdown_var = tk.IntVar(value=5)
        countdown_spin = tk.Spinbox(start_row, from_=1, to=10, textvariable=self.countdown_var, width=10)
        countdown_spin.pack(side="left", padx=(10, 0))

        # 控制按钮
        control_frame = tk.Frame(self.root)
        control_frame.pack(fill="x", padx=10, pady=10)

        self.btn_start = tk.Button(control_frame, text="开始输入", command=self.start_typing,
                                   bg="#2196F3", fg="white", font=("Arial", 12, "bold"))
        self.btn_start.pack(side="left", expand=True, fill="x", padx=5)

        self.btn_stop = tk.Button(control_frame, text="停止输入", command=self.stop_typing,
                                  bg="#f44336", fg="white", font=("Arial", 12, "bold"), state="disabled")
        self.btn_stop.pack(side="left", expand=True, fill="x", padx=5)

        # 状态栏
        self.status_var = tk.StringVar(value="就绪 | 请选择文本文件")
        status_bar = tk.Label(self.root, textvariable=self.status_var, relief="sunken", anchor="w")
        status_bar.pack(side="bottom", fill="x")

        # 提示标签
        tip_label = tk.Label(self.root, text="提示：开始输入后，请立即点击目标窗口（记事本、聊天框等）",
                             fg="orange", font=("Arial", 9))
        tip_label.pack(side="bottom", pady=5)

    def select_file(self):
        """选择文本文件"""
        file_path = filedialog.askopenfilename(
            title="选择文本文件",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )

        if file_path:
            self.file_path = file_path
            self.file_label.config(text=file_path, fg="black")

            # 显示文件内容预览
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.preview_text.delete(1.0, tk.END)
                    # 限制预览长度
                    if len(content) > 2000:
                        content = content[:2000] + "\n\n... (文件内容过长，仅显示前2000字符)"
                    self.preview_text.insert(1.0, content)
                self.status_var.set(f"就绪 | 已加载: {file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"读取文件失败: {e}")
                self.status_var.set("错误 | 文件读取失败")

    def countdown(self, seconds):
        """倒计时"""
        for i in range(seconds, 0, -1):
            if not self.is_typing:
                return False
            self.status_var.set(f"倒计时 {i} 秒... 请将光标置于目标窗口")
            time.sleep(1)
        return True

    def type_file_content(self):
        """执行输入（在单独线程中运行）"""
        try:
            # 读取文件
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 倒计时
            if not self.countdown(self.countdown_var.get()):
                return

            if not self.is_typing:
                return

            self.status_var.set("正在输入...")

            # 逐字符输入
            delay = self.delay_var.get()
            for i, char in enumerate(content):
                if not self.is_typing:
                    self.status_var.set("输入已停止")
                    return

                if char == '\n':
                    self.keyboard.press(Key.enter)
                    self.keyboard.release(Key.enter)
                elif char == '\t':
                    self.keyboard.press(Key.tab)
                    self.keyboard.release(Key.tab)
                else:
                    self.keyboard.type(char)

                # 更新进度（每100个字符更新一次，避免界面卡顿）
                if i % 100 == 0:
                    progress = (i + 1) / len(content) * 100
                    self.status_var.set(f"正在输入... {progress:.1f}% ({i + 1}/{len(content)})")

                time.sleep(delay)

            if self.is_typing:
                self.status_var.set("输入完成！")
                messagebox.showinfo("完成", "文件输入已完成")

        except Exception as e:
            self.status_var.set(f"错误: {str(e)}")
            messagebox.showerror("输入错误", f"输入过程中出错: {e}")
        finally:
            self.stop_typing()

    def start_typing(self):
        """开始输入"""
        if not self.file_path:
            messagebox.showwarning("警告", "请先选择文本文件")
            return

        if self.is_typing:
            return

        # 清空预览文本的选中状态
        self.preview_text.tag_remove("sel", "1.0", tk.END)

        self.is_typing = True
        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")

        # 在新线程中执行输入，避免阻塞GUI
        self.typing_thread = threading.Thread(target=self.type_file_content, daemon=True)
        self.typing_thread.start()

    def stop_typing(self):
        """停止输入"""
        self.is_typing = False
        self.btn_start.config(state="normal")
        self.btn_stop.config(state="disabled")

        if self.status_var.get() == "正在输入...":
            self.status_var.set("用户已停止输入")


def main():
    root = tk.Tk()
    app = AutoTyperGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()