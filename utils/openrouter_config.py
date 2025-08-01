import os
import time
from google import genai
from volcenginesdkarkruntime import Ark
from dotenv import load_dotenv
from dataclasses import dataclass
import backoff
from src.utils.logging_config import setup_logger, SUCCESS_ICON, ERROR_ICON, WAIT_ICON

# 设置日志记录
logger = setup_logger('api_calls')


@dataclass
class ChatMessage:
    content: str


@dataclass
class ChatChoice:
    message: ChatMessage


@dataclass
class ChatCompletion:
    choices: list[ChatChoice]


# 获取项目根目录
project_root = os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))
env_path = os.path.join(project_root, '.env')

# 加载环境变量
if os.path.exists(env_path):
    load_dotenv(env_path, override=True)
    logger.info(f"{SUCCESS_ICON} 已加载环境变量: {env_path}")
else:
    logger.warning(f"{ERROR_ICON} 未找到环境变量文件: {env_path}")

# 验证环境变量
api_key = os.getenv("GEMINI_API_KEY")
model = os.getenv("GEMINI_MODEL")

api_key = os.getenv("DOUBAO_API_KEY")
model = os.getenv("DOUBAO_MODEL")

if not api_key:
    logger.error(f"{ERROR_ICON} 未找到 GEMINI_API_KEY 环境变量")
    raise ValueError("GEMINI_API_KEY not found in environment variables")
if not model:
    model = "gemini-1.5-flash"
    logger.info(f"{WAIT_ICON} 使用默认模型: {model}")

# 初始化 Gemini 客户端
# client = genai.Client(api_key=api_key)
# logger.info(f"{SUCCESS_ICON} Gemini 客户端初始化成功")

# 初始化 豆包 客户端
client = Ark(api_key=api_key)
logger.info(f"{SUCCESS_ICON} Doubao 客户端初始化成功")

@backoff.on_exception(
    backoff.expo,
    (Exception),
    max_tries=5,
    max_time=300,
    giveup=lambda e: "AFC is enabled" not in str(e)
)
def generate_content_with_retry(model, contents, config=None):
    """带重试机制的内容生成函数"""
    try:
        logger.info(f"{WAIT_ICON} 正在调用 Gemini API...")
        logger.debug(f"请求内容: {contents}")
        logger.debug(f"请求配置: {config}")

        # # google获取回复
        # response = client.models.generate_content(
        #     model=model,
        #     contents=contents,
        #     config=config
        # )
        # print(contents)
        # 豆包获取响应
        response = client.chat.completions.create(
            model=model,
            messages=contents
        )

        logger.info(f"{SUCCESS_ICON} API 调用成功")
        # logger.debug(f"响应内容: {response.text[:500]}...")
        logger.debug(f"响应内容: {response.choices[0].message.content[:500]}")
        return response
    except Exception as e:
        if "AFC is enabled" in str(e):
            logger.warning(f"{ERROR_ICON} 触发 API 限制，等待重试... 错误: {str(e)}")
            time.sleep(5)
            raise e
        logger.error(f"{ERROR_ICON} API 调用失败: {str(e)}")
        logger.error(f"错误详情: {str(e)}")
        raise e


def get_chat_completion(messages, model=None, max_retries=3, initial_retry_delay=1):
    """获取聊天完成结果，包含重试逻辑"""
    try:
        if model is None:
            # 设置模型
            model = os.getenv("DOUBAO_MODEL", "doubao-1-5-pro-256k-250115")

        logger.info(f"{WAIT_ICON} 使用模型: {model}")
        logger.debug(f"消息内容: {messages}")

        for attempt in range(max_retries):
            try:
                # # 转换Google消息格式
                # prompt = ""
                # system_instruction = None

                # for message in messages:
                #     role = message["role"]
                #     content = message["content"]
                #     if role == "system":
                #         system_instruction = content
                #     elif role == "user":
                #         prompt += f"User: {content}\n"
                #     elif role == "assistant":
                #         prompt += f"Assistant: {content}\n"

                # # 准备配置
                # config = {}
                # if system_instruction:
                #     config['system_instruction'] = system_instruction

                # 调用 API
                response = generate_content_with_retry(
                    model=model,
                    contents=messages,
                    # config=config
                )

                if response is None:
                    logger.warning(
                        f"{ERROR_ICON} 尝试 {attempt + 1}/{max_retries}: API 返回空值")
                    if attempt < max_retries - 1:
                        retry_delay = initial_retry_delay * (2 ** attempt)
                        logger.info(f"{WAIT_ICON} 等待 {retry_delay} 秒后重试...")
                        time.sleep(retry_delay)
                        continue
                    return None

                # # 转换Google响应格式
                # chat_message = ChatMessage(content=response.text)
                # chat_choice = ChatChoice(message=chat_message)
                # completion = ChatCompletion(choices=[chat_choice])
                
                chat_message = ChatMessage(content=response.choices[0].message.content)
                chat_choice = ChatChoice(message=chat_message)
                completion = ChatCompletion(choices=[chat_choice])

                # logger.debug(f"API 原始响应: {response.text}")
                logger.debug(f"API 原始响应: {response.choices[0].message}")
                logger.info(f"{SUCCESS_ICON} 成功获取响应")
                return completion.choices[0].message.content

            except Exception as e:
                logger.error(
                    f"{ERROR_ICON} 尝试 {attempt + 1}/{max_retries} 失败: {str(e)}")
                if attempt < max_retries - 1:
                    retry_delay = initial_retry_delay * (2 ** attempt)
                    logger.info(f"{WAIT_ICON} 等待 {retry_delay} 秒后重试...")
                    time.sleep(retry_delay)
                else:
                    logger.error(f"{ERROR_ICON} 最终错误: {str(e)}")
                    return None

    except Exception as e:
        logger.error(f"{ERROR_ICON} get_chat_completion 发生错误: {str(e)}")
        return None
