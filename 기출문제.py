import streamlit as st
import pandas as pd
from datetime import datetime

# =====================================
# 기본 설정
# =====================================
st.set_page_config(
    page_title="기출문제 모음",
    page_icon="📚",
    layout="wide"
)

# =====================================
# 기출문제 예시 데이터
# =====================================
QUESTIONS = [
    {
        "id": 1,
        "subject": "국어",
        "grade": "1학년",
        "year": 2025,
        "exam": "중간고사",
        "title": "중심 내용 파악",
        "question": "글의 중심 내용을 파악하는 방법으로 가장 적절한 것은?",
        "choices": [
            "첫 문장만 읽는다",
            "핵심 내용과 글 전체의 흐름을 살핀다",
            "모르는 단어만 찾는다",
            "마지막 문장만 외운다"
        ],
        "answer": 1,
        "explanation": "핵심 내용과 글 전체의 흐름을 함께 살펴야 중심 내용을 정확하게 파악할 수 있습니다."
    },
    {
        "id": 2,
        "subject": "국어",
        "grade": "2학년",
        "year": 2024,
        "exam": "기말고사",
        "title": "비유 표현",
        "question": "'내 마음은 호수요'에 사용된 표현 방법은?",
        "choices": ["반어", "의인", "은유", "과장"],
        "answer": 2,
        "explanation": "은유는 한 대상을 다른 대상에 직접 빗대어 표현하는 방법입니다."
    },
    {
        "id": 3,
        "subject": "수학",
        "grade": "1학년",
        "year": 2025,
        "exam": "중간고사",
        "title": "일차방정식",
        "question": "3x + 5 = 20일 때 x의 값은?",
        "choices": ["3", "5", "8", "15"],
        "answer": 1,
        "explanation": "3x + 5 = 20에서 양변에 5를 빼면 3x = 15입니다. 따라서 x = 5입니다."
    },
    {
        "id": 4,
        "subject": "수학",
        "grade": "2학년",
        "year": 2025,
        "exam": "기말고사",
        "title": "삼각형의 넓이",
        "question": "밑변이 8cm이고 높이가 5cm인 삼각형의 넓이는?",
        "choices": ["13㎠", "20㎠", "40㎠", "80㎠"],
        "answer": 1,
        "explanation": "삼각형의 넓이는 밑변 × 높이 ÷ 2입니다. 8 × 5 ÷ 2 = 20㎠입니다."
    },
    {
        "id": 5,
        "subject": "영어",
        "grade": "1학년",
        "year": 2025,
        "exam": "기말고사",
        "title": "영어 문법",
        "question": "빈칸에 알맞은 말을 고르세요: She ____ to school every day.",
        "choices": ["go", "goes", "going", "gone"],
        "answer": 1,
        "explanation": "주어가 3인칭 단수이고 현재의 습관을 나타내므로 goes가 알맞습니다."
    },
    {
        "id": 6,
        "subject": "영어",
        "grade": "2학년",
        "year": 2024,
        "exam": "중간고사",
        "title": "영어 어휘",
        "question": "'important'와 가장 가까운 뜻을 가진 단어는?",
        "choices": ["easy", "significant", "empty", "quiet"],
        "answer": 1,
        "explanation": "important와 significant는 모두 '중요한'이라는 뜻입니다."
    },
    {
        "id": 7,
        "subject": "사회",
        "grade": "1학년",
        "year": 2025,
        "exam": "중간고사",
        "title": "지도 읽기",
        "question": "지도에서 실제 거리를 일정한 비율로 줄여 나타낸 것은?",
        "choices": ["범례", "방위표", "축척", "등고선"],
        "answer": 2,
        "explanation": "축척은 지도상의 거리와 실제 거리 사이의 비율을 나타냅니다."
    },
    {
        "id": 8,
        "subject": "사회",
        "grade": "2학년",
        "year": 2024,
        "exam": "기말고사",
        "title": "민주주의",
        "question": "국민이 정치에 참여하는 방법으로 적절한 것은?",
        "choices": [
            "선거에 참여하기",
            "법을 무시하기",
            "다른 사람의 의견을 금지하기",
            "정보를 숨기기"
        ],
        "answer": 0,
        "explanation": "선거는 국민이 대표자를 선택하고 정치에 참여하는 중요한 방법입니다."
    },
    {
        "id": 9,
        "subject": "과학",
        "grade": "1학년",
        "year": 2024,
        "exam": "기말고사",
        "title": "물질의 상태",
        "question": "일정한 모양과 부피를 가지는 물질의 상태는?",
        "choices": ["고체", "액체", "기체", "수증기"],
        "answer": 0,
        "explanation": "고체는 일정한 모양과 부피를 유지합니다."
    },
    {
        "id": 10,
        "subject": "과학",
        "grade": "2학년",
        "year": 2025,
        "exam": "중간고사",
        "title": "힘과 운동",
        "question": "물체의 운동 상태를 변화시키는 원인이 되는 것은?",
        "choices": ["힘", "색깔", "이름", "무늬"],
        "answer": 0,
        "explanation": "힘은 물체의 운동 상태나 모양을 변화시킬 수 있습니다."
    },
    {
        "id": 11,
        "subject": "한국사",
        "grade": "2학년",
        "year": 2025,
        "exam": "기말고사",
        "title": "고려의 건국",
        "question": "고려를 건국한 인물은 누구인가요?",
        "choices": ["이성계", "왕건", "궁예", "견훤"],
        "answer": 1,
        "explanation": "왕건은 918년에 고려를 건국했습니다."
    },
    {
        "id": 12,
        "subject": "한국사",
        "grade": "1학년",
        "year": 2023,
        "exam": "중간고사",
        "title": "조선의 건국",
        "question": "조선을 건국한 인물은 누구인가요?",
        "choices": ["왕건", "세종", "이성계", "정몽주"],
        "answer": 2,
        "explanation": "이성계는 1392년에 조선을 건국했습니다."
    }
]

SUBJECTS = ["국어", "수학", "영어", "사회", "과학", "한국사"]


# =====================================
# 세션 상태 초기화
# =====================================
DEFAULTS = {
    "navigation": "문제 찾기",
    "quiz_ids": [],
    "quiz_index": 0,
    "answers": {},
    "checked": set(),
    "finished": False,
    "history": []
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =====================================
# 기능 함수
# =====================================
def start_quiz(ids):
    st.session_state.quiz_ids = list(ids)
    st.session_state.quiz_index = 0
    st.session_state.answers = {}
    st.session_state.checked = set()
    st.session_state.finished = False
    st.session_state.navigation = "문제 풀기"


def get_question(qid):
    for question in QUESTIONS:
        if question["id"] == qid:
            return question
    return None


def save_current_answer(qid):
    key = f"answer_{qid}"
    if key in st.session_state:
        st.session_state.answers[qid] = st.session_state[key]


def check_answer(qid):
    save_current_answer(qid)
    st.session_state.checked.add(qid)


def next_question(qid):
    save_current_answer(qid)
    st.session_state.quiz_index += 1


def previous_question(qid):
    save_current_answer(qid)
    st.session_state.quiz_index -= 1


def finish_quiz(qid):
    save_current_answer(qid)

    if st.session_state.finished:
        return

    questions = [
        get_question(i)
        for i in st.session_state.quiz_ids
    ]
    questions = [q for q in questions if q is not None]

    total = len(questions)

    correct = sum(
        1 for q in questions
        if st.session_state.answers.get(q["id"]) == q["answer"]
    )

    score = round(correct / total * 100) if total else 0

    st.session_state.history.append({
        "완료 시각": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "문제 수": total,
        "정답 수": correct,
        "점수": score
    })

    st.session_state.finished = True


# =====================================
# 디자인
# =====================================
st.markdown("""
<style>
.stApp {
    background-color: #f5f9ff;
}
.block-container {
    max-width: 1200px;
    padding-top: 2rem;
}
.hero {
    background: linear-gradient(120deg, #d8ebff, #eff7ff);
    border: 1px solid #b8d8f2;
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 20px;
}
.hero h1 {
    color: #204b70;
    margin-bottom: 5px;
}
.hero p {
    color: #45677f;
}
div.stButton > button {
    border-radius: 9px;
}
</style>
""", unsafe_allow_html=True)


# =====================================
# 왼쪽 메뉴
# 중요: navigation을 직접 연결해
# 페이지 이동이 유지되도록 합니다.
# =====================================
with st.sidebar:
    st.markdown("## 📚 기출문제 모음")
    st.caption("원하는 문제를 찾고 풀어보세요.")

    st.radio(
        "메뉴",
        ["문제 찾기", "문제 풀기", "학습 기록"],
        key="navigation"
    )

    st.divider()

    st.markdown("### 이용 방법")
    st.write("1. 원하는 과목과 연도를 선택하세요.")
    st.write("2. 문제 풀기를 눌러 답을 선택하세요.")
    st.write("3. 채점 후 정답과 해설을 확인하세요.")


# =====================================
# 상단 제목
# =====================================
st.markdown("""
<div class="hero">
    <h1>📘 기출문제 모음</h1>
    <p>과목 · 학년 · 연도별로 문제를 찾고 실력을 확인해 보세요!</p>
</div>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)

with c1:
    st.metric("전체 문제", f"{len(QUESTIONS)}개")

with c2:
    st.metric("과목 수", f"{len(SUBJECTS)}개")

with c3:
    st.metric("완료한 학습", f"{len(st.session_state.history)}회")


# =====================================
# 페이지 1: 문제 찾기
# =====================================
if st.session_state.navigation == "문제 찾기":

    st.subheader("🔎 기출문제 검색")

    search = st.text_input(
        "문제 검색",
        placeholder="문제 제목 또는 키워드를 입력하세요."
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        subject = st.selectbox(
            "과목",
            ["전체"] + SUBJECTS
        )

    with c2:
        grade = st.selectbox(
            "학년",
            ["전체", "1학년", "2학년", "3학년"]
        )

    with c3:
        years = sorted(
            {q["year"] for q in QUESTIONS},
            reverse=True
        )

        year = st.selectbox(
            "시험 연도",
            ["전체"] + years
        )

    with c4:
        exam = st.selectbox(
            "시험 종류",
            ["전체", "중간고사", "기말고사"]
        )

    # 검색 조건 적용
    filtered = QUESTIONS.copy()

    if search.strip():
        keyword = search.strip().lower()

        filtered = [
            q for q in filtered
            if keyword in q["title"].lower()
            or keyword in q["question"].lower()
            or keyword in q["subject"].lower()
        ]

    if subject != "전체":
        filtered = [
            q for q in filtered
            if q["subject"] == subject
        ]

    if grade != "전체":
        filtered = [
            q for q in filtered
            if q["grade"] == grade
        ]

    if year != "전체":
        filtered = [
            q for q in filtered
            if q["year"] == year
        ]

    if exam != "전체":
        filtered = [
            q for q in filtered
            if q["exam"] == exam
        ]

    st.markdown(f"### 검색 결과 {len(filtered)}개")

    if not filtered:
        st.info("검색 결과가 없습니다. 검색어나 필터를 바꿔보세요.")

    else:
        for q in filtered:

            with st.container(border=True):

                left, right = st.columns([5, 1.4])

                with left:
                    st.markdown(f"### {q['title']}")

                    st.caption(
                        f"{q['subject']} | {q['grade']} | "
                        f"{q['year']}년 | {q['exam']}"
                    )

                    st.write(q["question"])

                with right:
                    st.write("")

                    st.button(
                        "문제 풀기",
                        key=f"solve_{q['id']}",
                        use_container_width=True,
                        on_click=start_quiz,
                        args=([q["id"]],)
                    )

                    with st.expander("해설 보기"):
                        st.write(q["explanation"])

        st.button(
            "검색 결과 전체 풀기",
            type="primary",
            use_container_width=True,
            on_click=start_quiz,
            args=([q["id"] for q in filtered],)
        )


# =====================================
# 페이지 2: 문제 풀기
# =====================================
elif st.session_state.navigation == "문제 풀기":

    st.subheader("✏️ 문제 풀기")

    quiz_questions = [
        get_question(qid)
        for qid in st.session_state.quiz_ids
    ]

    quiz_questions = [
        q for q in quiz_questions
        if q is not None
    ]

    if not quiz_questions:

        st.info("아직 선택한 문제가 없습니다.")

        st.button(
            "문제 찾기",
            on_click=lambda: setattr(
                st.session_state, "navigation", "문제 찾기"
            )
        )

    elif st.session_state.finished:

        total = len(quiz_questions)

        correct = sum(
            1 for q in quiz_questions
            if st.session_state.answers.get(q["id"]) == q["answer"]
        )

        score = round(correct / total * 100) if total else 0

        st.success(
            f"채점 완료! 점수: {score}점 "
            f"({correct}/{total}문제 정답)"
        )

        for q in quiz_questions:

            with st.container(border=True):

                st.markdown(f"### {q['title']}")
                st.write(q["question"])

                chosen = st.session_state.answers.get(q["id"])

                if chosen == q["answer"]:
                    st.success(
                        f"정답: {q['choices'][q['answer']]}"
                    )
                elif chosen is None:
                    st.warning(
                        f"미응답 · 정답: {q['choices'][q['answer']]}"
                    )
                else:
                    st.error(
                        f"내 답: {q['choices'][chosen]} · "
                        f"정답: {q['choices'][q['answer']]}"
                    )

                st.info(f"해설: {q['explanation']}")

        st.button(
            "다른 문제 풀기",
            type="primary",
            on_click=lambda: setattr(
                st.session_state, "navigation", "문제 찾기"
            )
        )

    else:

        index = st.session_state.quiz_index
        q = quiz_questions[index]

        st.progress(
            (index + 1) / len(quiz_questions),
            text=f"{index + 1} / {len(quiz_questions)} 문제"
        )

        st.caption(
            f"{q['subject']} | {q['grade']} | "
            f"{q['year']}년 | {q['exam']}"
        )

        with st.container(border=True):

            st.markdown(f"### {q['title']}")
            st.markdown(
                f"**문제 {index + 1}.** {q['question']}"
            )

            # 답을 선택하는 영역
            st.radio(
                "정답을 선택하세요.",
                options=list(range(len(q["choices"]))),
                format_func=lambda i: (
                    f"{i + 1}. {q['choices'][i]}"
                ),
                key=f"answer_{q['id']}"
            )

            st.button(
                "정답 확인",
                key=f"check_{q['id']}",
                on_click=check_answer,
                args=(q["id"],)
            )

            # 정답 확인 버튼을 눌렀을 때만 결과 표시
            if q["id"] in st.session_state.checked:

                chosen = st.session_state.answers.get(q["id"])

                if chosen == q["answer"]:
                    st.success("정답입니다! 🎉")
                else:
                    st.error(
                        f"오답입니다. 정답은 "
                        f"{q['choices'][q['answer']]}입니다."
                    )

                st.info(f"해설: {q['explanation']}")

        prev_col, empty_col, next_col = st.columns([1, 2, 1])

        with prev_col:
            st.button(
                "← 이전",
                disabled=index == 0,
                use_container_width=True,
                on_click=previous_question,
                args=(q["id"],)
            )

        with next_col:

            if index < len(quiz_questions) - 1:

                st.button(
                    "다음 →",
                    use_container_width=True,
                    on_click=next_question,
                    args=(q["id"],)
                )

            else:

                st.button(
                    "채점하기",
                    type="primary",
                    use_container_width=True,
                    on_click=finish_quiz,
                    args=(q["id"],)
                )


# =====================================
# 페이지 3: 학습 기록
# =====================================
elif st.session_state.navigation == "학습 기록":

    st.subheader("📊 나의 학습 기록")

    if not st.session_state.history:

        st.info(
            "아직 학습 기록이 없습니다. "
            "문제를 풀고 채점하면 기록이 표시됩니다."
        )

    else:

        df = pd.DataFrame(st.session_state.history)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        c1, c2 = st.columns(2)

        with c1:
            st.metric(
                "평균 점수",
                f"{round(df['점수'].mean())}점"
            )

        with c2:
            st.metric(
                "최고 점수",
                f"{df['점수'].max()}점"
            )

        st.download_button(
            "학습 기록 다운로드",
            data=df.to_csv(
                index=False
            ).encode("utf-8-sig"),
            file_name="학습기록.csv",
            mime="text/csv"
        )


# =====================================
# 하단 안내
# =====================================
st.divider()

st.caption(
    "현재 제공되는 문제는 기능 확인용 예시 문제입니다. "
    "실제 학교 기출문제는 별도로 추가해야 합니다."
)
