# infer_utils.py
import os
from docx import Document
from openai import OpenAI
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from dotenv import load_dotenv
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_sections(docx_file):
    """②, ④ 항목 텍스트 추출"""
    doc = Document(docx_file)
    text = "\n".join([p.text.strip() for p in doc.paragraphs])
    part_2 = text.split("②")[1].split("③")[0].strip() if "③" in text else ""
    part_4 = text.split("④")[1].split("⑤")[0].strip() if "⑤" in text else ""
    return part_2, part_4

def generate_correction(model_name, poor_text):
    """GPT로 교정된 결과 생성"""
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": "너는 행정문서 교정 전문가이다."},
            {"role": "user", "content": poor_text}
        ]
    )
    return response.choices[0].message.content

def export_pdf(text, output_path):
    """교정 결과를 PDF로 저장"""
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(output_path)
    story = []
    for part in text.split("\n\n"):
        story.append(Paragraph(part, styles["BodyText"]))
        story.append(Spacer(1, 12))
    doc.build(story)
    return output_path
