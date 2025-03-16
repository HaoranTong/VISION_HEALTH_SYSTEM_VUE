import requests
import pyreadline3 as readline  # 支持终端历史记录（Windows 兼容）

API_URL = "https://api.siliconflow.cn/v1"
API_KEY = "sk-sygdtrlrvnbzmxqrmkdtxbuhhmiosmjjmixwyyecudsdgfxu"  # 替换为你的Key


def chat_with_deepseek():
    headers = {"Authorization": f"Bearer {API_KEY}"}
    print("DeepSeek-R1 终端对话已启动（输入exit退出）...")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break
        data = {
            "model": "deepseek-r1",
            "messages": [{"role": "user", "content": user_input}]
        }
        try:
            response = requests.post(API_URL, headers=headers, json=data)
            response.raise_for_status()  # 检查请求是否成功
            reply = response.json()['choices'][0]['message']['content']
            print(f"AI: {reply}\n")
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
        except KeyError:
            print("API 返回格式错误，无法解析回复。")


if __name__ == "__main__":
    chat_with_deepseek()
