import os
from dotenv import load_dotenv
from utils.logging_config import setup_logger, SUCCESS_ICON, ERROR_ICON, WAIT_ICON
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import time

load_dotenv(override=True)
logger = setup_logger(',LLM_calls')

api_key = os.getenv("DOUBAO_API_KEY")
model = os.getenv("DOUBAO_MODEL", "doubao-1-5-pro-32k-250115")

doubao_llm = ChatOpenAI(
    model=os.getenv("DOUBAO_MODEL", "doubao-1-5-pro-32k-250115"),
    openai_api_key=os.getenv("DOUBAO_API_KEY"),
    openai_api_base=os.getenv("DOUBAO_API_BASE", "https://ark.cn-beijing.volces.com/api/v3"),
    temperature=0.7,
    max_tokens=4096,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0,
    stop=None,
    timeout=10,
)

def get_chat_completion(messages, model=None, max_retries=3, initial_retry_delay=1):
    model_name = model or os.getenv("DOUBAO_MODEL", "doubao-1-5-pro-256k-250115")
    logger.info(f"{WAIT_ICON} 使用模型: {model_name}")

    # 初始化 ChatOpenAI，保持与原函数参数一致
    llm = ChatOpenAI(
        model=model_name,
        temperature=0,
        max_retries=0  # 自己实现重试逻辑
    )

    # 将通用 message dict 转换成 LangChain 格式
    lc_msgs = []
    for m in messages:
        role = m.get("role")
        content = m.get("content", "")
        if role == "system":
            lc_msgs.append(SystemMessage(content=content))
        else:
            lc_msgs.append(HumanMessage(content=content))

    for attempt in range(max_retries):
        try:
            resp = llm.invoke(lc_msgs)
            text = resp.content
            logger.debug(f"API 原始响应: {text}")
            logger.info(f"{SUCCESS_ICON} 成功获取响应")
            return text
        except Exception as e:
            logger.error(f"{ERROR_ICON} 尝试 {attempt+1}/{max_retries} 失败: {e}")
            if attempt < max_retries - 1:
                delay = initial_retry_delay * (2 ** attempt)
                logger.info(f"{WAIT_ICON} 等待 {delay} 秒后重试...")
                time.sleep(delay)
            else:
                logger.error(f"{ERROR_ICON} 最终错误: {e}")
                return None