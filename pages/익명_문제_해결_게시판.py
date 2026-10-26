
# ====================================
# 💬 익명 사용자 채팅 기능
# ====================================

st.divider()
st.header("💬 익명 소통방")
st.write("다른 학생들과 공부 관련 질문이나 풀이 방법을 자유롭게 나눠 보세요!")

# 채팅 데이터 초기화
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {
            "name": "익명 01",
            "message": "수학 시험 범위 어디까지인가요?",
            "time": "09:00"
        },
        {
            "name": "익명 02",
            "message": "저희는 이차방정식까지예요!",
            "time": "09:02"
        },
        {
            "name": "익명 03",
            "message": "영어 단어 외우는 팁 있나요?",
            "time": "09:05"
        }
    ]

if "chat_nickname" not in st.session_state:
    st.session_state.chat_nickname = "익명 사용자"

# 닉네임 설정
nickname = st.text_input(
    "채팅 닉네임",
    value=st.session_state.chat_nickname,
    max_chars=15,
    key="chat_nickname_input"
)

st.session_state.chat_nickname = nickname.strip() or "익명 사용자"

# 채팅 내역
st.subheader("대화 내용")

chat_box = st.container(height=300, border=True)

with chat_box:
    for msg in st.session_state.chat_messages:
        st.markdown(
            f"**{msg['name']}** · {msg['time']}"
        )
        st.write(msg["message"])
        st.divider()

# 메시지 보내기
with st.form("chat_form", clear_on_submit=True):
    message = st.text_input(
        "메시지",
        placeholder="메시지를 입력하세요...",
        max_chars=300
    )

    send = st.form_submit_button("보내기")

    if send:
        if message.strip():
            st.session_state.chat_messages.append({
                "name": st.session_state.chat_nickname,
                "message": message.strip(),
                "time": datetime.now().strftime("%H:%M")
            })
            st.rerun()
        else:
            st.warning("메시지를 입력해 주세요.")
