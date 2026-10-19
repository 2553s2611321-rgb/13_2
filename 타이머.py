import streamlit as st
import time
import math

# 1. 기본 페이지 설정
st.set_page_config(
    page_title="학습 도우미 시계",
    page_icon="⏱️",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .stApp {
        background-color: #FFFFFF;
    }
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 1.5rem;
    }
    
    /* 좌/우 컨테이너 스타일링 */
    [data-testid="stColumn"]:first-child [data-testid="stVerticalBlockBorderWrapper"],
    [data-testid="stColumn"]:last-child [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #DDEBF7 !important;
        border: 2px solid #5B9BD5 !important;
        border-radius: 12px !important;
        padding: 10px !important;
    }

    /* 폼 요소 스타일 */
    [data-testid="stForm"] {
        background-color: rgba(255, 255, 255, 0.8) !important;
        border-radius: 8px !important;
        border: 1px solid #B0C4DE !important;
    }

    /* 중앙 영역 스타일 */
    .total-title {
        font-size: 1.8rem;
        font-weight: bold;
        color: #000000;
        text-align: center;
        margin-bottom: 5px;
    }
    .total-time-display {
        font-size: 2.2rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 15px;
    }
    .digital-clock {
        font-size: 2.5rem;
        font-weight: bold;
        color: #111111;
        text-align: center;
        margin-top: 10px;
        margin-bottom: 15px;
        font-family: 'Courier New', Courier, monospace, sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

# 2. 세션 상태 초기화
if "tasks" not in st.session_state:
    st.session_state.tasks = [
        {"subject": "수학", "task": "수학 문제집 풀기", "completed": False},
        {"subject": "영어", "task": "영어 단어 암기", "completed": False}
    ]
if "subject_times" not in st.session_state:
    st.session_state.subject_times = {"수학": 0, "영어": 0, "국어": 0, "기타": 0}
if "total_study_sec" not in st.session_state:
    st.session_state.total_study_sec = 0

if "mode" not in st.session_state:
    st.session_state.mode = "뽀모도로 타이머"
if "pomo_target_min" not in st.session_state:
    st.session_state.pomo_target_min = 25
if "pomo_current_sec" not in st.session_state:
    st.session_state.pomo_current_sec = 25 * 60
if "stopwatch_sec" not in st.session_state:
    st.session_state.stopwatch_sec = 0
if "is_running" not in st.session_state:
    st.session_state.is_running = False
if "selected_subject" not in st.session_state:
    st.session_state.selected_subject = "수학"
if "last_tick_time" not in st.session_state:
    st.session_state.last_tick_time = None

# 시간 포맷 함수 (초 -> HH:MM:SS)
def format_hhmmss(seconds):
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

# 3. 빨간색 아날로그 파이 시계 SVG 생성
def render_analog_clock(current_sec, max_sec, is_countdown=True):
    if max_sec <= 0:
        max_sec = 1
    
    if is_countdown:
        ratio = max(0.0, min(1.0, current_sec / max_sec))
    else:
        ratio = (current_sec % 3600) / 3600.0
        if ratio == 0 and current_sec > 0:
            ratio = 1.0

    cx, cy, r = 100, 100, 85
    
    # 12시 방향부터 시계 방향으로 그리도록 각도 산출
    angle = ratio * 360
    rad = math.radians(angle - 90)
    
    x = cx + r * math.cos(rad)
    y = cy + r * math.sin(rad)
    large_arc_flag = 1 if angle > 180 else 0

    if ratio >= 0.9999:
        # 완전한 원
        path_d = f"M {cx},{cy - r} A {r},{r} 0 1,1 {cx - 0.001},{cy - r} Z"
    elif ratio <= 0.0001:
        path_d = ""
    else:
        path_d = f"M {cx},{cy} L {cx},{cy - r} A {r},{r} 0 {large_arc_flag},1 {x},{y} Z"

    svg_code = f"""
    <div style="display: flex; justify-content: center; align-items: center; margin: 10px 0;">
        <svg width="220" height="220" viewBox="0 0 200 200">
            <!-- 테두리 -->
            <circle cx="{cx}" cy="{cy}" r="{r + 4}" fill="none" stroke="#D32F2F" stroke-width="4"/>
            <!-- 시계 배경 (검은색) -->
            <circle cx="{cx}" cy="{cy}" r="{r}" fill="#000000" />
            <!-- 빨간색 부채꼴 -->
            <path d="{path_d}" fill="#FF0000" />
            <!-- 시계 중앙 지점 -->
            <circle cx="{cx}" cy="{cy}" r="4" fill="#FFFFFF" />
        </svg>
    </div>
    """
    return svg_code

# 4. 실시간 시간 경과 업데이트 로직 (st.rerun 매 루프마다 호출)
if st.session_state.is_running:
    now = time.time()
    if st.session_state.last_tick_time is not None:
        elapsed = int(now - st.session_state.last_tick_time)
        if elapsed >= 1:
            cur_sub = st.session_state.selected_subject
            st.session_state.total_study_sec += elapsed
            st.session_state.subject_times[cur_sub] = st.session_state.subject_times.get(cur_sub, 0) + elapsed

            if st.session_state.mode == "뽀모도로 타이머":
                st.session_state.pomo_current_sec = max(0, st.session_state.pomo_current_sec - elapsed)
                if st.session_state.pomo_current_sec == 0:
                    st.session_state.is_running = False
                    st.balloons()
            else:
                st.session_state.stopwatch_sec += elapsed

            st.session_state.last_tick_time = now
    else:
        st.session_state.last_tick_time = now

# 5. 3컬럼 레이아웃 구성
col_left, col_center, col_right = st.columns([1, 1.2, 1])

# [좌측] 공부 리스트
with col_left:
    with st.container(border=True):
        st.markdown("<h3 style='margin-top:0; color:#000000; font-weight:bold;'>공부 리스트</h3>", unsafe_allow_html=True)
        
        with st.form("task_form", clear_on_submit=True):
            f_subject = st.text_input("과목명", placeholder="예: 국어")
            f_task = st.text_input("할 일", placeholder="예: 비문학 3지문 풀기")
            if st.form_submit_button("추가"):
                if f_task:
                    sub = f_subject.strip() if f_subject.strip() else "기타"
                    st.session_state.tasks.append({"subject": sub, "task": f_task, "completed": False})
                    if sub not in st.session_state.subject_times:
                        st.session_state.subject_times[sub] = 0
                    st.rerun()

        st.markdown("<hr style='border:1px solid #B0C4DE; margin: 15px 0;'>", unsafe_allow_html=True)
        
        sub_list = list(st.session_state.subject_times.keys())
        st.session_state.selected_subject = st.selectbox("현재 학습 과목", sub_list)

        st.write("**할 일 목록**")
        for i, t in enumerate(st.session_state.tasks):
            chk = st.checkbox(f"[{t['subject']}] {t['task']}", value=t["completed"], key=f"t_{i}")
            st.session_state.tasks[i]["completed"] = chk

# [중앙] 총 공부 시간 & 타이머/스톱워치
with col_center:
    st.markdown('<div class="total-title">총 공부 시간</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="total-time-display">{format_hhmmss(st.session_state.total_study_sec)}</div>', unsafe_allow_html=True)

    selected_mode = st.radio(
        "시계 기능 선택",
        ["뽀모도로 타이머", "공부 시간 측정"],
        horizontal=True,
        disabled=st.session_state.is_running
    )
    if selected_mode != st.session_state.mode:
        st.session_state.mode = selected_mode
        st.rerun()

    if st.session_state.mode == "뽀모도로 타이머" and not st.session_state.is_running:
        p_min = st.number_input("뽀모도로 설정(분)", min_value=1, max_value=120, value=st.session_state.pomo_target_min, step=5)
        if p_min != st.session_state.pomo_target_min:
            st.session_state.pomo_target_min = p_min
            st.session_state.pomo_current_sec = p_min * 60

    # 시계 & 디지털 출력
    if st.session_state.mode == "뽀모도로 타이머":
        st.markdown(render_analog_clock(st.session_state.pomo_current_sec, st.session_state.pomo_target_min * 60, True), unsafe_allow_html=True)
        st.markdown(f'<div class="digital-clock">{format_hhmmss(st.session_state.pomo_current_sec)}</div>', unsafe_allow_html=True)
    else:
        st.markdown(render_analog_clock(st.session_state.stopwatch_sec, 3600, False), unsafe_allow_html=True)
        st.markdown(f'<div class="digital-clock">{format_hhmmss(st.session_state.stopwatch_sec)}</div>', unsafe_allow_html=True)

    # 제어 버튼
    b_col1, b_col2, b_col3 = st.columns(3)
    with b_col1:
        if st.button("시작", use_container_width=True):
            st.session_state.is_running = True
            st.session_state.last_tick_time = time.time()
            st.rerun()
    with b_col2:
        if st.button("일시정지", use_container_width=True):
            st.session_state.is_running = False
            st.session_state.last_tick_time = None
            st.rerun()
    with b_col3:
        if st.button("리셋", use_container_width=True):
            st.session_state.is_running = False
            st.session_state.last_tick_time = None
            st.session_state.pomo_current_sec = st.session_state.pomo_target_min * 60
            st.session_state.stopwatch_sec = 0
            st.rerun()

# [우측] 과목별 공부 시간
with col_right:
    with st.container(border=True):
        st.markdown("<h3 style='margin-top:0; color:#000000; font-weight:bold;'>과목별 공부 시간</h3>", unsafe_allow_html=True)
        for sub, sec in st.session_state.subject_times.items():
            st.write(f"**{sub}**: {format_hhmmss(sec)}")
            progress_val = min(1.0, sec / 10800)
            st.progress(progress_val)

# 6. 타이머 루프 제어 (1초 간격 재실행)
if st.session_state.is_running:
    time.sleep(1)
    st.rerun()
