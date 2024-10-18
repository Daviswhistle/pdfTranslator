import pdfplumber

def extract_pdf_elements(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        elements = []
        page_sizes = []
        for page in pdf.pages:
            text = page.extract_text()
            words = page.extract_words()
            images = []
            for img in page.images:
                image = page.crop((img['x0'], img['top'], img['x1'], img['bottom'])).to_image(resolution=150)
                image_bytes = image.original.bytes
                img['image_bytes'] = image_bytes
                images.append(img)
            tables = page.extract_tables()
            width = page.width
            height = page.height
            elements.append({
                'text': text,
                'words': words,
                'images': images,
                'tables': tables,
                'layout': page.objects
            })
            page_sizes.append((width, height))
        return elements, page_sizes
