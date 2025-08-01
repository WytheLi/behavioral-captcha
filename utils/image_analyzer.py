from openai import OpenAI

from config import config
from utils.image_process import image_to_base64


class MultiImageAnalyzer:
    """多图片分析工具类"""

    def __init__(self, api_key: str):
        """
        初始化分析器

        :param api_key: 阿里云DashScope API密钥
        """
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        self.image_desc = []

    def describe_image(self, image_path: str, question: str = "图中描绘的是什么?", model="qwen-vl-max-latest"):
        """
        分析单张图片并生成描述
        https://help.aliyun.com/zh/model-studio/vision

        :param image_path: 图片路径
        :param question: 分析问题
        :param model: 视觉-语言多模态模型
        :return:
        """
        image_base64 = image_to_base64(image_path)

        messages = [
            {
                "role": "system",
                "content": [{"type": "text", "text": "你是一个专业的图像分析助手，请准确描述图片内容。"}],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_base64
                        },
                    },
                    {"type": "text", "text": question},
                ],
            },
        ]

        completion = self.client.chat.completions.create(
            model=model,
            # 此处以qwen-vl-max-latest为例，可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/models
            messages=messages,
        )
        if completion.choices and completion.choices[0].message.content:
            result = completion.choices[0].message.content
            # 存储描述结果
            self.image_desc.append(result)
            return result

    def solve_question_with_desc(self, question: str, model="qwen-max"):
        """
        基于图片描述信息，回答综合问题

        :param question:
        :param model: 纯文本大语言模型
        :return:
        """
        # 构建比较请求
        messages = [
            {
                "role": "system",
                "content": [{"type": "text", "text": "你是一个专业的分析助手，需要基于多张图片的描述进行比较分析。"}],
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"以下是多张图片的分析描述，请根据这些描述回答（结果只输出符合条件的图片编号，用逗号分隔，例如图片1、图片2符合要求，输出：'1,2'；如果没有符合条件的图片，输出'0'。不要添加任何额外解释。）：{question}\n\n"}
                ],
            }
        ]

        # 添加所有图片描述
        for i, desc in enumerate(self.image_desc):
            messages[1]["content"].append({
                "type": "text",
                "text": f"图片{i + 1}描述: {desc}\n"
            })

        try:
            completion = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=800,
                temperature=0.3,
            )

            if completion.choices and completion.choices[0].message.content:
                return completion.choices[0].message.content
            print("比较分析未收到有效响应")

        except Exception as e:
            print(f"比较分析失败: {str(e)}")


if __name__ == '__main__':
    analyzer = MultiImageAnalyzer(config.DASHSCOPE_API_KEY)

    for i in range(1, 10):
        row = (i - 1) // 3
        col = (i - 1) % 3
        analyzer.describe_image(f"utils/9grid_output/grid_{row}{col}.jpg")

    result = analyzer.solve_question_with_desc("哪些事物或者动物能在公园里看到")
    print(f"分析结果：{result}")
