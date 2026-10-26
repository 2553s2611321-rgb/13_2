
import streamlit as st
from supabase import create_client
from datetime import datetime
import uuid

st.set_page_config(
    page_title="익명 내신 문제 해결 게시판",
    page_icon="📚",
    layout="wide"
)

SUBJECTS = ["수학", "국어", "영어", "과학", "사회/역사", "기타"]
GRADES = ["중1", "중2", "중3", "고1", "고2", "고3"]
BUCKET = "question-images"
MAX_IMAGE_SIZE = 5 * 1024 * 1024

st.title("📚 익명 내신 문제 해결 게시판")
st.caption("모르는 문제를 질문하고 서로 풀이를 공유해 보세요!")

# Supabase 연결
@st.cache_resource
def connect_db():
    return create_client(
        st.secrets["supabase"]["url"],
        st.secrets["supabase"]["anon_key"]
    )

try:
    db = connect_db()
except Exception:
    st.error("Supabase 설정을 확인해 주세요.")
    st.stop()


# 게시글 불러오기
def get_questions():
    result = (
        db.table("questions")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )
    return result.data or []


# 답변 불러오기
def get_answers(question_id):
    result = (
        db.table("answers")
        .select("*")
        .eq("question_id", question_id)
        .order("created_at")
        .execute()
    )
    return result.data or []


# 날짜 표시
def format_date(value):
    if not value:
        return ""
    try:
        return datetime.fromisoformat(
            value.replace("Z", "+00:00")
        ).astimezone().strftime("%Y-%m-%d %H:%M")
    except (ValueError, TypeError):
        return str(value)


# 사진 업로드
def upload_image(file):
    if file is None:
        return None

    data = file.getvalue()

    if len(data) > MAX_IMAGE_SIZE:
        raise ValueError("사진은 5MB 이하만 첨부할 수 있습니다.")

    extension = file.name.rsplit(".", 1)[-1].lower()

    if extension not in ["png", "jpg", "jpeg"]:
        raise ValueError("PNG, JPG, JPEG 파일만 가능합니다.")

    path = f"{uuid.uuid4().hex}.{extension}"

    db.storage.from_(BUCKET).upload(
        path,
        data,
        file_options={
            "content-type": file.type or "image/jpeg"
        }
    )

    return db.storage.from_(BUCKET).get_public_url(path)


# 사이드바: 질문 작성
with st.sidebar:
    st.header("✏️ 질문 작성")

    with st.form("question_form", clear_on_submit=True):
        subject = st.selectbox("과목", SUBJECTS)
        grade = st.selectbox("학년", GRADES)

        title = st.text_input(
            "질문 제목",
            max_chars=120,
            placeholder="예: 이차방정식 문제 질문"
        )

        content = st.text_area(
            "질문 내용",
            max_chars=8000,
            placeholder="문제 내용과 막힌 부분을 적어 주세요."
        )

        photo = st.file_uploader(
            "문제 사진 첨부 (선택)",
            type=["png", "jpg", "jpeg"]
        )

        submit = st.form_submit_button(
            "질문 등록하기",
            use_container_width=True
        )

    if submit:
        if not title.strip() or not content.strip():
            st.warning("제목과 내용을 모두 입력해 주세요.")
        else:
            try:
                image_url = upload_image(photo)

                db.table("questions").insert({
                    "subject": subject,
                    "grade": grade,
                    "title": title.strip(),
                    "content": content.strip(),
                    "image_url": image_url,
                    "resolved": False,
                    "author": "익명"
                }).execute()

                st.success("질문이 등록되었습니다!")
                st.rerun()

            except Exception as error:
                st.error(f"질문 등록 실패: {error}")

    st.divider()
    st.caption("개인정보는 질문이나 사진에 올리지 마세요.")


# 검색 및 필터
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    keyword = st.text_input(
        "🔎 게시글 검색",
        placeholder="제목 또는 내용 검색"
    )

with col2:
    subject_filter = st.selectbox(
        "과목",
        ["전체"] + SUBJECTS
    )

with col3:
    status_filter = st.selectbox(
        "해결 상태",
        ["전체", "답변 대기 중", "해결 완료"]
    )


# 게시글 목록
try:
    questions = get_questions()
except Exception as error:
    st.error(f"게시글을 불러오지 못했습니다: {error}")
    st.stop()

if subject_filter != "전체":
    questions = [
        q for q in questions
        if q["subject"] == subject_filter
    ]

if status_filter == "답변 대기 중":
    questions = [q for q in questions if not q["resolved"]]
elif status_filter == "해결 완료":
    questions = [q for q in questions if q["resolved"]]

if keyword.strip():
    word = keyword.strip().casefold()
    questions = [
        q for q in questions
        if word in q["title"].casefold()
        or word in q["content"].casefold()
    ]

st.subheader(f"📋 게시글 목록 ({len(questions)}개)")

if not questions:
    st.info("게시글이 없습니다. 첫 질문을 작성해 보세요!")


# 개별 게시글
for q in questions:
    status = "✅ 해결 완료" if q["resolved"] else "❓ 답변 대기 중"

    with st.expander(
        f"[{q['subject']} / {q['grade']}] "
        f"{q['title']} · {status}"
    ):
        st.caption(
            f"작성자: 익명 · {format_date(q.get('created_at'))}"
        )

        st.write(q["content"])

        if q.get("image_url"):
            st.image(
                q["image_url"],
                caption="첨부된 문제 사진",
                use_container_width=True
            )

        # 해결 상태 변경
        if not q["resolved"]:
            if st.button(
                "해결 완료로 표시",
                key=f"resolve_{q['id']}"
            ):
                try:
                    db.table("questions").update(
                        {"resolved": True}
                    ).eq("id", q["id"]).execute()
                    st.rerun()
                except Exception as error:
                    st.error(f"상태 변경 실패: {error}")
        else:
            st.success("해결된 질문입니다.")

            if st.button(
                "해결 상태 취소",
                key=f"unresolve_{q['id']}"
            ):
                try:
                    db.table("questions").update(
                        {"resolved": False}
                    ).eq("id", q["id"]).execute()
                    st.rerun()
                except Exception as error:
                    st.error(f"상태 변경 실패: {error}")

        # 답변 목록
        st.markdown("### 💬 답변 목록")

        try:
            answers = get_answers(q["id"])
        except Exception as error:
            st.error(f"답변을 불러오지 못했습니다: {error}")
            answers = []

        if not answers:
            st.caption("아직 답변이 없습니다.")

        for answer in answers:
            with st.container(border=True):
                st.caption(
                    f"익명 · {format_date(answer.get('created_at'))}"
                )
                st.write(answer["content"])

        # 답변 작성
        st.markdown("#### ✏️ 답변 작성")

        with st.form(f"answer_form_{q['id']}", clear_on_submit=True):
            answer_content = st.text_area(
                "답변 내용",
                max_chars=8000,
                placeholder="풀이 과정을 이해하기 쉽게 작성해 주세요."
            )

            answer_submit = st.form_submit_button("답변 등록")

            if answer_submit:
                if not answer_content.strip():
                    st.warning("답변 내용을 입력해 주세요.")
                else:
                    try:
                        db.table("answers").insert({
                            "question_id": q["id"],
                            "content": answer_content.strip(),
                            "author": "익명"
                        }).execute()

                        st.success("답변이 등록되었습니다!")
                        st.rerun()

                    except Exception as error:
                        st.error(f"답변 등록 실패: {error}")


st.divider()
st.caption(
    "익명 게시판입니다. 공개 게시 전 개인정보 보호와 "
    "관리자 권한 설정을 확인해 주세요."
)
