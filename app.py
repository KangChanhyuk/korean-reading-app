import streamlit as st
from streamlit_mic_recorder import mic_recorder
from gtts import gTTS
import io
import difflib

# 1. 페이지 설정
st.set_page_config(page_title="무럭무럭 국어 싹트기", page_icon="🌱", layout="centered")

# 디자인 테마
st.markdown("""
    <style>
    .stApp { background-color: #F8FBFE; }
    .main-card { background-color: #FFFFFF; padding: 25px; border-radius: 20px; border: 3px solid #AED6F1; text-align: center; }
    .logo-text { font-size: 2.8rem; color: #1B4F72; font-weight: bold; margin-bottom: 0px; }
    .target-text { font-size: 2.5rem !important; color: #1B4F72; font-weight: bold; margin: 15px 0; line-height: 1.4; }
    .practice-tag { background-color: #EBF5FB; color: #2E86C1; padding: 5px 12px; border-radius: 15px; font-size: 0.9rem; font-weight: bold; }
    .result-box { background: #FFFFFF; padding: 15px; border-radius: 15px; border: 1px solid #D5DBDB; margin-top: 15px; font-size: 1.3rem; text-align: center; }
    .correct { color: #28B463; }
    .wrong { color: #E74C3C; text-decoration: underline; font-weight: bold; }
    .star-rating { font-size: 2.5rem; color: #F1C40F; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

# 데이터 초기화
if 'data' not in st.session_state:
    st.session_state.data = {
        "1단계 (단어)": ["학교", "선생님", "친구", "운동장", "우리나라"],
        "2단계 (문장)": ["나는 학교가 좋아요.", "하늘에 무지개가 떴어요."],
        "3단계 (문단)": ["오늘은 즐거운 체육 시간입니다. 운동장에서 친구들과 뛰어놀았습니다."],
        "📷 사진으로 만들기": []
    }
if 'idx' not in st.session_state: st.session_state.idx = 0
if 'level' not in st.session_state: st.session_state.level = "1단계 (단어)"
if 'counts' not in st.session_state: st.session_state.counts = {}

# --- 로고 및 상단 ---
st.markdown('<p class="logo-text" style="text-align:center;">🌱 국어 싹트기</p>', unsafe_allow_html=True)

# 사이드바
st.sidebar.title("📖 학습 메뉴")
new_level = st.sidebar.selectbox("단계를 골라보세요", list(st.session_state.data.keys()), index=list(st.session_state.data.keys()).index(st.session_state.level))

if new_level != st.session_state.level:
    st.session_state.level = new_level
    st.session_state.idx = 0
    st.rerun()

# --- 기능 1: 사진 찍어 글자 만들기 (경량화 버전) ---
if st.session_state.level == "📷 사진으로 만들기":
    st.subheader("📸 교과서 사진 찍기")
    st.info("💡 서버 사양을 위해, 사진 속 글자를 직접 입력하거나 복사해서 넣어주세요!")
    pasted_text = st.text_area("사진 속 글자를 여기에 입력하고 [저장]을 누르세요:", height=150)
    if st.button("🚀 연습 목록에 저장"):
        if pasted_text.strip():
            st.session_state.data["📷 사진으로 만들기"].append(pasted_text.strip())
            st.session_state.idx = len(st.session_state.data["📷 사진으로 만들기"]) - 1
            st.success("저장되었습니다! 이제 위 단계에서 공부할 수 있어요.")
            st.rerun()

# --- 기능 2: 학습 화면 ---
current_list = st.session_state.data[st.session_state.level]

if not current_list:
    st.warning("아직 등록된 문장이 없어요. 사진 단계에서 글을 추가해 보세요!")
else:
    target = current_list[st.session_state.idx]
    p_id = f"{st.session_state.level}_{st.session_state.idx}"
    count = st.session_state.counts.get(p_id, 0)

    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.markdown(f'<span class="practice-tag">🔥 {count}번째 연습</span>', unsafe_allow_html=True)
    st.markdown(f'<p class="target-text">{target}</p>', unsafe_allow_html=True)
    
    if st.button("🔊 먼저 들어보기 (쉐도우 리딩)"):
        tts = gTTS(text=target, lang='ko')
        b = io.BytesIO()
        tts.write_to_fp(b)
        st.audio(b.getvalue())
    st.markdown('</div>', unsafe_allow_html=True)

    # 버튼 레이아웃
    c1, c2 = st.columns(2)
    with c1:
        if st.button("⬅️ 이전"):
            st.session_state.idx = (st.session_state.idx - 1) % len(current_list)
            st.rerun()
    with c2:
        if st.button("다음 ➡️"):
            st.session_state.idx = (st.session_state.idx + 1) % len(current_list)
            st.rerun()

    st.write("---")
    audio = mic_recorder(start_prompt="🎤 녹음 시작", stop_prompt="🛑 녹음 완료", key=f'rec_{p_id}')

    if audio:
        st.session_state.counts[p_id] = count + 1
        st.audio(audio['bytes'])
        
        user_in = st.text_input("아이가 읽은 내용을 적어주세요 (피드백 확인용):")
        if user_in:
            # 빨간색 표시 로직
            res_html = []
            diff = difflib.ndiff(target, user_in)
            for char in diff:
                if char[0] == ' ': res_html.append(f'<span class="correct">{char[-1]}</span>')
                else: res_html.append(f'<span class="wrong">{char[-1]}</span>')
            
            # 별점 계산
            score = difflib.SequenceMatcher(None, target, user_in).ratio()
            stars = int(score * 5)
            st.markdown(f'<div class="star-rating">{"★"*stars}{"☆"*(5-stars)}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="result-box">{"".join(res_html)}</div>', unsafe_allow_html=True)
            if stars == 5: st.balloons()
