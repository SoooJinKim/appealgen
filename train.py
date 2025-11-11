# train.py
import os
import json
from docx import Document
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_sections(docx_path):
    """
    docx 파일에서 ②와 ④ 항목 추출
    """
    doc = Document(docx_path)
    text = "\n".join([p.text.strip() for p in doc.paragraphs])
    content_2, content_4 = "", ""

    if "②" in text and "④" in text:
        part_2 = text.split("②")[1].split("③")[0].strip() if "③" in text else ""
        part_4 = text.split("④")[1].split("⑤")[0].strip() if "⑤" in text else ""
        content_2, content_4 = part_2, part_4

    return content_2, content_4


def make_training_pairs(good_dir, poor_dir, out_path):
    data = []
    good_files = sorted(os.listdir(good_dir))
    poor_files = sorted(os.listdir(poor_dir))

    for g, p in zip(good_files, poor_files):
        good_2, good_4 = extract_sections(os.path.join(good_dir, g))
        poor_2, poor_4 = extract_sections(os.path.join(poor_dir, p))

        input_text = f"② 처분의 내용:\n{poor_2}\n\n④ 이의신청의 취지와 사유:\n{poor_4}"
        output_text = f"② 처분의 내용:\n{good_2}\n\n④ 이의신청의 취지와 사유:\n{good_4}"

        data.append({
            "messages": [
                {"role": "system", "content": "너는 행정문서 교정 전문가이다."},
                {"role": "user", "content": input_text},
                {"role": "assistant", "content": output_text}
            ]
        })

    with open(out_path, "w", encoding="utf-8") as f:
        for d in data:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")

    print(f"✅ Training data saved to {out_path} ({len(data)} samples)")


def run_fine_tuning(train_file):
    # 1️⃣ 업로드
    file_resp = client.files.create(file=open(train_file, "rb"), purpose="fine-tune")

    # 2️⃣ 파인튜닝 실행
    job = client.fine_tuning.jobs.create(
        training_file=file_resp.id,
        model="gpt-4o-mini-2024-11-01",
        suffix="appeal-correction"
    )
    print("🚀 Fine-tuning job created!")
    print(job)


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)

    out_path = "data/appeal_train.jsonl"
    make_training_pairs("data/good_docs", "data/poor_docs", out_path)
    run_fine_tuning(out_path)
