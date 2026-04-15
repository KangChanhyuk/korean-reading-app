import streamlit as st
from streamlit_mic_recorder import mic_recorder
import difflib

# 1. 페이지 설정 및 모바일 최적화
st.set_page_config(page_title="무럭무럭 국어 싹트기", page_icon="🌱", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #F8FBFE; }
    .main-card { background-color: #FFFFFF; padding: 25px; border-radius: 20px; border: 3px solid #AED6F1; text-align: center; margin-bottom: 20px; }
    .target-text { font-size: 2.5rem !important; color: #1B4F72; font-weight: bold; margin: 15px 0; letter-spacing: 2px; }
    .result-box { background: #F2F4F4; padding: 15px; border-radius: 10px; margin-top: 15px; font-size: 1.5rem; line-height: 1.8; text-align: center; }
    .correct { color: #28B463; }
    .wrong { color: #E74C3C; text-decoration: underline; font-weight: bold; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3rem; font-weight: bold; background-color: #EBF5FB; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 세팅
if 'data' not in st.session_state:
    st.session_state.data = {
        "1단계 (단어)": ["학교", "선생님", "친구", "운동장", "우리나라", "무지개"],
        "2단계 (문장)": ["나는 학교가 좋아요.", "하늘에 무지개가 떴어요.", "친구와 사이좋게 지내요."],
        "3단계 (문단)": ["오늘은 즐거운 체육 시간입니다. 운동장에서 친구들과 뛰어놀았습니다."]
    }
if 'idx' not in st.session_state: st.session_state.idx = 0
if 'level' not in st.session_state: st.session_state.level = "1단계 (단어)"

# 3. 사이드바 메뉴
st.sidebar.title("📖 학습 메뉴")
level_list = list(st.session_state.data.keys())
new_level = st.sidebar.selectbox("단계를 골라보세요", level_list, index=level_list.index(st.session_state.level))

if new_level != st.session_state.level:
    st.session_state.level = new_level
    st.session_state.idx = 0
    st.rerun()

# 4. 메인 화면
st.title("🌱 국어 싹트기")
current_list = st.session_state.data[st.session_state.level]
target_word = current_list[st.session_state.idx]

st.markdown('<div class="main-card">', unsafe_allow_html=True)
st.write(f"**{st.session_state.level}** - {st.session_state.idx + 1}번째 문제")
st.markdown(f'<p class="target-text">{target_word}</p>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# 5. 이전/다음 버튼
c1, c2 = st.columns(2)
with c1:
    if st.button("⬅️ 이전 문제"):
        st.session_state.idx = (st.session_state.idx - 1) % len(current_list)
        st.rerun()
with c2:
    if st.button("다음 문제 ➡️"):
        st.session_state.idx = (st.session_state.idx + 1) % len(current_list)
        st.rerun()

st.write("---")

# 6. 녹음 기능
st.write("▼ 아래 버튼을 누르고 소리 내어 읽어주세요!")
audio = mic_recorder(start_prompt="🎤 녹음 시작", stop_prompt="🛑 녹음 완료", key='recorder')

# 7. 분석 결과 (틀린 부분 빨간색 표시)
if audio:
    st.success("✅ 녹음이 완료되었습니다!")
    # 테스트용 입력창 (나중에 자동 인식으로 업그레이드 가능)
    user_input = st.text_input("아이의 발음을 여기에 입력해보세요 (분석 테스트):")
    
    if user_input:
        result_display = []
        diff = difflib.ndiff(target_word, user_input)
        
        for char in diff:
            if char[0] == ' ': # 맞음
                result_display.append(f'<span class="correct">{char[-1]}</span>')
            elif char[0] == '-': # 빠짐/틀림
                result_display.append(f'<span class="wrong">{char[-1]}</span>')
            elif char[0] == '+': # 더 읽음
                result_display.append(f'<span class="wrong">{char[-1]}</span>')

        st.markdown(f'<div class="result-box">{"".join(result_display)}</div>', unsafe_allow_html=True)
        
        if user_input.replace(" ", "") == target_word.replace(" ", ""):
            st.balloons()
            st.write("### 🎉 정말 잘 읽었어요!")
