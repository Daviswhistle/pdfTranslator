from dotenv import load_dotenv
import openai
import pytesseract
from PIL import Image
import io
import os

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

import os
from openai import OpenAI

client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "system",
            "content": f"Translate the following text to {target_language}. Since we provide PDF file translation services, you must translate without missing a single word, and do not arbitrarily perform changes such as summaries.",
        },
    ],
    model="gpt-4o",
)

def translate_text(text, target_language='ko'):
    try:
        response = openai.ChatCompletion.create(
            model='gpt-4o',
            messages=[
                {"role": "system", "content": f"Translate the following text to {target_language}. Since we provide PDF file translation services, you must translate without missing a single word, and do not arbitrarily perform changes such as summaries."},
                {"role": "user", "content": text}
            ]
        )
        translated_text = response['choices'][0]['message']['content'].strip()
        return translated_text
    except Exception as e:
        print(f"번역 중 오류 발생: {e}")
        return ""

def insert_translated_text_into_image(image, translated_text):
    draw = ImageDraw.Draw(image)
    font_size = 12
    font = ImageFont.truetype('HakgyoansimSantteutdotumM.ttf', font_size)
    max_width = image.width - 20  # 이미지의 양쪽 여백을 고려
    lines = []
    words = translated_text.split()
    line = ''
    for word in words:
        test_line = line + word + ' '
        text_width, _ = draw.textsize(test_line, font=font)
        if text_width <= max_width:
            line = test_line
        else:
            lines.append(line)
            line = word + ' '
    lines.append(line)

    y_text = 10  # 이미지의 상단 여백
    for line in lines:
        draw.text((10, y_text), line, font=font, fill=(0, 0, 0))
        y_text += font.getsize(line)[1]
    return image

def ocr_and_translate_image(image_bytes, target_language='ko'):
    try:
        image = Image.open(io.BytesIO(image_bytes))
        extracted_text = pytesseract.image_to_string(image)
        # 텍스트 번역
        translated_text = translate_text(extracted_text, target_language)
        # 번역된 텍스트를 이미지에 삽입
        image_with_text = insert_translated_text_into_image(image, translated_text)
        # 이미지 데이터를 바이트로 변환하여 반환
        img_byte_arr = io.BytesIO()
        image_with_text.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        return img_byte_arr
    except Exception as e:
        print(f"OCR 처리 중 오류 발생: {e}")
        return None

# 예시: 추출한 텍스트 번역 및 이미지 내 텍스트 처리
def process_pdf_elements(pdf_elements, target_language='ko'):
    for page_elements in pdf_elements:
        # 텍스트 번역
        original_text = page_elements['text']
        if original_text:
            translated_text = translate_text(original_text, target_language)
            page_elements['translated_text'] = translated_text
        else:
            page_elements['translated_text'] = ''

        # 이미지 내 텍스트 처리
        for img_dict in page_elements['images']:
            # 이미지 데이터 추출
            image_data = img_dict.get('image_bytes')
            if image_data:
                translated_image_text = ocr_and_translate_image(image_data, target_language)
                img_dict['translated_text'] = translated_image_text
            else:
                img_dict['translated_text'] = ''
    return pdf_elements

# 사용 예시
# 번역할 대상 언어 설정 (예: 한국어 'ko', 영어 'en' 등)
# target_language = 'ko'
# processed_elements = process_pdf_elements(pdf_elements, target_language)


