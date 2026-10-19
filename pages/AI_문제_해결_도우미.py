import streamlit as st
from google import genai
from google.genai import types

# 페이지 기본 설정
st.set_page_config(
    page_title="AI 학생 전용 문제 해결 도우미",
    page_icon="🎒",
    layout="wide"
)

# 세션 상태(Session State) 초기화
if "problem_text" not in st.session_state:
    st.session_state["problem_text"] = ""

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
    ["📚 내신/수능/시험 대비", "✍️ 공부 습관/시간 관리", "👥 친구 관계/조별 과제", "🧭 진로/생기부/활동", "🛋️ 일상/멘탈 관리"]
)

response_format = st.sidebar.radio(
    "답변 스타일",
    ["📋 4단계 실천 가이드", "⚡ 3줄 요약 핵심 해결책", "🛠️ 실행 체크리스트 포맷"]
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **특징:** 교과서적인 원론이나 뻔한 솔루션 없이, 학생들이 오늘 당장 학교와 책상에서 실행할 수 있는 지침만 제공합니다.")

# 메인 화면 타이틀
st.title("🎒 AI 학생 전용 문제 해결 도우미")
st.caption("공부, 시험, 친구 관계, 조별 과제까지! 지금 당장 행동으로 옮길 수 있는 실전 솔루션을 알려드립니다.")

# 학생 맞춤형 빠른 예시 버튼 (session_state 활용)
st.markdown("##### 💡 학생 맞춤형 고민 예시 (클릭 시 자동 입력)")
col1, col2, col3 = st.columns(3)

if col1.button("📱 시험 기간 폰 중독"):
    st.session_state["problem_text"] = "시험 기간인데 책상에 앉기만 하면 폰을 보고 딴짓을 하게 됩니다. 당장 오늘 스마트폰을 내려놓고 공부에 몰입할 수 있는 환경 설정과 행동법을 알려주세요."

if col2.button("⚡ 시험 D-3 벼락치기"):
    st.session_state["problem_text"] = "시험이 3일밖에 안 남았는데 공부할 양이 너무 많아서 막막합니다. 지금 당장 어떤 순서로 무엇부터 외우고 공부해야 할지 벼락치기 우선순위 전략을 짜주세요."

if col3.button("👥 조별 과제 무임승차 대처"):
    st.session_state["problem_text"] = "조별 과제에서 아무것도 안 하는 조원이 있습니다. 감정적으로 싸우지 않고 역할을 나누어 과제를 완성할 수 있는 가이드를 알려주세요."

# 입력 폼
with st.form(key="problem_form"):
    problem_input = st.text_area(
        "겪고 계신 문제나 고민을 자세히 적어주세요:",
        value=st.session_state["problem_text"],
        placeholder="예: 수행평가 제출이 내일인데 주제 잡기가 너무 힘들어요. 오늘 저녁 안에 완성할 수 있는 단계별 방법을 알려주세요.",
        height=130
    )
    submit_button = st.form_submit_button(label="🚀 실행 가능한 해결책 받기", use_container_width=True)

# 프롬프트 엔지니어링 (학생 및 문제 해결 중심)
SYSTEM_INSTRUCTION = f"""
너는 학생들을 돕는 최고의 '학생 전용 문제 해결 컨설턴트'이다.
너의 유일한 목적은 학생이 제출한 문제에 대해 원론적이고 진부한 조언(예: '공부는 중요하니 열심히 하세요', '친구와 대화를 나누세요' 등)을 완전히 배제하고, **학생이 책상이나 학교에서 오늘 당장 5분 안에 시작할 수 있는 실천 지침**을 제시하는 것이다.

[답변 규칙]
1. 불필요한 인사나 교과서적인 설명은 전부 생략할 것.
2. 학생의 눈높이에 맞춰 이해하기 쉽고 명확한 말투로 작성할 것.
3. 선택된 분야({category})와 요청 스타일({response_format})에 맞추어 구성할 것.
4. 오늘 당장 5분 안에 실행할 수 있는 **첫 번째 작은 행동(Small Win)**을 반드시 하단에 포함할 것.
"""

if submit_button:
    if not api_key_to_use:
        st.error("⚠️ Gemini API Key가 설정되지 않았습니다. 사이드바에 API Key를 입력하거나 Secrets를 등록해 주세요.")
    elif not problem_input.strip():
        st.warning("⚠️ 해결하고 싶은 문제 내용을 입력해 주세요.")
    else:
        with st.spinner("🔍 분석 중... 학생 맞춤형 솔루션을 생성하고 있습니다."):
            try:
                # Gemini 클라이언트 초기화
                client = genai.Client(api_key=api_key_to_use)
                
                # API 호출 (gemini-3.5-flash-lite)
                response = client.models.generate_content(
                    model="gemini-3.5-flash-lite",
                    contents=f"분야: {category}\n요청 스타일: {response_format}\n\n[학생의 고민/문제]\n{problem_input}",
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
