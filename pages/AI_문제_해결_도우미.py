import streamlit as st
from google import genai
from google.genai import types

# 페이지 기본 설정
st.set_page_config(
    page_title="AI 실전 문제 해결 도우미",
    page_icon="🛠️",
    layout="wide"
)

# 사이드바 - API Key 및 옵션 설정
st.sidebar.title("⚙️ 설정 및 API Key")

# Secrets 또는 직접 입력에서 API Key 가져오기
gemini_api_key = st.secrets.get("GEMINI_API_KEY", "")

user_api_key = st.sidebar.text_input(
    "Gemini API Key 입력",
    value=gemini_api_key,
    type="password",
    help="Secrets에 등록되어 있지 않은 경우 여기에 API 키를 직접 입력하세요."
)

api_key_to_use = user_api_key if user_api_key else gemini_api_key

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 문제 해결 옵션")
category = st.sidebar.selectbox(
    "문제 분야 선택",
    ["🎓 학업/공부 방법", "💼 업무/비즈니스", "💻 IT/기술/코딩", "🛋️ 일상/습관 개선", "🤝 인간관계/소통"]
)

response_format = st.sidebar.radio(
    "답변 스타일",
    ["📋 4단계 실천 가이드", "⚡ 3줄 요약 핵심 해결책", "🛠️ 실행 체크리스트 포맷"]
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **특징:** 원론적인 정의나 불필요한 설명 없이 바로 실행할 수 있는 '문제 해결책'만 제공합니다.")

# 메인 화면 타이틀
st.title("🛠️ AI 실전 문제 해결 도우미")
st.caption("더 이상 원론적인 답변은 그만! 지금 당장 시작할 수 있는 실용적인 해결책을 만들어 드립니다.")

# 빠른 예시 버튼
st.markdown("##### 💡 빠른 질문 예시 (클릭 시 자동 입력)")
col1, col2, col3 = st.columns(3)

example_prompt = ""
if col1.button("📚 공부할 때 집중력이 떨어져요"):
    example_prompt = "공부할 때 10분만 지나면 집중력이 흐려지고 딴짓을 하게 됩니다. 당장 오늘 적용할 수 있는 공부법을 알려주세요."
if col2.button("⏱️ 업무 우선순위 정하기가 어려워요"):
    example_prompt = "할 일이 너무 많아서 무엇부터 시작해야 할지 모르겠습니다. 효율적인 우선순위 정리 솔루션이 필요해요."
if col3.button("💬 어색한 동료와 대화 트는 법"):
    example_prompt = "새로 들어온 팀원과 어색한 사이를 풀고 자연스럽게 대화를 시작하고 싶습니다."

# 입력 폼
with st.form(key="problem_form"):
    problem_input = st.text_area(
        "겪고 계신 문제나 고민을 자세히 적어주세요:",
        value=example_prompt if example_prompt else "",
        placeholder="예: 시험 기간인데 공부가 손에 안 잡히고 딴짓만 하게 돼요. 당장 실행할 수 있는 방법을 알려주세요.",
        height=130
    )
    submit_button = st.form_submit_button(label="🚀 실행 가능한 해결책 받기", use_container_width=True)

# 프롬프트 엔지니어링 (문제 해결 중심)
SYSTEM_INSTRUCTION = f"""
너는 최고의 '문제 해결 전문 컨설턴트'이다.
너의 유일한 목적은 사용자가 제출한 문제에 대해 백과사전식 정의, 불필요한 원론적/법률적 지식, 당위적 설명(예: '공부는 중요합니다' 등)을 완전히 배제하고, **지금 당장 실행할 수 있는 실전 솔루션**을 제시하는 것이다.

[답변 규칙]
1. 사전에 나올 법한 원론적인 설명이나 불필요한 인사를 절대 포함하지 말 것.
2. 해결책은 반드시 **구체적인 행동 지침(Actionable Steps)** 중심으로 구성할 것.
3. 선택된 분야({category})와 요청 스타일({response_format})에 맞춰 깔끔하게 마크다운으로 작성할 것.
4. 오늘 당장 5분 안에 시작할 수 있는 **첫 번째 행동(Small Win)**을 반드시 하단에 포함할 것.
"""

if submit_button:
    if not api_key_to_use:
        st.error("⚠️ Gemini API Key가 설정되지 않았습니다. 사이드바에 API Key를 입력하거나 Secrets를 등록해 주세요.")
    elif not problem_input.strip():
        st.warning("⚠️ 해결하고 싶은 문제 내용을 입력해 주세요.")
    else:
        with st.spinner("🔍 분석 중... 문제 해결 솔루션을 생성하고 있습니다."):
            try:
                # Gemini 클라이언트 초기화
                client = genai.Client(api_key=api_key_to_use)
                
                # 최신 지원 모델(gemini-3.5-flash-lite)로 변경 적용
                response = client.models.generate_content(
                    model="gemini-3.5-flash-lite",
                    contents=f"분야: {category}\n요청 스타일: {response_format}\n\n[사용자의 문제]\n{problem_input}",
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION,
                        temperature=0.3
                    )
                )
                
                st.success("✨ 해결 솔루션 생성이 완료되었습니다!")
                
                # 결과 출력
                st.markdown("### 🎯 맞춤형 문제 해결 솔루션")
                st.markdown("---")
                st.markdown(response.text)
                    
            except Exception as e:
                st.error(f"❌ API 호출 중 오류가 발생했습니다: {str(e)}")
                st.info("💡 API Key가 올바른지, Google AI Studio에서 키 권한 및 제한을 확인해 주세요.")
