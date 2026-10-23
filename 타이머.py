import streamlit as st
import time
from datetime import datetime

# =========================================================
# 기본 설정
# =========================================================

st.set_page_config(
    page_title="Study Timer",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =========================================================
# CSS
# =========================================================

st.markdown(
    """
    <style>
    /* 전체 배경 */
    .stApp {
        background-color: #ffffff;
    }

    /* 기본 여백 */
    .block-container {
        max-width: 1250px;
        padding-top: 30px;
        padding-bottom: 40px;
    }

    /* 제목 */
    .main-title {
        font-size: 42px;
        font-weight: 800;
        color: #111111;
        margin-bottom: 25px;
    }

    /* 카드 */
    .card {
        border: 1px solid #d8dce2;
        border-radius: 14px;
        padding: 24px;
        background: white;
        margin-bottom: 20px;
    }

    /* 카드 제목 */
    .card-title {
        font-size: 30px;
        font-weight: 800;
        color: #111111;
        margin-bottom: 20px;
    }

    /* 파란 구분선 */
    .blue-line {
        height: 2px;
        background: #9ec5ff;
        margin: 25px 0;
    }

    /* 총 공부 시간 */
    .total-time {
        text-align: center;
        font-size: 54px;
        font-weight: 800;
        color: #2585df;
        letter-spacing: 2px;
        margin: 10px 0 25px 0;
    }

    /* 타이머 */
    .timer {
        text-align: center;
        font-size: 58px;
        font-weight: 800;
        color: #111111;
        letter-spacing: 3px;
        margin: 15px 0;
    }

    /* 원형 타이머 */
    .timer-circle {
        width: 245px;
        height: 245px;
        border-radius: 50%;
        margin: 20px auto;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 7px solid #e12b2b;
        background: #ff0000;
        box-shadow: inset 0 0 0 3px white;
    }

    .timer-circle-text {
        color: white;
        font-size: 34px;
        font-weight: 800;
    }

    /* 과목 시간 */
    .subject-name {
        font-size: 18px;
        font-weight: 700;
        color: #30343b;
    }

    .subject-time {
        font-size: 16px;
        color: #30343b;
        margin-bottom: 8px;
    }

    /* 진행바 */
    .progress-bg {
        width: 100%;
        height: 11px;
        background: #eef0f3;
        border-radius: 10px;
        overflow: hidden;
        margin-bottom: 22px;
    }

    .progress-fill {
        height: 100%;
        background: #4d9bea;
        border-radius: 10px;
    }

    /* 통계 */
    .stat-box {
        background: #f5f7fa;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        margin-bottom: 10px;
    }

    .stat-number {
        font-size: 25px;
        font-weight: 800;
        color: #2585df;
    }

    .stat-label {
        color: #555;
        font-size: 14px;
    }

    /* Streamlit 버튼 */
    div.stButton > button {
        border-radius: 10px;
        min-height: 42px;
        font-size: 16px;
    }

    /* 체크박스 */
    div[data-testid="stCheckbox"] {
        padding-top: 4px;
    }

    /* 모바일 대응 */
    @media (max-width: 900px) {
        .main-title {
            font-size: 32px;
        }

        .total-time {
            font-size: 40px;
        }

        .timer {
            font-size: 44px;
        }

        .timer-circle {
            width: 200px;
            height: 200px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# Session State 초기화
# =========================================================

if "tasks" not in st.session_state:
    st.session_state.tasks = [
        {
            "id": 1,
            "subject": "수학",
            "task": "수학 문제집 풀기",
            "done": False,
        },
        {
            "id": 2,
            "subject": "영어",
            "task": "영어 단어 암기",
            "done": False,
        },
    ]

if "subject_times" not in st.session_state:
    st.session_state.subject_times = {
        "수학": 0,
        "영어": 0,
        "국어": 0,
        "과학": 0,
        "사회": 0,
        "기타": 0,
    }

if "total_study_seconds" not in st.session_state:
    st.session_state.total_study_seconds = 0

if "timer_running" not in st.session_state:
    st.session_state.timer_running = False

if "timer_mode" not in st.session_state:
    st.session_state.timer_mode = "pomodoro"

if "pomodoro_minutes" not in st.session_state:
    st.session_state.pomodoro_minutes = 25

if "timer_seconds" not in st.session_state:
    st.session_state.timer_seconds = 25 * 60

if "timer_started_at" not in st.session_state:
    st.session_state.timer_started_at = None

if "timer_accumulated" not in st.session_state:
    st.session_state.timer_accumulated = 0

if "current_subject" not in st.session_state:
    st.session_state.current_subject = "수학"

if "pomodoro_count" not in st.session_state:
    st.session_state.pomodoro_count = 0

if "timer_phase" not in st.session_state:
    st.session_state.timer_phase = "집중"

if "next_id" not in st.session_state:
    st.session_state.next_id = 3


# =========================================================
# 함수
# =========================================================

def format_time(seconds):
    """초를 HH:MM:SS 형태로 변환"""
    seconds = max(0, int(seconds))

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def format_timer(seconds):
    """뽀모도로 MM:SS"""
    seconds = max(0, int(seconds))

    minutes = seconds // 60
    secs = seconds % 60

    return f"{minutes:02d}:{secs:02d}"


def add_study_time(seconds):
    """현재 과목에 공부 시간 추가"""
    if seconds <= 0:
        return

    subject = st.session_state.current_subject

    if subject not in st.session_state.subject_times:
        st.session_state.subject_times[subject] = 0

    st.session_state.subject_times[subject] += seconds
    st.session_state.total_study_seconds += seconds


def start_timer():
    """타이머 시작"""
    if not st.session_state.timer_running:
        st.session_state.timer_running = True
        st.session_state.timer_started_at = time.time()


def pause_timer():
    """타이머 일시정지"""
    if st.session_state.timer_running:
        now = time.time()

        elapsed = now - st.session_state.timer_started_at

        st.session_state.timer_accumulated += elapsed
        st.session_state.timer_running = False
        st.session_state.timer_started_at = None


def reset_timer():
    """타이머 리셋"""
    st.session_state.timer_running = False
    st.session_state.timer_started_at = None
    st.session_state.timer_accumulated = 0

    if st.session_state.timer_mode == "pomodoro":
        st.session_state.timer_seconds = (
            st.session_state.pomodoro_minutes * 60
        )
    else:
        st.session_state.timer_seconds = 0


def get_current_timer_seconds():
    """현재 타이머의 남은 시간을 계산"""
    if st.session_state.timer_mode == "pomodoro":
        total = st.session_state.pomodoro_minutes * 60

        if st.session_state.timer_running:
            elapsed = (
                time.time()
                - st.session_state.timer_started_at
                + st.session_state.timer_accumulated
            )
        else:
            elapsed = st.session_state.timer_accumulated

        return max(0, total - int(elapsed))

    # 공부 시간 측정 모드
    if st.session_state.timer_running:
        elapsed = (
            time.time()
            - st.session_state.timer_started_at
            + st.session_state.timer_accumulated
        )
        return int(elapsed)

    return int(st.session_state.timer_accumulated)


def change_pomodoro_minutes(value):
    """뽀모도로 시간 변경"""
    new_value = st.session_state.pomodoro_minutes + value

    new_value = max(1, min(120, new_value))

    # 실행 중이 아닐 때만 시간 변경
    if not st.session_state.timer_running:
        st.session_state.pomodoro_minutes = new_value
        st.session_state.timer_seconds = new_value * 60
        st.session_state.timer_accumulated = 0


# =========================================================
# 타이머 자동 업데이트
# =========================================================

if st.session_state.timer_running:
    current_seconds = get_current_timer_seconds()

    if st.session_state.timer_mode == "pomodoro" and current_seconds <= 0:
        # 뽀모도로 한 세트 완료
        add_study_time(
            st.session_state.pomodoro_minutes * 60
        )

        st.session_state.pomodoro_count += 1

        st.session_state.timer_running = False
        st.session_state.timer_started_at = None
        st.session_state.timer_accumulated = 0
        st.session_state.timer_seconds = (
            st.session_state.pomodoro_minutes * 60
        )

        st.session_state.timer_phase = "완료"

        st.toast("🎉 뽀모도로 한 세트를 완료했어요!")

# =========================================================
# 상단 제목
# =========================================================

st.markdown(
    '<div class="main-title">📚 공부 타이머</div>',
    unsafe_allow_html=True,
)

# =========================================================
# 화면 2분할
# =========================================================

left_col, right_col = st.columns([1, 1.35], gap="large")


# =========================================================
# 왼쪽 영역
# 공부 리스트 + 과목별 공부 시간
# =========================================================

with left_col:

    # -----------------------------------------------------
    # 공부 리스트
    # -----------------------------------------------------

    st.markdown(
        """
        <div class="card">
            <div class="card-title">공부 리스트</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 입력 영역
    with st.form("add_task_form", clear_on_submit=True):

        subject = st.selectbox(
            "과목명",
            [
                "수학",
                "영어",
                "국어",
                "과학",
                "사회",
                "기타",
            ],
        )

        task_text = st.text_input(
            "할 일",
            placeholder="예: 비문학 3지문 풀기",
        )

        submitted = st.form_submit_button(
            "＋ 추가",
            use_container_width=True,
        )

        if submitted:
            if not task_text.strip():
                st.warning("할 일을 입력해주세요.")
            else:
                st.session_state.tasks.append(
                    {
                        "id": st.session_state.next_id,
                        "subject": subject,
                        "task": task_text.strip(),
                        "done": False,
                    }
                )

                st.session_state.next_id += 1

                if subject not in st.session_state.subject_times:
                    st.session_state.subject_times[subject] = 0

                st.rerun()

    st.markdown(
        '<div class="blue-line"></div>',
        unsafe_allow_html=True,
    )

    # -----------------------------------------------------
    # 현재 공부 과목
    # -----------------------------------------------------

    subjects = list(st.session_state.subject_times.keys())

    current_index = (
        subjects.index(st.session_state.current_subject)
        if st.session_state.current_subject in subjects
        else 0
    )

    selected_subject = st.selectbox(
        "현재 학습 과목",
        subjects,
        index=current_index,
    )

    if selected_subject != st.session_state.current_subject:

        # 과목이 변경되면 진행 중 타이머 정지
        if st.session_state.timer_running:
            pause_timer()

        st.session_state.current_subject = selected_subject

    # -----------------------------------------------------
    # 할 일 목록
    # -----------------------------------------------------

    st.markdown(
        "### 할 일 목록"
    )

    if not st.session_state.tasks:
        st.info("등록된 공부가 없습니다.")

    else:
        for task in st.session_state.tasks:

            col_check, col_text, col_delete = st.columns(
                [0.12, 0.70, 0.18]
            )

            with col_check:

                checked = st.checkbox(
                    "완료",
                    value=task["done"],
                    key=f"check_{task['id']}",
                    label_visibility="collapsed",
                )

                if checked != task["done"]:
                    task["done"] = checked

            with col_text:

                if task["done"]:
                    st.markdown(
                        f"~~[{task['subject']}] {task['task']}~~"
                    )
                else:
                    st.markdown(
                        f"**[{task['subject']}]** {task['task']}"
                    )

            with col_delete:

                if st.button(
                    "삭제",
                    key=f"delete_{task['id']}",
                ):
                    st.session_state.tasks = [
                        x
                        for x in st.session_state.tasks
                        if x["id"] != task["id"]
                    ]

                    st.rerun()

    # -----------------------------------------------------
    # 과목별 공부 시간
    # -----------------------------------------------------

    st.markdown(
        '<div class="blue-line"></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        "### 과목별 공부 시간"
    )

    total_seconds = max(
        1,
        st.session_state.total_study_seconds,
    )

    for subject_name, seconds in (
        st.session_state.subject_times.items()
    ):

        if seconds <= 0:
            percentage = 0
        else:
            percentage = min(
                100,
                (seconds / total_seconds) * 100,
            )

        st.markdown(
            f"""
            <div class="subject-name">
                {subject_name}
            </div>
            <div class="subject-time">
                {format_time(seconds)}
            </div>
            <div class="progress-bg">
                <div
                    class="progress-fill"
                    style="width:{percentage}%"
                ></div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# =========================================================
# 오른쪽 영역
# 총 공부 시간 + 뽀모도로
# =========================================================

with right_col:

    # -----------------------------------------------------
    # 총 공부 시간
    # -----------------------------------------------------

    st.markdown(
        '<div class="card-title">총 공부 시간</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="total-time">
            {format_time(st.session_state.total_study_seconds)}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # -----------------------------------------------------
    # 통계
    # -----------------------------------------------------

    stat1, stat2, stat3 = st.columns(3)

    with stat1:
        st.markdown(
            f"""
            <div class="stat-box">
                <div class="stat-number">
                    {st.session_state.pomodoro_count}
                </div>
                <div class="stat-label">
                    완료한 뽀모도로
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with stat2:
        completed = sum(
            1
            for task in st.session_state.tasks
            if task["done"]
        )

        st.markdown(
            f"""
            <div class="stat-box">
                <div class="stat-number">
                    {completed}
                </div>
                <div class="stat-label">
                    완료한 할 일
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with stat3:
        st.markdown(
            f"""
            <div class="stat-box">
                <div class="stat-number">
                    {st.session_state.current_subject}
                </div>
                <div class="stat-label">
                    현재 과목
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # -----------------------------------------------------
    # 시계 기능 선택
    # -----------------------------------------------------

    st.markdown(
        "### 시계 기능 선택"
    )

    mode = st.radio(
        "",
        [
            "뽀모도로 타이머",
            "공부 시간 측정",
        ],
        horizontal=True,
        label_visibility="collapsed",
    )

    new_mode = (
        "pomodoro"
        if mode == "뽀모도로 타이머"
        else "stopwatch"
    )

    if new_mode != st.session_state.timer_mode:

        # 실행 중이면 정지
        if st.session_state.timer_running:
            pause_timer()

        st.session_state.timer_mode = new_mode
        st.session_state.timer_accumulated = 0
        st.session_state.timer_started_at = None

        if new_mode == "pomodoro":
            st.session_state.timer_seconds = (
                st.session_state.pomodoro_minutes * 60
            )
        else:
            st.session_state.timer_seconds = 0

    # -----------------------------------------------------
    # 뽀모도로 설정
    # -----------------------------------------------------

    if st.session_state.timer_mode == "pomodoro":

        st.markdown(
            "### 뽀모도로 설정(분)"
        )

        minus_col, number_col, plus_col = st.columns(
            [1, 5, 1]
        )

        with minus_col:
            if st.button(
                "−",
                use_container_width=True,
            ):
                change_pomodoro_minutes(-5)
                st.rerun()

        with number_col:
            st.markdown(
                f"""
                <div style="
                    background:#f0f2f5;
                    border-radius:10px;
                    padding:10px;
                    text-align:center;
                    font-size:20px;
                    font-weight:700;
                ">
                    {st.session_state.pomodoro_minutes}분
                </div>
                """,
                unsafe_allow_html=True,
            )

        with plus_col:
            if st.button(
                "+",
                use_container_width=True,
            ):
                change_pomodoro_minutes(5)
                st.rerun()

        # -------------------------------------------------
        # 뽀모도로 원
        # -------------------------------------------------

        remaining = get_current_timer_seconds()

        progress = 1 - (
            remaining
            / max(
                1,
                st.session_state.pomodoro_minutes * 60,
            )
        )

        progress = max(
            0,
            min(1, progress),
        )

        st.markdown(
            f"""
            <div class="timer-circle">
                <div class="timer-circle-text">
                    {format_timer(remaining)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="timer">
                {format_timer(remaining)}
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.progress(
            progress,
            text=f"{int(progress * 100)}% 진행",
        )

    # -----------------------------------------------------
    # 공부 시간 측정
    # -----------------------------------------------------

    else:

        current = get_current_timer_seconds()

        st.markdown(
            f"""
            <div class="timer-circle"
                 style="
                    background:#2585df;
                    border-color:#2585df;
                 ">
                <div class="timer-circle-text">
                    {format_time(current)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="timer">
                {format_time(current)}
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.info(
            f"현재 과목: {st.session_state.current_subject}"
        )

    # -----------------------------------------------------
    # 타이머 버튼
    # -----------------------------------------------------

    start_col, pause_col, reset_col = st.columns(3)

    with start_col:

        if st.button(
            "▶ 시작",
            use_container_width=True,
            type="primary",
        ):
            start_timer()
            st.rerun()

    with pause_col:

        if st.button(
            "⏸ 일시정지",
            use_container_width=True,
        ):
            pause_timer()

            # 측정 모드에서는 일시정지한 시간을 기록
            if st.session_state.timer_mode == "stopwatch":

                elapsed = st.session_state.timer_accumulated

                if elapsed > 0:
                    add_study_time(int(elapsed))

                    st.session_state.timer_accumulated = 0

            st.rerun()

    with reset_col:

        if st.button(
            "↻ 리셋",
            use_container_width=True,
        ):
            reset_timer()
            st.rerun()

    # -----------------------------------------------------
    # 초기화
    # -----------------------------------------------------

    st.markdown("---")

    if st.button(
        "🗑 오늘 공부 기록 전체 초기화",
        use_container_width=True,
    ):

        st.session_state.total_study_seconds = 0

        for subject in st.session_state.subject_times:
            st.session_state.subject_times[subject] = 0

        st.session_state.pomodoro_count = 0

        reset_timer()

        st.toast("오늘의 공부 기록을 초기화했습니다.")

        st.rerun()


# =========================================================
# 자동 새로고침
# =========================================================

# 타이머가 실행 중일 때 1초마다 화면을 다시 실행
if st.session_state.timer_running:

    time.sleep(1)
    st.rerun()
