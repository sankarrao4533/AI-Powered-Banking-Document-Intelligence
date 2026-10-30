from pathlib import Path
from pptx import Presentation

PROJECT_ROOT = Path(__file__).resolve().parent.parent if Path(__file__).resolve().parent.name == "scripts" else Path(__file__).resolve().parent
deck_path = PROJECT_ROOT / "docs" / "AI_Powered_Banking_Document_Intelligence_Deck.pptx"
if not deck_path.exists():
    deck_path = PROJECT_ROOT / "AI_Powered_Banking_Document_Intelligence_Deck.pptx"

prs = Presentation(str(deck_path))
print(f"Total slides: {len(prs.slides)}")
for idx, s in enumerate(prs.slides, 1):
    texts = [shape.text_frame.text[:40].replace('\n', ' ') for shape in s.shapes if shape.has_text_frame]
    print(f"Slide {idx:02d}: {len(s.shapes)} shapes | {texts[:2]}")
