import sys
from pathlib import Path

try:
    from pypdf import PdfReader
except Exception as e:
    print('pypdf not available:', e)
    sys.exit(2)

if len(sys.argv) < 3:
    print('Usage: python extract_pdf.py <pdf_path> <out_txt>')
    sys.exit(1)

pdf_path = Path(sys.argv[1])
out_path = Path(sys.argv[2])

if not pdf_path.exists():
    print('PDF not found:', pdf_path)
    sys.exit(1)

reader = PdfReader(str(pdf_path))
text = []
for page in reader.pages:
    try:
        text.append(page.extract_text() or '')
    except Exception as e:
        text.append(f'<!-- page extract error: {e} -->')

out_path.write_text('\n\n'.join(text), encoding='utf-8')
print('Wrote', out_path)
