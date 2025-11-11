
import os
import sys
import streamlit as st
from openai import OpenAI
from infer_utils import extract_sections, generate_correction, export_pdf

import openai, sys, os
print("openai version:", openai.__version__)
print("python path:", sys.executable)
print("api key prefix:", os.getenv("OPENAI_API_KEY")[:20])


# ✅ 1. 직접 API 키 지정
OPENAI_API_KEY = ""
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# ✅ 2. OpenAI 클라이언트 생성
client = OpenAI(api_key=OPENAI_API_KEY)

# 페이지 설정
st.set_page_config(page_title="이의신청서 교정 모델", page_icon="📄")

st.title("📄 국민건강보험공단 이의신청서 교정 모델")
st.write("못 쓴 이의신청서를 업로드하면 GPT가 자동으로 문체와 논리를 교정해줍니다.")
st.write(f"✅ Using API key: {OPENAI_API_KEY[:20]}...")

# ✅ 3. 사용 가능한 모델 목록 불러오기
try:
    with st.spinner("사용 가능한 모델 목록을 불러오는 중..."):
        models = [m.id for m in client.models.list().data if "gpt" in m.id]
    if not models:
        st.warning("사용 가능한 GPT 모델이 없습니다. 결제 활성화를 확인하세요.")
    else:
        st.success(f"{len(models)}개의 모델이 감지되었습니다.")
except Exception as e:
    st.error(f"모델 목록을 불러오지 못했습니다: {e}")
    models = []

# ✅ 4. 모델 선택 UI
default_model = "gpt-4o-mini" if "gpt-4o-mini" in models else (models[0] if models else "")
model_name = st.selectbox("🧠 사용할 모델을 선택하세요", models, index=models.index(default_model) if default_model in models else 0)

# ✅ 5. 파일 업로드 및 교정 실행
uploaded_file = st.file_uploader("이의신청서 (.docx) 파일 업로드", type=["docx"])

if uploaded_file:
    st.info("파일을 업로드했습니다. 교정 실행 버튼을 눌러주세요.")

    if st.button("✏️ 교정 실행"):
        with st.spinner(f"{model_name} 모델로 교정 중입니다..."):
            try:
                part2, part4 = extract_sections(uploaded_file)
                input_text = f"② 처분의 내용:\n{part2}\n\n④ 이의신청의 취지와 사유:\n{part4}"

                # ✅ 선택된 모델로 교정 실행
                result = generate_correction(model_name, input_text)

                st.subheader("🪄 교정된 결과")
                st.text_area("결과 미리보기", result, height=300)

                os.makedirs("outputs/corrected_pdfs", exist_ok=True)
                output_pdf = os.path.join("outputs/corrected_pdfs", f"{uploaded_file.name}_corrected.pdf")
                export_pdf(result, output_pdf)

                with open(output_pdf, "rb") as f:
                    st.download_button(
                        label="📥 PDF 다운로드",
                        data=f,
                        file_name=f"{uploaded_file.name}_corrected.pdf",
                        mime="application/pdf"
                    )

                st.success(f"✅ {model_name} 모델로 교정 완료!")
            except Exception as e:
                st.error(f"❌ 오류 발생: {e}")
