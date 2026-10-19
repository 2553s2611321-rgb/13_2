import streamlit as st
import time
import math

# 1. 기본 페이지 설정
st.set_page_config(
    page_title="학습 도우미 시계",
    page_icon="⏱️",
    layout="wide"
)

# Custom CSS - 세 컬럼의 높이를 동일하게 맞추고 상단/하단 테두리를 정돈하는 스타일
st.markdown("""
    <style>
    .stApp {
        background-color: #FFFFFF;
    }
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 1.5rem;
    }
    
    /* 3개 컬럼의 높이를 동등하게 정렬 */
    [data-testid="stColumn"] {
        display: flex;
        flex-direction: column;
    }

    /* 좌/우측 하늘색 상자 - 높이 100% 고정 및 동일 최소 높이 부여 */
    .sky-box {
        background-color: #DDEBF7;
        border: 2px solid #5B9BD5 !important;
        border-radius: 10px;
        padding: 20px;
        height: 100%;
        min-height: 620px;
        box-sizing: border-box;
        display: flex;
        flex-direction: column;
    }

    .sky-box h3 {
        margin-top: 0 !important;
        padding-top: 0 !important;
        color: #000000;
        font-weight: bold;
    }

    /* 폼 영역 하얀 배경 */
    [data-testid="stForm"] {
        background-color: rgba(255, 255, 255, 0.8) !important;
        border-radius: 8px !important;
        border: 1px solid #B0C4DE !important;
    }

    /* 중앙 시계 패널 - 동일한 높이 균형 맞춤 */
    .center-panel {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-start;
        text-align: center;
        height: 100%;
        min-height: 620px;
        padding: 10px 0;
        box-sizing: border-box;
    }
    
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
        text-align: center !important;
        margin-top: 10px;
        margin-bottom: 15px;
        font-family: 'Courier New', Courier, monospace, sans-serif;
        width: 100%;
        display: block;
    }
    
    .stButton>button {
        width: 100%;
        border-radius: 6px;
        font-weight: bold;
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

def format_hhmmss(seconds):
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

# 3. 파이 시계 SVG 생성
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
    angle = ratio * 360
    rad = math.radians(angle - 90)
    
    x = cx + r * math.cos(rad)
    y = cy + r * math.sin(rad)
    large_arc_flag = 1 if angle > 180 else 0

    if ratio >= 0.9999:
        path_d = f"M {cx},{cy - r} A {r},{r} 0 1,1 {cx - 0.001},{cy - r} Z"
    elif ratio <= 0.0001:
        path_d = ""
    else:
        path_d = f"M {cx},{cy} L {cx},{cy - r} A {r},{r} 0 {large_arc_flag},1 {x},{y} Z"

    svg_code = f"""
    <div style="display: flex; justify-content: center; align-items: center; margin: 10px 0; width: 100%;">
        <svg width="220" height="220" viewBox="0 0 200 200">
            <circle cx="{cx}" cy="{cy}" r="{r + 4}" fill="none" stroke="#D32F2F" stroke-width="4"/>
            <circle cx="{cx}" cy="{cy}" r="{r}" fill="#000000" />
            <path d="{path_d}" fill="#FF0000" />
            <circle cx="{cx}" cy="{cy}" r="3" fill="#FFFFFF" />
        </svg>
    </div>
    """
    return svg_code

# 4. 3컬럼 레이아웃
col_left, col_center, col_right = st.columns([1, 1.2, 1])

# ==========================================
# [좌측] 공부 리스트 (동일 높이 카드)
# ==========================================
with col_left:
    st.markdown('<div class="sky-box">', unsafe_allow_html=True)
    st.markdown("<h3>공부 리스트</h3>", unsafe_allow_html=True)
    
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

    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# [중앙] 총 공부 시간 & 시계 (동일 높이 패널)
# ==========================================
with col_center:
    st.markdown('<div class="center-panel">', unsafe_allow_html=True)
    
    st.markdown('<div class="total-title">총 공부 시간</div>', unsafe_allow_html=True)
    total_time_place = st.empty()
    total_time_place.markdown(f'<div class="total-time-display">{format_hhmmss(st.session_state.total_study_sec)}</div>', unsafe_allow_html=True)

    selected_mode = st.radio(
        "시계 기능 선택",
        ["뽀모도로 타이머", "공부 시간 측정"],
        horizontal=True,
        disabled=st.session_state.is_running
    )
    st.session_state.mode = selected_mode

    if st.session_state.mode == "뽀모도로 타이머":
        if not st.session_state.is_running:
            p_min = st.number_input("뽀모도로 설정(분)", min_value=1, max_value=120, value=st.session_state.pomo_target_min, step=5)
            if p_min != st.session_state.pomo_target_min:
                st.session_state.pomo_target_min = p_min
                st.session_state.pomo_current_sec = p_min * 60

    clock_place = st.empty()
    digital_place = st.empty()

    b_col1, b_col2, b_col3 = st.columns(3)
    with b_col1:
        if st.button("시작"):
            st.session_state.is_running = True
    with b_col2:
        if st.button("일시정지"):
            st.session_state.is_running = False
    with b_col3:
        if st.button("리셋"):
            st.session_state.is_running = False
            st.session_state.pomo_current_sec = st.session_state.pomo_target_min * 60
            st.session_state.stopwatch_sec = 0
            st.rerun()

    if st.session_state.mode == "뽀모도로 타이머":
        clock_place.markdown(render_analog_clock(st.session_state.pomo_current_sec, st.session_state.pomo_target_min * 60, True), unsafe_allow_html=True)
        digital_place.markdown(f'<div class="digital-clock">{format_hhmmss(st.session_state.pomo_current_sec)}</div>', unsafe_allow_html=True)
    else:
        clock_place.markdown(render_analog_clock(st.session_state.stopwatch_sec, 3600, False), unsafe_allow_html=True)
        digital_place.markdown(f'<div class="digital-clock">{format_hhmmss(st.session_state.stopwatch_sec)}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# [우측] 과목별 공부 시간 (동일 높이 카드)
# ==========================================
with col_right:
    st.markdown('<div class="sky-box">', unsafe_allow_html=True)
    st.markdown("<h3>과목별 공부 시간</h3>", unsafe_allow_html=True)
    
    subject_place = st.empty()
    
    def update_subject_display():
        with subject_place.container():
            for sub, sec in st.session_state.subject_times.items():
                st.write(f"**{sub}**: {format_hhmmss(sec)}")
                progress_val = min(1.0, sec / 10800)
                st.progress(progress_val)

    update_subject_display()
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# 실시간 타이머 동작 루프
# ==========================================
if st.session_state.is_running:
    while st.session_state.is_running:
        time.sleep(1)
        cur_sub = st.session_state.selected_subject
        
        st.session_state.total_study_sec += 1
        st.session_state.subject_times[cur_sub] = st.session_state.subject_times.get(cur_sub, 0) + 1

        if st.session_state.mode == "뽀모도로 타이머":
            if st.session_state.pomo_current_sec > 0:
                st.session_state.pomo_current_sec -= 1
            else:
                st.session_state.is_running = False
                st.balloons()
                st.success("뽀모도로 시간이 완료되었습니다!")
                
            clock_place.markdown(render_analog_clock(st.session_state.pomo_current_sec, st.session_state.pomo_target_min * 60, True), unsafe_allow_html=True)
            digital_place.markdown(f'<div class="digital-clock">{format_hhmmss(st.session_state.pomo_current_sec)}</div>', unsafe_allow_html=True)
            
        else:
            st.session_state.stopwatch_sec += 1
            clock_place.markdown(render_analog_clock(st.session_state.stopwatch_sec, 3600, False), unsafe_allow_html=True)
            digital_place.markdown(f'<div class="digital-clock">{format_hhmmss(st.session_state.stopwatch_sec)}</div>', unsafe_allow_html=True)

        total_time_place.markdown(f'<div class="total-time-display">{format_hhmmss(st.session_state.total_study_sec)}</div>', unsafe_allow_html=True)
        update_subject_display()

        if not st.session_state.is_running:
            st.rerun()
