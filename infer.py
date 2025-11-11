# infer.py
import os
from docx import Document
from openai import OpenAI
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_sections(docx_path):
    doc = Document(docx_path)
    text = "\n".join([p.text.strip() for p in doc.paragraphs])
    part_2 = text.split("②")[1].split("③")[0].strip() if "③" in text else ""
    part_4 = text.split("④")[1].split("⑤")[0].strip() if "⑤" in text else ""
    return part_2, part_4


def generate_correction(model_name, poor_file):
    poor_2, poor_4 = extract_sections(poor_file)
    user_input = f"② 처분의 내용:\n{poor_2}\n\n④ 이의신청의 취지와 사유:\n{poor_4}"

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": "너는 행정문서 교정 전문가이다."},
            {"role": "user", "content": user_input}
        ]
    )

    return response.choices[0].message.content


def export_pdf(text, output_path):
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(output_path)
    story = []

    for part in text.split("\n\n"):
        story.append(Paragraph(part, styles["BodyText"]))
        story.append(Spacer(1, 10))
    doc.build(story)
    print(f"📄 Saved PDF: {output_path}")


if __name__ == "__main__":
    model_name = "ft:gpt-4o-mini:your-org::appeal-correction"  # fine-tuned 모델 ID
    input_file = "data/poor_docs/sample.docx"
    output_path = "outputs/corrected_pdfs/corrected_sample.pdf"

    os.makedirs("outputs/corrected_pdfs", exist_ok=True)

    result = generate_correction(model_name, input_file)
    export_pdf(result, output_path)
