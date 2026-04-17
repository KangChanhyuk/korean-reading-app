import streamlit as st
from streamlit_mic_recorder import mic_recorder
from gtts import gTTS
import io
import difflib
import easyocr
import numpy as np
from PIL import Image

# 1. 페이지 설정
st.set_page_config(page_title="무럭무럭 국어 싹트기", page_icon="🌱", layout="centered")

# OCR 엔진 로드 (한글 전용)
@st.cache_resource
def load_ocr():
    return easyocr.Reader(['ko'])

reader = load_ocr()

# 디자인 테마 (별점 및 결과창 스타일 강화)
st.markdown("""
    <style>
    .stApp { background-color: #F8FBFE; }
    .main-card { background-color: #FFFFFF; padding: 25px; border-radius: 20px; border: 3px solid #AED6F1; text-align: center; }
    .logo-text { font-size: 2.8rem; color: #1B4F72; font-weight: bold; margin-bottom: 10px; }
    .target-text { font-size: 2.5rem !important; color: #1B4F72; font-weight: bold; margin: 15px 0; line-height: 1.4; }
    .correct { color: #28B463; font-weight: normal; }
    .wrong { color: #E74C3C; text-decoration: underline; font-weight: bold; }
    .star-rating { font-size: 3.5rem; color: #F1C40F; margin: 10px 0; text-align: center; }
    .result-box { background: #FDFEFE; padding: 20px; border-radius: 15px; border: 2px solid #D5DBDB; margin-top: 15px; font-size: 1.6rem; text-align: center; }
    .practice-tag { background-color: #EBF5FB; color: #2E86C1; padding: 5px 12px; border-radius: 15px; font-size: 0.9rem; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 2. 데이터 초기화 (기존 데이터 유지 + 사진 추가용 리스트)
if 'data' not in st.session_state:
    st.session_state.data = {
        "1단계 (단어)": ["학교", "선생님", "친구", "운동장", "우리나라"],
        "2단계 (문장)": ["나는 학교가 좋아요.", "하늘에 무지개가 떴어요."],
        "3단계 (문단)": ["오늘은 즐거운 체육 시간입니다. 운동장에서 친구들과 뛰어놀았습니다."],
        "📷 카메라로 찍기": []
    }
if 'idx' not in st.session_state: st.session_state.idx = 0
if 'level' not in st.session_state: st.session_state.level = "1단계 (단어)"
if 'counts' not in st.session_state: st.session_state.counts = {}

# 로고
st.markdown('<p class="logo-text" style="text-align:center;">🌱 국어 싹트기</p>', unsafe_allow_html=True)

# 3. 사이드바 (단계 선택 및 카메라 기능 통합)
st.sidebar.title("📖 학습 메뉴")
level_options = list(st.session_state.data.keys())
new_level = st.sidebar.selectbox("공부할 단계를 골라보세요", level_options, index=level_options.index(st.session_state.level))

if new_level != st.session_state.level:
    st.session_state.level = new_level
    st.session_state.idx = 0
    st.rerun()

# --- 카메라 기능 (해당 단계일 때만 표시) ---
if st.session_state.level == "📷 카메라로 찍기":
    st.subheader("📸 교과서 사진을 찍어주세요")
    uploaded_file = st.file_uploader("사진을 올리면 글자를 자동으로 가져옵니다", type=['jpg', 'jpeg', 'png'])
    
    if uploaded_file:
        img = Image.open(uploaded_file)
        st.image(img, use_container_width=True)
        if st.button("🔍 사진 속 글자 읽기"):
            with st.spinner("AI가 글자를 찾는 중..."):
                img_np = np.array(img)
                result = reader.readtext(img_np)
                extracted = " ".join([res[1] for res in result])
                if extracted.strip():
                    st.session_state.data["📷 카메라로 찍기"].append(extracted.strip())
                    st.session_state.idx = len(st.session_state.data["📷 카메라로 찍기"]) - 1
                    st.success("새로운 공부 거리가 추가되었습니다!")
                    st.rerun()

# --- 메인 학습 화면 ---
current_list = st.session_state.data[st.session_state.level]

if not current_list:
    st.info("아직 추가된 사진이 없어요. 사진을 먼저 올려주세요!")
else:
    # 인덱스 안전장치
    if st.session_state.idx >= len(current_list): st.session_state.idx = 0
    
    target = current_list[st.session_state.idx]
    p_id = f"{st.session_state.level}_{st.session_state.idx}"
    count = st.session_state.counts.get(p_id, 0)

    # 문제 카드
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.markdown(f'<span class="practice-tag">🔥 {count}번째 연습 중</span>', unsafe_allow_html=True)
    st.markdown(f'<p class="target-text">{target}</p>', unsafe_allow_html=True)
    
    # 👦 아이 목소리 톤 (남자아이 느낌을 위해 속도 조절)
    if st.button("👦 AI 친구 목소리 듣기 (먼저 읽어주기)"):
        tts = gTTS(text=target, lang='ko', slow=False) # slow=False가 더 발랄한 느낌을 줍니다
        b = io.BytesIO()
        tts.write_to_fp(b)
        st.audio(b.getvalue())
    st.markdown('</div>', unsafe_allow_html=True)

    # 조작 버튼
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
    
    # 녹음 및 실시간 피드백
    audio = mic_recorder(start_prompt="🎤 녹음 시작", stop_prompt="🛑 녹음 완료", key=f'rec_{p_id}')

    if audio:
        st.session_state.counts[p_id] = count + 1
        st.audio(audio['bytes'])
        
        st.write("🧐 **선생님/부모님 확인용**")
        user_in = st.text_input("아이가 읽은 내용을 입력하면 즉시 분석합니다:", key=f'in_{p_id}')
        
        if user_in:
            # 1. 빨간색 오답 표시 (글자 단위 분석)
            res_html = []
            diff = difflib.ndiff(target, user_in)
            for char in diff:
                if char[0] == ' ': # 정답
                    res_html.append(f'<span class="correct">{char[-1]}</span>')
                else: # 오답 (누락되거나 틀린 글자)
                    res_html.append(f'<span class="wrong">{char[-1]}</span>')
            
            # 2. 별점 계산 (0~5개)
            score = difflib.SequenceMatcher(None, target.replace(" ",""), user_in.replace(" ","")).ratio()
            stars = int(score * 5)
            if score > 0.95: stars = 5

            # 결과 출력
            st.markdown(f'<div class="star-rating">{"★"*stars}{"☆"*(5-stars)}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="result-box">{"".join(res_html)}</div>', unsafe_allow_html=True)
            
            if stars == 5:
                st.balloons()
                st.success("참 잘했어요! 만점입니다! 🌟")
