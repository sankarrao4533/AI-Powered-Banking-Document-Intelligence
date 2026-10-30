import sys
from pathlib import Path
import docx

sys.stdout.reconfigure(encoding='utf-8')

PROJECT_ROOT = Path(__file__).resolve().parent.parent if Path(__file__).resolve().parent.name == "scripts" else Path(__file__).resolve().parent
docx_path = PROJECT_ROOT / "docs" / "AI_Powered_Banking_Document_Intelligence_Report.docx"
if not docx_path.exists():
    docx_path = PROJECT_ROOT / "AI_Powered_Banking_Document_Intelligence_Report.docx"

doc = docx.Document(str(docx_path))
print(f"Total Paragraphs: {len(doc.paragraphs)}")
print(f"Total Tables: {len(doc.tables)}")

for i, t in enumerate(doc.tables):
    header = [c.text.strip().replace('\n', ' ')[:40] for c in t.rows[0].cells]
    print(f"Table {i+1:02d} ({len(t.rows)}x{len(t.columns)}): {header}")

headings = [p.text for p in doc.paragraphs if p.text.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.', '11.', '12.', '13.', '14.', '15.', '16.', '17.', '18.', 'Team', 'Project', 'Objectives', 'Expected', 'Problem', 'Final'))]
print(f"\nHeadings detected ({len(headings)}):")
for h in headings:
    print(f"  - {h}")
