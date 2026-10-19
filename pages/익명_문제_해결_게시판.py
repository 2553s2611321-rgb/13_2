import streamlit as st
from datetime import datetime

# 페이지 설정
st.set_page_config(
    page_title="익명 내신 Q&A 게시판",
    page_icon="📚",
    layout="wide"
)

# 세션 상태 초기화 (데이터 저장소)
if "questions" not in st.session_state:
    st.session_state.questions = [
        {
            "id": 1,
            "title": "고1 수학(상) 이차방정식 근과 계수 문제 풀이 부탁해요!",
            "subject": "수학",
            "grade": "고1",
            "author": "익명 1",
            "content": "이차방정식 x^2 - 4x + 2 = 0 의 두 근이 alpha, beta 일 때, alpha^2 + beta^2 값을 알려주세요!",
            "image": None,
            "created_at": "2026-10-19 10:00",
            "resolved": False,
            "answers": [
                {
                    "author": "익명 2",
                    "content": "어 그 문제는 곱셈공식 변형으로 푸는거야! (alpha + beta)^2 - 2*alpha*beta 에 대입하면 16 - 4 = 12가 나와!!",
                    "created_at": "2026-10-19 10:05"
                },
                {
                    "author": "익명 3",
                    "content": "근과 계수와의 관계를 쓰면 alpha+beta=4, alpha*beta=2니까 제곱해서 계산해도 돼!!",
                    "created_at": "2026-10-19 10:10"
                }
            ]
        }
    ]

# 메인 타이틀
st.title("📚 익명 내신 문제 Q&A")
st.caption("모르는 내신 문제를 부담 없이 익명으로 질문하고 답변을 주고받아 보세요!")

# 사이드바: 질문 등록 및 필터
st.sidebar.header("🔍 질문 검색 및 필터")
selected_subject = st.sidebar.selectbox("과목 선택", ["전체", "수학", "국어", "영어", "과학", "사회/역사", "기타"])
selected_status = st.sidebar.radio("상태 필터", ["전체 보기", "답변 대기 중", "해결 완료"])

st.sidebar.markdown("---")
st.sidebar.header("✏️ 새 질문 올리기")

with st.sidebar.form("question_form", clear_on_submit=True):
    q_subject = st.selectbox("과목", ["수학", "국어", "영어", "과학", "사회/역사", "기타"])
    q_grade = st.selectbox("학년", ["중1", "중2", "중3", "고1", "고2", "고3"])
    q_title = st.text_input("질문 제목", placeholder="예: 이차함수 최대최소 문제 질문")
    q_content = st.text_area("질문 내용", placeholder="모르는 문제 내용이나 풀다가 막힌 부분을 상세히 작성해주세요.")
    q_image = st.file_uploader("문제 사진 첨부 (선택)", type=["png", "jpg", "jpeg"])
    submit_btn = st.form_submit_button("질문 등록하기")

    if submit_btn:
        if not q_title.strip() or not q_content.strip():
            st.error("제목과 내용을 모두 입력해 주세요.")
        else:
            new_id = len(st.session_state.questions) + 1
            new_q = {
                "id": new_id,
                "title": q_title,
                "subject": q_subject,
                "grade": q_grade,
                "author": f"익명 {new_id}",
                "content": q_content,
                "image": q_image,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "resolved": False,
                "answers": []
            }
            st.session_state.questions.insert(0, new_q)
            st.success("질문이 성공적으로 등록되었습니다!")
            st.rerun()

# 질문 목록 필터링
filtered_q = st.session_state.questions

if selected_subject != "전체":
    filtered_q = [q for q in filtered_q if q["subject"] == selected_subject]

if selected_status == "답변 대기 중":
    filtered_q = [q for q in filtered_q if not q["resolved"]]
elif selected_status == "해결 완료":
    filtered_q = [q for q in filtered_q if q["resolved"]]

# 메인 화면: 질문 목록 표시
st.subheader(f"📋 등록된 질문 목록 ({len(filtered_q)}개)")

if not filtered_q:
    st.info("조건에 해당하는 질문이 없습니다. 새로운 질문을 작성해보세요!")

for q in filtered_q:
    status_tag = "✅ 해결됨" if q["resolved"] else "❓ 답변 대기중"
    with st.expander(f"[{q['subject']}/{q['grade']}] {q['title']}  |  {status_tag}"):
        st.markdown(f"**작성자:** {q['author']} | **작성일:** {q['created_at']}")
        st.markdown("---")
        st.write(q["content"])
        
        if q["image"] is not None:
            st.image(q["image"], caption="첨부된 문제 이미지", use_column_width=True)
            
        st.markdown("---")
        
        # 해결 처리 버튼
        col1, col2 = st.columns([1, 4])
        with col1:
            if not q["resolved"]:
                if st.button("해결 완료로 표시", key=f"resolve_{q['id']}"):
                    q["resolved"] = True
                    st.success("해결 상태로 변경되었습니다!")
                    st.rerun()
            else:
                st.write("🎉 해결된 질문입니다.")

        # 답변 목록
        st.markdown("### 💬 답변 목록")
        if not q["answers"]:
            st.caption("아직 작성된 답변이 없습니다. 첫번째 답변자가 되어보세요!")
        else:
            for idx, ans in enumerate(q["answers"]):
                with st.chat_message("user", avatar="🎓"):
                    st.markdown(f"**{ans['author']}** (`{ans['created_at']}`)")
                    st.write(ans["content"])

        # 답변 작성 Form
        st.markdown("#### ✏️ 답변 달기")
        with st.form(key=f"ans_form_{q['id']}", clear_on_submit=True):
            ans_text = st.text_area("답변 작성", placeholder="친절하고 이해하기 쉽게 풀이 과정을 적어주세요.")
            ans_submit = st.form_submit_button("답변 등록")
            
            if ans_submit:
                if not ans_text.strip():
                    st.warning("답변 내용을 입력해주세요.")
                else:
                    ans_author_num = len(q["answers"]) + 2
                    new_answer = {
                        "author": f"익명 {ans_author_num}",
                        "content": ans_text,
                        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
                    }
                    q["answers"].append(new_answer)
                    st.success("답변이 등록되었습니다!")
                    st.rerun()
