import streamlit as st
from google import genai
from google.genai import types

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="AI 문제 해결 도우미",
    page_icon="💡",
    layout="wide"
)

# 2. API 키 불러오기 (Secrets 우선, 없으면 사이드바 입력 사용)
api_key = ""
try:
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

# 3. 사이드바 구성
with st.sidebar:
    st.title("⚙️ 설정 및 도구")
    
    # Secrets 키가 없을 경우 수동 입력창 제공
    if not api_key:
        api_key = st.text_input(
            "Gemini API Key", 
            type="password", 
            help="Secrets 설정이 되어있지 않다면 직접 입력하세요."
        )
    else:
        st.success("🔑 Secrets에서 API Key를 정상적으로 불러왔습니다.")

    st.divider()
    
    # 카테고리 선택
    category = st.selectbox(
        "🎯 문제 카테고리 선택",
        ["일반 / 기타", "코딩 및 개발 오류", "비즈니스 및 업무 기획", "일상 및 생산성", "학업 및 연구"]
    )
    
    st.divider()
    
    # 대화 내용 초기화 버튼
    if st.button("🔄 대화 초기화", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# 4. 세션 상태 초기화 (메시지 저장용)
if "messages" not in st.session_state:
    st.session_state.messages = []

# 5. 메인 화면 타이틀 및 안내
st.title("💡 AI 문제 해결 도우미")
st.caption("해결하고자 하는 문제나 에러 내용을 작성해 주세요. 핵심 분석부터 단계별 해결 방안을 제안합니다.")

# 6. 문제 해결 중심 시스템 프롬프트 정의
SYSTEM_INSTRUCTION = f"""
당신은 최고의 'AI 문제 해결 전문 컨설턴트'입니다.
현재 사용자가 선택한 문제 카테고리: [{category}]

답변을 작성할 때 반드시 아래의 3단계 문제 해결 프레임워크를 준수하세요:

1. **[1단계] 문제 원인 분석**
   - 질문의 핵심 이슈와 발생 원인을 명확하게 요약 및 진단합니다.

2. **[2단계] 단계별 실행 솔루션 (Step-by-Step)**
   - 문제 해결을 위해 당장 실행해야 할 액션 플랜을 순서대로 제시합니다.
   - 코드, 명령어, 구체적인 예시나 프로세스를 포함하여 바로 적용 가능하게 작성하세요.

3. **[3단계] 재발 방지 및 추가 팁**
   - 동일한 문제가 재발하지 않도록 예방하는 법이나 추가로 고려할 유용한 조언을 제공합니다.

명확하고 전문적이며 실행 중심의 친절한 어조를 유지하세요.
"""

# 7. 대화 이력 출력
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 8. 사용자 입력 및 AI 처리
if prompt := st.chat_input("해결할 문제나 에러 메시지를 입력하세요..."):
    # API 키 검증
    if not api_key or api_key.strip() == "":
        st.error("⚠️ Gemini API Key가 필요합니다. 사이드바에 입력하거나 Streamlit Secrets에 등록해 주세요.")
    else:
        # 사용자 메시지 화면 표시 및 저장
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # AI 응답 생성
        with st.chat_message("assistant"):
            with st.spinner("문제를 분석하여 최적의 해결책을 수립 중입니다..."):
                try:
                    # Google GenAI 클라이언트 생성
                    client = genai.Client(api_key=api_key)
                    
                    # 메시지 대화 이력 구성
                    contents = []
                    for msg in st.session_state.messages:
                        role = "user" if msg["role"] == "user" else "model"
                        contents.append(types.Content(role=role, parts=[types.Part.from_text(text=msg["content"])]))

                    # 모델 호출 (gemini-2.5-flash-lite)
                    response = client.models.generate_content(
                        model="gemini-2.5-flash-lite",
                        contents=contents,
                        config=types.GenerateContentConfig(
                            system_instruction=SYSTEM_INSTRUCTION,
                            temperature=0.2,
                        )
                    )

                    answer = response.text
                    st.markdown(answer)
                    
                    # 응답 저장
                    st.session_state.messages.append({"role": "assistant", "content": answer})

                except Exception as e:
                    st.error(f"❌ API 호출 중 오류가 발생했습니다: {str(e)}")
