
import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="익명 내신 문제 해결 게시판",
    page_icon="📚",
    layout="wide"
)

# 세션에 예시 데이터 저장
if "questions" not in st.session_state:
    st.session_state.questions = [
        {
            "id": 1,
            "grade": "고1",
            "subject": "수학",
            "title": "이차방정식 문제 풀이가 어려워요",
            "content": "판별식을 이용하는 문제인데 풀이 과정을 설명해 주세요.",
            "author": "익명 01",
            "solved": False,
            "created": "2026-10-25 15:30",
            "answers": [
                {
                    "author": "익명 답변자",
                    "content": "먼저 판별식 D=b²-4ac를 구해 보세요!"
                }
            ]
        },
        {
            "id": 2,
            "grade": "중3",
            "subject": "영어",
            "title": "관계대명사와 관계부사 차이",
            "content": "when과 which를 언제 구분해서 사용하나요?",
            "author": "익명 02",
            "solved": True,
            "created": "2026-10-24 18:20",
            "answers": [
                {
                    "author": "익명 답변자",
                    "content": "뒤에 완전한 문장이 오는지 확인하면 도움이 돼요."
                }
            ]
        },
        {
            "id": 3,
            "grade": "고2",
            "subject": "과학",
            "title": "전류와 전압의 관계",
            "content": "옴의 법칙을 실제 문제에 적용하는 방법이 궁금합니다.",
            "author": "익명 03",
            "solved": False,
            "created": "2026-10-23 12:10",
            "answers": []
        }
    ]

if "next_id" not in st.session_state:
    st.session_state.next_id = 4

if "selected_question" not in st.session_state:
    st.session_state.selected_question = None

st.title("📚 익명 내신 문제 해결 게시판")
st.caption("모르는 문제를 질문하고 함께 해결해 보세요!")

st.info(
    "프로토타입 체험용입니다. DB를 사용하지 않으므로 "
    "새로고침이나 앱 재시작 후 작성한 내용이 사라질 수 있습니다."
)

# 새 질문 작성
with st.expander("✏️ 새 질문 작성하기", expanded=False):
    with st.form("question_form", clear_on_submit=True):
        grade = st.selectbox(
            "학년",
            ["중1", "중2", "중3", "고1", "고2", "고3"]
        )

        subject = st.selectbox(
            "과목",
            ["수학", "국어", "영어", "과학", "사회", "역사", "기타"]
        )

        title = st.text_input("질문 제목")
        content = st.text_area("문제 내용 및 질문")

        submitted = st.form_submit_button("질문 등록")

        if submitted:
            if not title.strip() or not content.strip():
                st.warning("제목과 내용을 모두 입력해 주세요.")
            else:
                new_question = {
                    "id": st.session_state.next_id,
                    "grade": grade,
                    "subject": subject,
                    "title": title.strip(),
                    "content": content.strip(),
                    "author": "익명 사용자",
                    "solved": False,
                    "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "answers": []
                }

                st.session_state.questions.insert(0, new_question)
                st.session_state.next_id += 1
                st.session_state.selected_question = new_question["id"]

                st.success("질문이 등록되었습니다!")
                st.rerun()

# 검색 및 필터
st.subheader("🔎 질문 둘러보기")

col1, col2, col3 = st.columns(3)

with col1:
    search_text = st.text_input("제목 또는 내용 검색", placeholder="검색어 입력")

with col2:
    subject_filter = st.selectbox(
        "과목 필터",
        ["전체", "수학", "국어", "영어", "과학", "사회", "역사", "기타"]
    )

with col3:
    status_filter = st.selectbox(
        "해결 상태",
        ["전체", "미해결", "해결 완료"]
    )

questions = st.session_state.questions

filtered_questions = []

for q in questions:
    if subject_filter != "전체" and q["subject"] != subject_filter:
        continue

    if status_filter == "미해결" and q["solved"]:
        continue

    if status_filter == "해결 완료" and not q["solved"]:
        continue

    keyword = search_text.strip().lower()
    if keyword and keyword not in (
        q["title"] + " " + q["content"]
    ).lower():
        continue

    filtered_questions.append(q)

st.caption(f"총 {len(filtered_questions)}개의 질문")

# 질문 목록
for q in filtered_questions:
    with st.container(border=True):
        col1, col2 = st.columns([5, 1])

        with col1:
            status = "✅ 해결 완료" if q["solved"] else "🟡 미해결"
            st.markdown(f"**{q['title']}**")
            st.caption(
                f"{q['grade']} · {q['subject']} · "
                f"{q['author']} · {q['created']}"
            )
            st.write(q["content"])
            st.caption(f"{status}  |  답변 {len(q['answers'])}개")

        with col2:
            if st.button("상세 보기", key=f"view_{q['id']}"):
                st.session_state.selected_question = q["id"]
                st.rerun()

# 선택한 질문 상세 화면
selected_id = st.session_state.selected_question

if selected_id is not None:
    selected = next(
        (q for q in questions if q["id"] == selected_id),
        None
    )

    if selected:
        st.divider()
        st.subheader("📖 질문 상세")

        st.markdown(f"### {selected['title']}")
        st.caption(
            f"{selected['grade']} · {selected['subject']} · "
            f"{selected['author']} · {selected['created']}"
        )
        st.write(selected["content"])

        if selected["solved"]:
            st.success("해결 완료")
        else:
            st.warning("아직 해결되지 않은 질문입니다.")

        if st.button(
            "해결 상태 변경",
            key=f"solve_{selected['id']}"
        ):
            selected["solved"] = not selected["solved"]
            st.rerun()

        st.markdown("#### 💬 답변")

        if selected["answers"]:
            for i, answer in enumerate(selected["answers"]):
                with st.container(border=True):
                    st.caption(answer["author"])
                    st.write(answer["content"])
        else:
            st.write("아직 답변이 없습니다. 첫 답변을 남겨 보세요!")

        with st.form(f"answer_form_{selected['id']}", clear_on_submit=True):
            answer_text = st.text_area(
                "답변 작성",
                placeholder="풀이 방법이나 도움이 되는 내용을 적어 주세요."
            )

            answer_submitted = st.form_submit_button("답변 등록")

            if answer_submitted:
                if answer_text.strip():
                    selected["answers"].append({
                        "author": "익명 답변자",
                        "content": answer_text.strip()
                    })
                    st.success("답변이 등록되었습니다!")
                    st.rerun()
                else:
                    st.warning("답변 내용을 입력해 주세요.")

        if st.button("상세 보기 닫기"):
            st.session_state.selected_question = None
            st.rerun()
