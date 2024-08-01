import textwrap
import google.generativeai as genai
import streamlit as st
import toml
import pathlib

# secrets.toml 파일 경로
secrets_path = pathlib.Path(__file__).parent.parent / ".streamlit/secrets.toml"

# secrets.toml 파일 읽기
with open(secrets_path, "r") as f:
    secrets = toml.load(f)

# secrets.toml 파일에서 API 키 값 가져오기
api_key = secrets.get("api_key")

def to_markdown(text):
    text = text.replace('•', '*')
    return textwrap.indent(text, '> ', predicate=lambda _: True)

def try_generate_content(api_key, prompt):
    genai.configure(api_key=api_key)
   
    model = genai.GenerativeModel(model_name="gemini-1.0-pro",
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
                                  ])
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"API 호출 실패: {e}")
        return None

# Streamlit 앱 시작
st.title("지리 퀴즈 피드백 앱 🌍")

st.write("아래의 퀴즈를 풀고 제출하세요. 제출 후 피드백을 제공합니다.")

# 간단한 지리 퀴즈 제공
quiz_questions = [
    {
        "question": "가장 큰 대륙은 무엇인가요?",
        "options": ["아시아", "아프리카", "유럽", "남아메리카"],
        "answer": "아시아"
    },
    {
        "question": "세계에서 가장 큰 섬은 무엇인가요?",
        "options": ["그린란드", "뉴기니", "보르네오", "마다가스카르"],
        "answer": "그린란드"
    }
]

# 퀴즈 출력 및 답변 입력 받기
answers = []
for i, q in enumerate(quiz_questions):
    st.write(f"**{i+1}. {q['question']}**")
    answer = st.radio("", q["options"], key=f"q{i}", label_visibility="collapsed")
    answers.append(answer)

if st.button("제출"):
    correct_count = 0
    for i, q in enumerate(quiz_questions):
        if answers[i] == q["answer"]:
            correct_count += 1
    
    feedback_prompt = f"학생이 {len(quiz_questions)}개의 질문 중 {correct_count}개를 맞췄습니다. 피드백을 제공해주세요."
    feedback = try_generate_content(api_key, feedback_prompt)
    
    if feedback:
        st.markdown(to_markdown(feedback))
    else:
        st.error("피드백을 가져오는 데 실패했습니다. 다시 시도해주세요.")
