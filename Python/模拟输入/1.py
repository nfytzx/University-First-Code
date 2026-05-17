import time
from pynput.keyboard import Controller, Key


def type_file_content(file_path, delay=0.05):

    keyboard = Controller()

    # 读取文件内容
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except FileNotFoundError:
        print(f"错误：文件 {file_path} 未找到")
        return
    except Exception as e:
        print(f"读取文件时出错：{e}")
        return

    
    print("5秒后将开始输入，请将光标置于目标输入框...")
    time.sleep(5)

    # 逐字符输入
    for char in content:
        if char == '\n':
            # 回车键
            keyboard.press(Key.enter)
            keyboard.release(Key.enter)
        elif char == '\t':
            # 制表符
            keyboard.press(Key.tab)
            keyboard.release(Key.tab)
        else:
            # 普通字符
            keyboard.type(char)  # type 方法直接输入字符
            # 或者使用更底层的 press/release：
            # keyboard.press(char)
            # keyboard.release(char)

        # 模拟人类打字间隔
        time.sleep(delay)


if __name__ == "__main__":
    # 示例：输入同目录下的 example.txt 文件
    type_file_content("example.txt", delay=0.05)