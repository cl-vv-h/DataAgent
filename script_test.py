import os
import json

input_dir = "res"

for filename in os.listdir(input_dir):
    if filename.endswith(".json"):
        file_path = os.path.join(input_dir, filename)

        try:
            # 读取原文件
            with open(file_path, "r", encoding="utf-8") as f:
                raw_content = f.read().strip()

            # 第一次反序列化：去掉外层字符串
            inner_json_str = json.loads(raw_content)

            # 第二次反序列化：把里面的 Unicode 转成正常中文
            if isinstance(inner_json_str, str):
                data = json.loads(inner_json_str)
            else:
                data = inner_json_str

            # 重新保存为缩进规整的 JSON
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

            print(f"✅ 格式化完成: {filename}")

        except Exception as e:
            print(f"❌ 处理失败 {filename}: {e}")