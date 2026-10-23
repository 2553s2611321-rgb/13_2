import streamlit as st
import time

# =========================================================
# 페이지 설정
# =========================================================

st.set_page_config(
    page_title="공부 타이머",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =========================================================
# CSS
# 사진과 비슷한 3열 레이아웃
# =========================================================

st.markdown(
    """
    <style>

    /* 전체 */
    .stApp {
        background: white;
    }

    .block-container {
        max-width: 1200px;
        padding-top: 20px;
        padding-bottom: 30px;
        padding-left: 25px;
        padding-right: 25px;
    }

    /* Streamlit 기본 위아래 여백 줄이기 */
    div[data-testid="stVerticalBlock"] {
        gap: 0.5rem;
    }

    /* -----------------------------------------
       왼쪽 / 오른쪽 카드
       ----------------------------------------- */

    .side-card {
        border: 1px solid #d6d9de;
        border-radius: 12px;
        padding: 22px;
        background: #ffffff;
    }

    .side-title {
        font-size: 30px;
        font-weight: 800;
        color: #111111;
        margin-bottom: 20px;
    }

    /* -----------------------------------------
       가운데 제목
       ----------------------------------------- */

    .center-title {
        text-align: center;
        font-size: 38px;
        font-weight: 800;
        color: #111111;
        margin-bottom: 5px;
    }

    /* -----------------------------------------
       총 공부 시간
       ----------------------------------------- */

    .total-time {
        text-align: center;
        font-size: 42px;
        font-weight: 800;
        color: #2587df;
        margin-top: 0px;
        margin-bottom: 32px;
        letter-spacing: 1px;
    }

    /* -----------------------------------------
       구분선
       ----------------------------------------- */

    .blue-line {
        height: 2px;
        width: 100%;
        background: #a7c9f5;
        margin-top: 22px;
        margin-bottom: 22px;
    }

    /* -----------------------------------------
       타이머 원
       ----------------------------------------- */

    .timer-circle {
        width: 245px;
        height: 245px;
        border-radius: 50%;

        background: #ff0000;

        border: 7px solid #d52c2c;

        box-shadow:
            inset 0 0 0 2px white,
            0 0 0 1px #ffffff;

        margin: 25px auto 18px auto;

        display: flex;
        justify-content: center;
        align-items: center;

        position: relative;
    }

    .timer-dot {
        width: 11px;
        height: 11px;
        border-radius: 50%;
        background: white;
    }

    /* -----------------------------------------
       타이머 숫자
       ----------------------------------------- */

    .timer-number {
        text-align: center;
        font-family: monospace;
        font-size: 48px;
        font-weight: 900;
        color: #111111;
        letter-spacing: 1px;
        margin-top: 5px;
        margin-bottom: 22px;
    }

    /* -----------------------------------------
       과목 시간
       ----------------------------------------- */

    .subject-row {
        margin-bottom: 20px;
    }

    .subject-name {
        font-size: 19px;
        font-weight: 700;
        color: #333333;
        margin-bottom: 7px;
    }

    .subject-time {
        font-size: 17px;
        color: #333333;
    }

    .subject-progress {
        width: 100%;
        height: 11px;
        background: #edf0f4;
        border-radius: 20px;
        overflow: hidden;
        margin-top: 10px;
    }

    .subject-progress-inner {
        height: 100%;
        background: #2587df;
        border-radius: 20px;
    }

    /* -----------------------------------------
       할 일
       ----------------------------------------- */

    .todo-title {
        font-size: 22px;
        font-weight: 800;
        color: #333333;
        margin-top: 12px;
        margin-bottom: 12px;
    }

    /* -----------------------------------------
       모바일
       ----------------------------------------- */

    @media (max-width: 900px) {

        .center-title {
            font-size: 30px;
        }

        .total-time {
            font-size: 34px;
        }

        .timer-circle {
            width: 210px;
            height: 210px;
        }

        .timer-number {
            font-size: 40px;
        }
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# Session State
# =========================================================

if "tasks" not in st.session_state:
    st.session_state.tasks = [
        {
            "id": 1,
            "subject": "수학",
            "text": "수학 문제집 풀기",
            "done": False,
        },
        {
            "id": 2,
            "subject": "영어",
            "text": "영어 단어 암기",
            "done": False,
        },
    ]

if "next_task_id" not in st.session_state:
    st.session_state.next_task_id = 3

if "current_subject" not in st.session_state:
    st.session_state.current_subject = "수학"

if "subjects" not in st.session_state:
    st.session_state.subjects = {
        "수학": 0,
        "영어": 0,
        "국어": 0,
        "과학": 0,
        "사회": 0,
        "기타": 0,
    }

if "pomodoro_minutes" not in st.session_state:
    st.session_state.pomodoro_minutes = 25

if "timer_running" not in st.session_state:
    st.session_state.timer_running = False

if "timer_started_at" not in st.session_state:
    st.session_state.timer_started_at = None

if "timer_elapsed_before_pause" not in st.session_state:
    st.session_state.timer_elapsed_before_pause = 0

if "completed_pomodoro" not in st.session_state:
    st.session_state.completed_pomodoro = 0

# =========================================================
# 함수
# =========================================================

def format_hms(seconds):
    """초 → HH:MM:SS"""
    seconds = max(0, int(seconds))

    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60

    return f"{h:02d}:{m:02d}:{s:02d}"


def format_ms(seconds):
    """초 → MM:SS"""
    seconds = max(0, int(seconds))

    m = seconds // 60
    s = seconds % 60

    return f"{m:02d}:{s:02d}"


def get_elapsed():
    """현재 실행 중인 타이머의 누적 시간"""

    elapsed = st.session_state.timer_elapsed_before_pause

    if st.session_state.timer_running:
        if st.session_state.timer_started_at is not None:
            elapsed += time.time() - st.session_state.timer_started_at

    return int(elapsed)


def get_remaining():
    """뽀모도로 남은 시간"""

    total = st.session_state.pomodoro_minutes * 60
    elapsed = get_elapsed()

    return max(0, total - elapsed)


def add_study_time(seconds):
    """현재 과목에 공부 시간 추가"""

    if seconds <= 0:
        return

    subject = st.session_state.current_subject

    if subject not in st.session_state.subjects:
        st.session_state.subjects[subject] = 0

    st.session_state.subjects[subject] += int(seconds)


def reset_timer_state():
    """타이머 초기화"""

    st.session_state.timer_running = False
    st.session_state.timer_started_at = None
    st.session_state.timer_elapsed_before_pause = 0


# =========================================================
# 뽀모도로 완료 확인
# =========================================================

if st.session_state.timer_running:

    remaining = get_remaining()

    if remaining <= 0:

        # 25분 공부 시간 기록
        completed_seconds = (
            st.session_state.pomodoro_minutes * 60
        )

        add_study_time(completed_seconds)

        st.session_state.completed_pomodoro += 1

        reset_timer_state()

        st.toast("🎉 뽀모도로 완료!")

# =========================================================
# 전체 레이아웃
# =========================================================

left, center, right = st.columns(
    [1.05, 1.35, 1.05],
    gap="large",
)

# =========================================================
# 왼쪽
# =========================================================

with left:

    # ---------------------------------------------
    # 공부 리스트
    # ---------------------------------------------

    st.markdown(
        """
        <div class="side-card">
            <div class="side-title">
                공부 리스트
            </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form(
        "add_task",
        clear_on_submit=True,
    ):

        subject = st.text_input(
            "과목명",
            placeholder="예: 국어",
        )

        task = st.text_input(
            "할 일",
            placeholder="예: 비문학 3지문 풀기",
        )

        add_button = st.form_submit_button(
            "추가",
            use_container_width=False,
        )

        if add_button:

            subject = subject.strip()
            task = task.strip()

            if not subject:
                st.warning("과목명을 입력해주세요.")

            elif not task:
                st.warning("할 일을 입력해주세요.")

            else:

                st.session_state.tasks.append(
                    {
                        "id": st.session_state.next_task_id,
                        "subject": subject,
                        "text": task,
                        "done": False,
                    }
                )

                st.session_state.next_task_id += 1

                if subject not in st.session_state.subjects:
                    st.session_state.subjects[subject] = 0

                st.rerun()

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )

    # ---------------------------------------------
    # 구분선
    # ---------------------------------------------

    st.markdown(
        '<div class="blue-line"></div>',
        unsafe_allow_html=True,
    )

    # ---------------------------------------------
    # 현재 학습 과목
    # ---------------------------------------------

    st.markdown(
        "현재 학습 과목"
    )

    subject_list = list(
        st.session_state.subjects.keys()
    )

    if not subject_list:
        subject_list = ["기타"]

    if (
        st.session_state.current_subject
        not in subject_list
    ):
        st.session_state.current_subject = (
            subject_list[0]
        )

    selected = st.selectbox(
        "현재 과목",
        subject_list,
        index=subject_list.index(
            st.session_state.current_subject
        ),
        label_visibility="collapsed",
    )

    if selected != st.session_state.current_subject:

        # 과목 변경 시 타이머를 안전하게 초기화
        reset_timer_state()

        st.session_state.current_subject = selected

    # ---------------------------------------------
    # 할 일 목록
    # ---------------------------------------------

    st.markdown(
        '<div class="todo-title">할 일 목록</div>',
        unsafe_allow_html=True,
    )

    if not st.session_state.tasks:

        st.info("등록된 할 일이 없습니다.")

    else:

        for item in st.session_state.tasks:

            check_col, text_col, delete_col = st.columns(
                [0.12, 0.70, 0.18]
            )

            with check_col:

                checked = st.checkbox(
                    "완료",
                    value=item["done"],
                    key=f"check_{item['id']}",
                    label_visibility="collapsed",
                )

                if checked != item["done"]:
                    item["done"] = checked

            with text_col:

                if item["done"]:

                    st.markdown(
                        f"""
                        <span style="
                            color:#999;
                            text-decoration:line-through;
                        ">
                            [{item['subject']}] {item['text']}
                        </span>
                        """,
                        unsafe_allow_html=True,
                    )

                else:

                    st.markdown(
                        f"""
                        [{item['subject']}] {item['text']}
                        """
                    )

            with delete_col:

                if st.button(
                    "×",
                    key=f"delete_{item['id']}",
                ):

                    st.session_state.tasks = [
                        x
                        for x in st.session_state.tasks
                        if x["id"] != item["id"]
                    ]

                    st.rerun()


# =========================================================
# 가운데
# =========================================================

with center:

    st.markdown(
        '<div class="center-title">총 공부 시간</div>',
        unsafe_allow_html=True,
    )

    # 총 공부 시간
    total_study = sum(
        st.session_state.subjects.values()
    )

    st.markdown(
        f"""
        <div class="total-time">
            {format_hms(total_study)}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---------------------------------------------
    # 시계 기능 선택
    # ---------------------------------------------

    st.markdown(
        "시계 기능 선택"
    )

    st.radio(
        "timer_mode",
        [
            "뽀모도로 타이머",
            "공부 시간 측정",
        ],
        index=0,
        horizontal=True,
        label_visibility="collapsed",
    )

    # 사진과 동일한 기본 형태를 위해
    # 뽀모도로 타이머를 중심으로 구현
    # ---------------------------------------------

    st.markdown(
        "<br>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "뽀모도로 설정(분)"
    )

    # ---------------------------------------------
    # 25분 - +
    # ---------------------------------------------

    minus, number, plus = st.columns(
        [1, 7, 1]
    )

    with minus:

        if st.button(
            "−",
            key="minus",
            use_container_width=True,
        ):

            if not st.session_state.timer_running:

                st.session_state.pomodoro_minutes = max(
                    1,
                    st.session_state.pomodoro_minutes - 5,
                )

                st.rerun()

    with number:

        st.markdown(
            f"""
            <div style="
                background:#eef0f4;
                border-radius:10px;
                padding:12px 16px;
                font-size:18px;
                color:#333;
            ">
                {st.session_state.pomodoro_minutes}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with plus:

        if st.button(
            "+",
            key="plus",
            use_container_width=True,
        ):

            if not st.session_state.timer_running:

                st.session_state.pomodoro_minutes = min(
                    120,
                    st.session_state.pomodoro_minutes + 5,
                )

                st.rerun()

    # ---------------------------------------------
    # 원형 타이머
    # ---------------------------------------------

    remaining = get_remaining()

    st.markdown(
        f"""
        <div class="timer-circle">
            <div class="timer-dot"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="timer-number">
            {format_hms(remaining)}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---------------------------------------------
    # 버튼
    # ---------------------------------------------

    start, pause, reset = st.columns(
        3,
        gap="small",
    )

    with start:

        if st.button(
            "시작",
            use_container_width=True,
            type="secondary",
        ):

            if not st.session_state.timer_running:

                st.session_state.timer_running = True

                st.session_state.timer_started_at = (
                    time.time()
                )

                st.rerun()

    with pause:

        if st.button(
            "일시정지",
            use_container_width=True,
        ):

            if st.session_state.timer_running:

                # 현재까지의 시간 저장
                st.session_state.timer_elapsed_before_pause = (
                    get_elapsed()
                )

                st.session_state.timer_running = False

                st.session_state.timer_started_at = None

                st.rerun()

    with reset:

        if st.button(
            "리셋",
            use_container_width=True,
        ):

            reset_timer_state()

            st.rerun()

    # ---------------------------------------------
    # 완료한 뽀모도로
    # ---------------------------------------------

    st.markdown(
        f"""
        <div style="
            text-align:center;
            margin-top:18px;
            color:#777;
            font-size:14px;
        ">
            완료한 뽀모도로: 
            <b>{st.session_state.completed_pomodoro}</b>회
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# 오른쪽
# =========================================================

with right:

    st.markdown(
        """
        <div class="side-card">
            <div class="side-title">
                과목별 공부 시간
            </div>
        """,
        unsafe_allow_html=True,
    )

    # 가장 많이 공부한 과목을 기준으로
    # 진행률 계산
    max_time = max(
        st.session_state.subjects.values()
    ) if st.session_state.subjects else 1

    if max_time <= 0:
        max_time = 1

    for subject, seconds in (
        st.session_state.subjects.items()
    ):

        percentage = (
            seconds / max_time
        ) * 100

        percentage = min(
            100,
            max(0, percentage),
        )

        st.markdown(
            f"""
            <div class="subject-row">

                <div class="subject-name">
                    {subject}:
                    <span style="
                        font-weight:400;
                    ">
                        {format_hms(seconds)}
                    </span>
                </div>

                <div class="subject-progress">
                    <div
                        class="subject-progress-inner"
                        style="width:{percentage}%"
                    ></div>
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )


# =========================================================
# 타이머 실행 중이면 1초마다 갱신
# =========================================================

if st.session_state.timer_running:

    time.sleep(1)

    st.rerun()
