import streamlit as st
import time
import datetime

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="뽀모도로 학습 도우미",
    page_icon="⏱️",
    layout="centered"
)

# Custom CSS로 UI 개선
st.markdown("""
    <style>
    .main-title {
        text-align: center;
        color: #FF4B4B;
        font-size: 2.3rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    .sub-title {
        text-align: center;
        color: #555;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# 2. 세션 상태(Session State) 초기화
if "work_min" not in st.session_state:
    st.session_state.work_min = 25
if "rest_min" not in st.session_state:
    st.session_state.rest_min = 5
if "current_time_sec" not in st.session_state:
    st.session_state.current_time_sec = 25 * 60
if "total_time_sec" not in st.session_state:
    st.session_state.total_time_sec = 25 * 60
if "is_running" not in st.session_state:
    st.session_state.is_running = False
if "mode" not in st.session_state:
    st.session_state.mode = "집중 모드"  # "집중 모드" 또는 "휴식 모드"
if "logs" not in st.session_state:
    st.session_state.logs = []
if "pomo_count" not in st.session_state:
    st.session_state.pomo_count = 0

# 3. SVG 아날로그 뽀모도로 시계 생성 함수
def render_pomodoro_clock(current_sec, total_sec, mode):
    progress = 1.0 - (current_sec / total_sec if total_sec > 0 else 0)
    minutes = current_sec // 60
    seconds = current_sec % 60
    time_str = f"{minutes:02d}:{seconds:02d}"

    # 모드별 테마 색상 설정
    if mode == "집중 모드":
        theme_color = "#FF4B4B" # Red
        bg_color = "#FFE6E6"
    else:
        theme_color = "#28A745" # Green
        bg_color = "#E6F4EA"

    # SVG 원형 시계 게이지 계산 (원 둘레: 2 * pi * 90 ≈ 565.48)
    stroke_dashoffset = 565.48 * progress

    svg_html = f"""
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; margin: 20px 0;">
        <svg width="240" height="240" viewBox="0 0 200 200">
            <!-- 배경 원 -->
            <circle cx="100" cy="100" r="90" fill="none" stroke="{bg_color}" stroke-width="12"/>
            <!-- 잔여 시간 원형 게이지 -->
            <circle cx="100" cy="100" r="90" fill="none" stroke="{theme_color}" stroke-width="12"
                    stroke-dasharray="565.48" stroke-dashoffset="{stroke_dashoffset}"
                    stroke-linecap="round" transform="rotate(-90 100 100)" style="transition: stroke-dashoffset 0.5s ease;"/>
            <!-- 뽀모도로 시계 꼭지 부분 (디자인) -->
            <rect x="92" y="2" width="16" height="8" rx="3" fill="{theme_color}" />
            <!-- 디지털 잔여 시간 텍스트 -->
            <text x="100" y="95" text-anchor="middle" font-size="30" font-weight="bold" fill="#333" font-family="sans-serif">{time_str}</text>
            <!-- 현재 모드 표시 -->
            <text x="100" y="125" text-anchor="middle" font-size="14" font-weight="600" fill="{theme_color}" font-family="sans-serif">{mode}</text>
        </svg>
    </div>
    """
    return svg_html

# 4. 헤더 영역
st.markdown('<div class="main-title">⏱️ 뽀모도로 학습 도우미</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">시각적인 아날로그 시계와 함께 집중력을 극대화해보세요!</div>', unsafe_allow_html=True)

# 5. 사이드바 - 타이머 설정
st.sidebar.header("⚙️ 타이머 설정")

preset = st.sidebar.radio("자주 사용하는 타이머", ["25분 집중 / 5분 휴식", "50분 집중 / 10분 휴식", "사용자 지정"])

if preset == "25분 집중 / 5분 휴식":
    work_input = 25
    rest_input = 5
elif preset == "50분 집중 / 10분 휴식":
    work_input = 50
    rest_input = 10
else:
    work_input = st.sidebar.number_input("집중 시간(분)", min_value=1, max_value=120, value=25)
    rest_input = st.sidebar.number_input("휴식 시간(분)", min_value=1, max_value=60, value=5)

# 설정 변경 시 타이머 리셋 처리
if st.sidebar.button("설정 적용 및 타이머 초기화"):
    st.session_state.work_min = work_input
    st.session_state.rest_min = rest_input
    st.session_state.mode = "집중 모드"
    st.session_state.current_time_sec = work_input * 60
    st.session_state.total_time_sec = work_input * 60
    st.session_state.is_running = False
    st.rerun()

# 6. 메인 콘텐츠 화면
col1, col2 = st.columns([1, 1])

with col1:
    task_name = st.text_input("📝 오늘의 학습 목표 / 과제", placeholder="예: 수학 문제집 5페이지 풀기")

    # 아날로그 시계 렌더링을 위한 빈 컨테이너
    clock_placeholder = st.empty()
    clock_placeholder.markdown(
        render_pomodoro_clock(st.session_state.current_time_sec, st.session_state.total_time_sec, st.session_state.mode),
        unsafe_allow_html=True
    )

    # 제어 버튼
    btn_col1, btn_col2, btn_col3 = st.columns(3)

    with btn_col1:
        if st.button("▶ 시작"):
            st.session_state.is_running = True

    with btn_col2:
        if st.button("⏸ 일시정지"):
            st.session_state.is_running = False

    with btn_col3:
        if st.button("🔄 리셋"):
            st.session_state.is_running = False
            if st.session_state.mode == "집중 모드":
                st.session_state.current_time_sec = st.session_state.work_min * 60
                st.session_state.total_time_sec = st.session_state.work_min * 60
            else:
                st.session_state.current_time_sec = st.session_state.rest_min * 60
                st.session_state.total_time_sec = st.session_state.rest_min * 60
            st.rerun()

with col2:
    st.subheader("📊 오늘의 학습 현황")

    # 성과 메트릭
    m_col1, m_col2 = st.columns(2)
    m_col1.metric("완료한 뽀모도로", f"{st.session_state.pomo_count}개")
    m_col2.metric("총 집중 시간", f"{st.session_state.pomo_count * st.session_state.work_min}분")

    st.markdown("---")
    st.write("📋 **학습 기록 (Timelog)**")

    if st.session_state.logs:
        for log in reversed(st.session_state.logs):
            st.caption(f"• **[{log['time']}]** {log['task']} ({log['mode']})")
    else:
        st.info("타이머를 완료하면 기록이 자동으로 쌓입니다.")

# 7. 타이머 루프 실행 로직 (안정적인 실시간 갱신)
if st.session_state.is_running:
    while st.session_state.current_time_sec > 0 and st.session_state.is_running:
        time.sleep(1)
        st.session_state.current_time_sec -= 1

        # 시계 UI 업데이트
        clock_placeholder.markdown(
            render_pomodoro_clock(st.session_state.current_time_sec, st.session_state.total_time_sec, st.session_state.mode),
            unsafe_allow_html=True
        )

    # 시간 종료 시 자동 전환
    if st.session_state.current_time_sec == 0 and st.session_state.is_running:
        now_str = datetime.datetime.now().strftime("%H:%M:%S")
        current_task = task_name if task_name else "목표 미입력"

        if st.session_state.mode == "집중 모드":
            st.balloons()
            st.session_state.pomo_count += 1
            st.session_state.logs.append({"time": now_str, "task": current_task, "mode": "집중 완료"})
            st.success("🎉 집중 시간이 끝났습니다! 휴식을 취하세요.")

            # 휴식 모드로 전환
            st.session_state.mode = "휴식 모드"
            st.session_state.current_time_sec = st.session_state.rest_min * 60
            st.session_state.total_time_sec = st.session_state.rest_min * 60
            st.session_state.is_running = False
        else:
            st.snow()
            st.session_state.logs.append({"time": now_str, "task": current_task, "mode": "휴식 완료"})
            st.info("🔔 휴식 시간이 끝났습니다! 다시 집중해볼까요?")

            # 집중 모드로 전환
            st.session_state.mode = "집중 모드"
            st.session_state.current_time_sec = st.session_state.work_min * 60
            st.session_state.total_time_sec = st.session_state.work_min * 60
            st.session_state.is_running = False

        st.rerun()
