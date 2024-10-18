# reorganize.py

from reportlab.lib.units import inch
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Image as ReportLabImage, Table, TableStyle, NextPageTemplate, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from processing import translate_table
from PIL import Image
import io

# 폰트 등록
pdfmetrics.registerFont(TTFont('KoreanFont', 'HakgyoansimSantteutdotumM.ttf'))

def create_translated_pdf(processed_elements, output_path, page_sizes, target_language='ko'):
    # 스타일 설정
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Korean', fontName='KoreanFont', fontSize=12))

    # 문서 생성
    doc = BaseDocTemplate(output_path)

    # 페이지 템플릿 생성 및 추가
    page_templates = []
    for i, (page_width, page_height) in enumerate(page_sizes):
        frame = Frame(0, 0, page_width, page_height, leftPadding=0, bottomPadding=0, rightPadding=0, topPadding=0)
        
        # 이미지와 기타 요소들을 그리기 위한 함수 정의
        def draw_page(canvas, doc, page_num=i):
            page_elements = processed_elements[page_num]

            # 이미지 추가
            for img_dict in page_elements['images']:
                image_data = img_dict.get('image')
                if image_data:
                    img_temp = io.BytesIO(image_data)
                    x0 = img_dict['x0']
                    y0 = img_dict['top']
                    img_width = img_dict['x1'] - img_dict['x0']
                    img_height = img_dict['bottom'] - img_dict['top']
                    x = x0
                    y = page_sizes[page_num][1] - y0 - img_height  # 좌표 변환
                    image = Image.open(img_temp)
                    canvas.drawInlineImage(image, x, y, width=img_width, height=img_height)
        
        page_template = PageTemplate(id=f'page_{i}', frames=[frame], pagesize=(page_width, page_height), onPage=draw_page)
        page_templates.append(page_template)

    doc.addPageTemplates(page_templates)

    story = []

    for page_num, page_elements in enumerate(processed_elements):
        # 다음 페이지 템플릿 설정
        story.append(NextPageTemplate(f'page_{page_num}'))

        # 페이지 구분 (첫 페이지 제외)
        if page_num != 0:
            story.append(PageBreak())

        # 번역된 텍스트 추가
        translated_text = page_elements['translated_text']
        if translated_text:
            para = Paragraph(translated_text, styles['Korean'])
            story.append(para)

        # 표 추가
        for table_data in page_elements['tables']:
            # 표 데이터 번역
            translated_table_data = translate_table(table_data, target_language)
            # Table 객체 생성
            table = Table(translated_table_data)
            # 표 스타일 설정
            table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                # 필요한 스타일 추가
            ]))
            story.append(table)

    # 문서 빌드
    doc.build(story)

    print(f"번역된 PDF가 {output_path}로 저장되었습니다.")
