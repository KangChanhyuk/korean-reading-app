import streamlit as st
from streamlit_mic_recorder import mic_recorder
import difflib
import random

# 1. 페이지 설정
st.set_page_config(page_title="무럭무럭 국어 싹트기", page_icon="🌱", layout="centered")

# 2. 아이들 눈높이에 맞춘 예쁜 디자인
st.markdown("""
    <style>
    .stApp { background-color: #FDFEFE; }
    .main-card { background-color: #FFFFFF; padding: 30px; border-radius: 30px; border: 5px solid #AED6F1; box-shadow: 10px 10px 20px rgba(0,0,0,0.05); text-align: center; }
    h1 { color: #2E86C1; font-family: 'Nanum Gothic', sans-serif; }
    .target-text { font-size: 3rem !important; color: #1B4F72; font-weight: bold; margin: 20px 0; background: #EBF5FB; border-radius: 15px; padding: 10px; }
    .correct { color: #28B463; font-weight: bold; font-size: 1.5rem; }
    .wrong { color: #E74C3C; font-weight: bold; font-size: 1.5rem; text-decoration: underline; }
    </style>
    """, unsafe_allow_html=True)

# 3. 읽기 연습 데이터
levels = {
    "1단계 (단어)": ["학교", "선생님", "친구", "운동장", "우리나라", "무지개"],
    "2단계 (문장)": ["나는 학교가 좋아요.", "하늘에 무지개가 떴어요.", "친구와 사이좋게 지내요.", "또박또박 읽어봐요."],
    "3단계 (문단)": ["오늘은 즐거운 체육 시간입니다. 운동장에서 친구들과 함께 신나게 뛰어놀았습니다. 땀이 났지만 정말 행복했습니다."]
}

# 4. 앱 상태 초기화
if 'level' not in st.session_state: st.session_state.level = "1단계 (단어)"
if 'target' not in st.session_state: st.session_state.target = random.choice(levels[st.session_state.level])

# 5. 메인 화면 구성
st.title("🌱 무럭무럭 국어 싹트기")
st.write("### 오늘의 읽기 모험을 시작해볼까?")

st.markdown('<div class="main-card">', unsafe_allow_html=True)
st.info(f"현재 **{st.session_state.level}** 공부 중이야!")
st.write("아래 글자를 소리 내어 읽어보세요:")
st.markdown(f'<p class="target-text">{st.session_state.target}</p>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.write("")

# 6. 녹음 버튼
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.write("▼ 보라색 버튼을 누르고 읽어줘!")
    audio = mic_recorder(start_prompt="🎤 녹음 시작하기", stop_prompt="✅ 다 읽었어!", key='recorder')

# 7. 결과 분석
if audio:
    st.divider()
    # 실제 앱 구동 확인용 입력창 (나중에 자동 인식으로 교체 가능)
    recognized_text = st.text_input("AI가 들은 말 (테스트를 위해 직접 입력해보세요):", value=st.session_state.target)
    
    target = st.session_state.target
    result_html = []
    for s in difflib.ndiff(target, recognized_text):
        if s[0] == ' ': result_html.append(f'<span class="correct">{s[-1]}</span>')
        elif s[0] == '-': result_html.append(f'<span class="wrong">{s[-1]}</span>')

    st.write("### 🧐 선생님의 분석 결과")
    st.markdown(f"<div>{''.join(result_html)}</div>", unsafe_allow_html=True)
    
    if target == recognized_text:
        st.balloons()
        st.success("우와! 완벽하게 읽었어! 정말 최고야! 👍")

# 8. 메뉴 설정
st.sidebar.title("📖 학습 메뉴")
new_level = st.sidebar.selectbox("단계를 골라보세요", list(levels.keys()))
if new_level != st.session_state.level:
    st.session_state.level = new_level
    st.session_state.target = random.choice(levels[new_level])
    st.rerun()

if st.sidebar.button("다른 문제로 바꿀래"):
    st.session_state.target = random.choice(levels[st.session_state.level])
    st.rerun()