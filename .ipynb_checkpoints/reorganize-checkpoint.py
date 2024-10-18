from reportlab.lib.units import inch
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Image as ReportLabImage
from reportlab.platypus import NextPageTemplate, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus.flowables import Spacer
import io

# 폰트 등록
pdfmetrics.registerFont(TTFont('KoreanFont', 'HakgyoansimSantteutdotumM.ttf'))

def create_translated_pdf(processed_elements, output_path, page_sizes):
    # 페이지 템플릿 생성
    page_templates = []
    for i, (page_width, page_height) in enumerate(page_sizes):
        frame = Frame(0, 0, page_width, page_height, leftPadding=0, bottomPadding=0, rightPadding=0, topPadding=0)
        page_template = PageTemplate(id=f'page_{i}', frames=[frame], pagesize=(page_width, page_height))
        page_templates.append(page_template)

    # 문서 생성
    doc = BaseDocTemplate(output_path, pageTemplates=page_templates)

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Korean', fontName='KoreanFont', fontSize=12))

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

        # 이미지 추가를 위한 Canvas 사용
        def draw_page(canvas, doc):
            # 페이지 크기 설정
            canvas.setPageSize(page_sizes[page_num])

            # 이미지 추가
            for img_dict in page_elements['images']:
                image_data = img_dict.get('image')
                if image_data:
                    img_temp = io.BytesIO(image_data)
                    x0 = img_dict['x0']
                    y0 = img_dict['top']
                    img_width = img_dict['width']
                    img_height = img_dict['height']
                    x = x0
                    y = page_sizes[page_num][1] - y0 - img_height  # 좌표 변환
                    image = Image.open(img_temp)
                    canvas.drawInlineImage(image, x, y, width=img_width, height=img_height)

        # 표 추가 (필요 시)
        # 표 처리 로직을 여기에 추가하세요

        # 문서 빌드
        doc.build(
            story,
            onFirstPage=draw_page,
            onLaterPages=draw_page
        )
        # 다음 페이지를 위해 스토리 초기화
        story = []

    print(f"번역된 PDF가 {output_path}로 저장되었습니다.")
