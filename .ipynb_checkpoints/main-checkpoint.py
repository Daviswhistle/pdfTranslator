# main.py

import sys
from extraction import extract_pdf_elements
from processing import process_pdf_elements
from reorganize import create_translated_pdf

def main():
    # 입력 PDF 경로 확인
    if len(sys.argv) < 2:
        print("사용법: python main.py 입력_PDF_파일_경로")
        sys.exit(1)

    input_pdf_path = sys.argv[1]
    output_pdf_path = 'translated_output.pdf'
    target_language = 'ko'  # 번역할 대상 언어 설정

    # 1단계: PDF 요소 추출
    print("PDF 요소를 추출하는 중...")
    pdf_elements, page_sizes = extract_pdf_elements(input_pdf_path)

    # 2단계: 요소 처리 및 번역
    print("PDF 요소를 처리하고 번역하는 중...")
    processed_elements = process_pdf_elements(pdf_elements, target_language)

    # 3단계: 번역된 PDF 생성
    print("번역된 PDF를 생성하는 중...")
    create_translated_pdf(processed_elements, output_pdf_path, page_sizes)

    print(f"번역된 PDF가 {output_pdf_path}로 저장되었습니다.")

if __name__ == '__main__':
    main()
