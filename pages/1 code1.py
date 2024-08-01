import textwrap
import google.generativeai as genai
import streamlit as st
import toml
import pathlib

# 현재 파일의 부모 디렉토리 경로를 기준으로 secrets.toml 파일 경로 설정
secrets_path = pathlib.Path(__file__).resolve().parent.parent / ".streamlit/secrets.toml"

# secrets.toml 파일 읽기
try:
    with open(secrets_path, "r") as f:
        secrets = toml.load(f)
except FileNotFoundError:
    st.error(f"secrets.toml 파일을 찾을 수 없습니다: {secrets_path}")
    secrets = {}

# secrets.toml 파일에서 API 키 값 가져오기
api_key = secrets.get("api_key")

def to_markdown(text):
    text = text.replace('•', '*')
    return textwrap.indent(text, '> ', predicate=lambda _: True)

def try_generate_content(api_key, prompt):
    genai.configure(api_key=api_key)

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config={
            "temperature": 0.9,
            "top_p": 1,
            "top_k": 1,
            "max_output_tokens": 2048,
        },
        safety_settings=[
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]
    )
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"API 호출 실패: {e}")
        return None

st.title("🩺 증상 기반 영양소 부족 확인기")

st.markdown("""
### 📝 가이드라인
1. **증상 입력하기** 🖊️
   - 예: 피로, 어지러움
   - 증상은 간단하고 명확하게 입력해주세요.
   
2. **확인 버튼 누르기** 🖱️
   - 입력한 증상에 따라 부족할 수 있는 무기질 및 비타민 정보를 제공합니다.
   
3. **결과 확인하기** 🔍
   - 결과는 아래에 표시됩니다. 부족한 영양소를 확인하고 적절한 음식을 섭취하세요.
   
⚠️ **주의사항**
- **API 키 설정**: 처음 사용할 때는 반드시 Google API 키를 입력해야 합니다.
- **정확성**: 제공되는 정보는 참고용입니다. 건강 문제가 지속되면 전문가와 상담하세요.
""")

st.image("https://previews.123rf.com/images/elnur/elnur1704/elnur170401231/75108548-%EB%8F%85%EA%B0%90%EC%9D%B4-%EC%B9%A8%EB%8C%80%EC%97%90-%EB%88%84%EC%9B%8C%EC%9E%88%EB%8A%94-%EC%95%84%ED%94%88-%EC%82%AC%EB%9E%8C.jpg", caption='아픈 사람', use_column_width=True)

symptom = st.text_input("증상을 입력하세요", "예: 피로, 어지러움")

if st.button("확인"):
    if not api_key:
        st.error("API 키를 설정해주세요!")
    else:
        prompt = f"다음 증상에 대한 무기질 및 비타민 부족 정보를 제공해주세요: {symptom}"
        result = try_generate_content(api_key, prompt)
        if result:
            st.markdown(to_markdown(result))
        else:
            st.error("콘텐츠 생성에 실패했습니다. 나중에 다시 시도해주세요.")
