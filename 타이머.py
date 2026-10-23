import streamlit as st
import time

# =========================================================
# 페이지 설정
# =========================================================

st.set_page_config(
    page_title="공부 타이머",
    page_icon="📚",
    layout="wide",
)

# =========================================================
# CSS
# =========================================================

st.markdown("""
<style>

.stApp {
    background: white;
}

.block-container {
    max-width: 1250px;
    padding-top: 25px;
    padding-bottom: 40px;
}

/* 왼쪽 / 오른쪽 카드 */
.side-card {
    border: 1px solid #d5d9df;
    border-radius: 12px;
    padding: 20px;
    background: white;
}

.side-title {
    font-size: 30px;
    font-weight: 800;
    margin-bottom: 20px;
}

/* 가운데 제목 */
.center-title {
    text-align: center;
    font-size: 38px;
    font-weight: 800;
    margin-bottom: 5px;
}

/* 총 공부 시간 */
.total-time {
    text-align: center;
    font-size: 42px;
    font-weight: 800;
    color: #2585df;
    margin-bottom: 28px;
}

/* 파란 선 */
.blue-line {
    height: 2px;
    background: #a9c9f5;
    margin: 22px 0;
}

/* 타이머 */
.timer-circle {
    width: 245px;
    height: 245px;
    border-radius: 50%;
    background: #ff0000;
    border: 7px solid #d52c2c;
    box-shadow:
        inset 0 0 0 2px white,
        0 0 0 1px white;
    margin: 25px auto 20px auto;

    display: flex;
    align-items: center;
    justify-content: center;
}

.timer-dot {
    width: 11px;
    height: 11px;
    background: white;
    border-radius: 50%;
}

.timer-number {
    text-align: center;
    font-family: monospace;
    font-size: 48px;
    font-weight: 900;
    margin-bottom: 25px;
}

/* 과목별 공부 시간 */
.subject-row {
    margin-bottom: 21px;
}

.subject-name {
    font-size: 18px;
    font-weight: 700;
    margin-bottom: 7px;
}

.subject-progress {
    width: 100%;
    height: 10px;
    background: #edf0f4;
    border-radius: 20px;
    overflow: hidden;
}

.subject-progress-inner {
    height: 100%;
    background: #2585df;
    border-radius: 20px;
}

/* 할 일 */
.todo-title {
    font-size: 22px;
    font-weight: 800;
    margin: 15px 0;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# Session State
# =========================================================

if "tasks" not in st.session_state:
    st.session_state.tasks = [
        {
            "id": 1,
            "subject": "수학",
            "text": "수학 문제집 풀기",
            "done": False
        },
        {
            "id": 2,
            "subject": "영어",
            "text": "영어 단어 암기",
            "done": False
        }
    ]

# ---------------------------------------------------------
# 이전 버전의 데이터가 남아 있어도 오류가 발생하지 않도록
# 자동으로 변환
# ---------------------------------------------------------

for item in st.session_state.tasks:

    # 이전 버전에서 task를 사용했다면 text로 변환
    if "text" not in item:

        if "task" in item:
            item["text"] = item["task"]

        else:
            item["text"] = "할 일"

    # subject가 없는 경우
    if "subject" not in item:
        item["subject"] = "기타"

    # done이 없는 경우
    if "done" not in item:
        item["done"] = False

    # id가 없는 경우
    if "id" not in item:
        item["id"] = len(st.session_state.tasks) + 1


if "next_task_id" not in st.session_state:
    st.session_state.next_task_id = 100


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


if "timer_elapsed" not in st.session_state:
    st.session_state.timer_elapsed = 0


if "completed_pomodoro" not in st.session_state:
    st.session_state.completed_pomodoro = 0


# =========================================================
# 함수
# =========================================================

def format_time(seconds):
    seconds = max(0, int(seconds))

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60

    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def get_elapsed():

    elapsed = st.session_state.timer_elapsed

    if st.session_state.timer_running:

        if st.session_state.timer_started_at is not None:

            elapsed += (
                time.time()
                - st.session_state.timer_started_at
            )

    return int(elapsed)


def get_remaining():

    total = st.session_state.pomodoro_minutes * 60

    return max(
        0,
        total - get_elapsed()
    )


def reset_timer():

    st.session_state.timer_running = False
    st.session_state.timer_started_at = None
    st.session_state.timer_elapsed = 0


def add_study_time(seconds):

    if seconds <= 0:
        return

    subject = st.session_state.current_subject

    if subject not in st.session_state.subjects:
        st.session_state.subjects[subject] = 0

    st.session_state.subjects[subject] += int(seconds)


# =========================================================
# 뽀모도로 완료 확인
# =========================================================

if st.session_state.timer_running:

    remaining = get_remaining()

    if remaining <= 0:

        study_seconds = (
            st.session_state.pomodoro_minutes * 60
        )

        add_study_time(study_seconds)

        st.session_state.completed_pomodoro += 1

        reset_timer()

        st.toast("🎉 뽀모도로 완료!")


# =========================================================
# 3열 구조
# =========================================================

left, center, right = st.columns(
    [1.05, 1.35, 1.05],
    gap="large"
)


# =========================================================
# 왼쪽
# =========================================================

with left:

    # -----------------------------------------------------
    # 공부 리스트
    # -----------------------------------------------------

    st.markdown(
        """
        <div class="side-card">
            <div class="side-title">
                공부 리스트
            </div>
        """,
        unsafe_allow_html=True
    )

    with st.form(
        "add_task_form",
        clear_on_submit=True
    ):

        subject_input = st.text_input(
            "과목명",
            placeholder="예: 국어"
        )

        task_input = st.text_input(
            "할 일",
            placeholder="예: 비문학 3지문 풀기"
        )

        add = st.form_submit_button(
            "추가"
        )

        if add:

            subject_input = subject_input.strip()
            task_input = task_input.strip()

            if not subject_input:

                st.warning("과목명을 입력해주세요.")

            elif not task_input:

                st.warning("할 일을 입력해주세요.")

            else:

                st.session_state.tasks.append({
                    "id": st.session_state.next_task_id,
                    "subject": subject_input,
                    "text": task_input,
                    "done": False
                })

                st.session_state.next_task_id += 1

                if subject_input not in st.session_state.subjects:
                    st.session_state.subjects[
                        subject_input
                    ] = 0

                st.rerun()

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )

    # -----------------------------------------------------
    # 구분선
    # -----------------------------------------------------

    st.markdown(
        '<div class="blue-line"></div>',
        unsafe_allow_html=True
    )

    # -----------------------------------------------------
    # 현재 학습 과목
    # -----------------------------------------------------

    st.markdown("현재 학습 과목")

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

    selected_subject = st.selectbox(
        "현재 과목",
        subject_list,
        index=subject_list.index(
            st.session_state.current_subject
        ),
        label_visibility="collapsed"
    )

    if selected_subject != st.session_state.current_subject:

        reset_timer()

        st.session_state.current_subject = (
            selected_subject
        )

    # -----------------------------------------------------
    # 할 일 목록
    # -----------------------------------------------------

    st.markdown(
        '<div class="todo-title">할 일 목록</div>',
        unsafe_allow_html=True
    )

    if not st.session_state.tasks:

        st.info("등록된 할 일이 없습니다.")

    else:

        for item in st.session_state.tasks:

            check_col, text_col, delete_col = st.columns(
                [0.12, 0.73, 0.15]
            )

            # 체크박스
            with check_col:

                checked = st.checkbox(
                    "완료",
                    value=bool(item.get("done", False)),
                    key=f"check_{item['id']}",
                    label_visibility="collapsed"
                )

                item["done"] = checked

            # 할 일
            with text_col:

                subject_name = item.get(
                    "subject",
                    "기타"
                )

                task_name = item.get(
                    "text",
                    item.get("task", "할 일")
                )

                if item["done"]:

                    st.markdown(
                        f"""
                        <span style="
                            color:#999;
                            text-decoration:line-through;
                        ">
                        [{subject_name}] {task_name}
                        </span>
                        """,
                        unsafe_allow_html=True
                    )

                else:

                    st.markdown(
                        f"[{subject_name}] {task_name}"
                    )

            # 삭제
            with delete_col:

                if st.button(
                    "×",
                    key=f"delete_{item['id']}"
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
        unsafe_allow_html=True
    )

    total_time = sum(
        st.session_state.subjects.values()
    )

    st.markdown(
        f"""
        <div class="total-time">
            {format_time(total_time)}
        </div>
        """,
        unsafe_allow_html=True
    )

    # -----------------------------------------------------
    # 시계 기능
    # -----------------------------------------------------

    st.markdown("시계 기능 선택")

    st.radio(
        "timer_mode",
        [
            "뽀모도로 타이머",
            "공부 시간 측정"
        ],
        horizontal=True,
        label_visibility="collapsed"
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # -----------------------------------------------------
    # 뽀모도로 설정
    # -----------------------------------------------------

    st.markdown("뽀모도로 설정(분)")

    minus, number, plus = st.columns(
        [1, 7, 1]
    )

    with minus:

        if st.button(
            "−",
            use_container_width=True
        ):

            if not st.session_state.timer_running:

                st.session_state.pomodoro_minutes = max(
                    1,
                    st.session_state.pomodoro_minutes - 5
                )

                st.rerun()

    with number:

        st.markdown(
            f"""
            <div style="
                background:#eef0f4;
                border-radius:10px;
                padding:12px;
                font-size:18px;
            ">
                {st.session_state.pomodoro_minutes}
            </div>
            """,
            unsafe_allow_html=True
        )

    with plus:

        if st.button(
            "+",
            use_container_width=True
        ):

            if not st.session_state.timer_running:

                st.session_state.pomodoro_minutes = min(
                    120,
                    st.session_state.pomodoro_minutes + 5
                )

                st.rerun()

    # -----------------------------------------------------
    # 빨간 타이머
    # -----------------------------------------------------

    remaining = get_remaining()

    st.markdown(
        """
        <div class="timer-circle">
            <div class="timer-dot"></div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="timer-number">
            {format_time(remaining)}
        </div>
        """,
        unsafe_allow_html=True
    )

    # -----------------------------------------------------
    # 버튼
    # -----------------------------------------------------

    start, pause, reset = st.columns(3)

    with start:

        if st.button(
            "시작",
            use_container_width=True
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
            use_container_width=True
        ):

            if st.session_state.timer_running:

                st.session_state.timer_elapsed = (
                    get_elapsed()
                )

                st.session_state.timer_running = False

                st.session_state.timer_started_at = None

                st.rerun()

    with reset:

        if st.button(
            "리셋",
            use_container_width=True
        ):

            reset_timer()

            st.rerun()


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
        unsafe_allow_html=True
    )

    max_time = max(
        st.session_state.subjects.values(),
        default=0
    )

    for subject, seconds in (
        st.session_state.subjects.items()
    ):

        if max_time > 0:

            percentage = (
                seconds / max_time
            ) * 100

        else:

            percentage = 0

        st.markdown(
            f"""
            <div class="subject-row">

                <div class="subject-name">
                    {subject}:
                    <span style="font-weight:400;">
                        {format_time(seconds)}
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
            unsafe_allow_html=True
        )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


# =========================================================
# 타이머 실행 중 화면 갱신
# =========================================================

if st.session_state.timer_running:

    time.sleep(1)

    st.rerun()
