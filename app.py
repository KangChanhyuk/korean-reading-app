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

# OCR 엔진 로드 (한글 전용, 가볍게 설정)
@st.cache_resource
def load_ocr():
    return easyocr.Reader(['ko'])

reader = load_ocr()

# 디자인 및 스타일 (빨간색 표시와 별점 강조)
st.markdown("""
    <style>
    .stApp { background-color: #F8FBFE; }
    .main-card { background-color: #FFFFFF; padding: 25px; border-radius: 20px; border: 3px solid #AED6F1; text-align: center; }
    .target-text { font-size: 2.3rem !important; color: #1B4F72; font-weight: bold; margin: 15px 0; }
    .correct { color: #28B463; }
    .wrong { color: #E74C3C; text-decoration: underline; font-weight: bold; font-size: 1.2em; }
    .star-rating { font-size: 3.5rem; color: #F1C40F; margin: 10px 0; text-align: center; }
    .result-box { background: #FDFEFE; padding: 20px; border-radius: 15px; border: 2px solid #D5DBDB; margin-top: 15px; font-size: 1.6rem; text-align: center; min-height: 80px; }
    </style>
    """, unsafe_allow_html=True)

# 데이터 초기화
if 'data' not in st.session_state:
    st.session_state.data = {"학습 목록": ["학교", "선생님", "친구와 사이좋게 지내요."]}
if 'idx' not in st.session_state: st.session_state.idx = 0
if 'counts' not in st.session_state: st.session_state.counts = {}

# 상단 로고
st.markdown('<p style="font-size:2.8rem; color:#1B4F72; font-weight:bold; text-align:center;">🌱 국어 싹트기</p>', unsafe_allow_html=True)

# --- [핵심 기능 1] 사진 찍어 글자 읽기 ---
st.write("### 📸 사진 찍어서 문장 만들기")
uploaded_file = st.file_uploader("교과서 사진을 올려주세요", type=['jpg', 'jpeg', 'png'])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, caption="가져온 사진", use_container_width=True)
    
    if st.button("🔍 사진 속 글자 추출하기"):
        with st.spinner("AI가 글자를 읽고 있습니다..."):
            img_np = np.array(img)
            result = reader.readtext(img_np)
            extracted_text = " ".join([res[1] for res in result])
            if extracted_text.strip():
                st.session_state.data["학습 목록"].append(extracted_text.strip())
                st.session_state.idx = len(st.session_state.data["학습 목록"]) - 1
                st.success("새로운 문장이 추가되었습니다!")
                st.rerun()

st.write("---")

# --- [핵심 기능 2] 학습 및 피드백 화면 ---
current_list = st.session_state.data["학습 목록"]
if current_list:
    target = current_list[st.session_state.idx]
    p_id = f"item_{st.session_state.idx}"
    count = st.session_state.counts.get(p_id, 0)

    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.write(f"🔥 {count}번째 도전 중")
    st.markdown(f'<p class="target-text">{target}</p>', unsafe_allow_html=True)
    
    # 👦 아이 목소리 톤 설정 (속도를 약간 빠르게 하고 톤을 높임)
    if st.button("👦 AI 친구 목소리 듣기"):
        tts = gTTS(text=target, lang='ko', slow=False) 
        b = io.BytesIO()
        tts.write_to_fp(b)
        # HTML5를 이용해 피치를 살짝 올리는 효과는 브라우저마다 다르지만, slow=False가 가장 아이 같습니다.
        st.audio(b.getvalue())
    st.markdown('</div>', unsafe_allow_html=True)

    # 이전/다음 버튼
    c1, c2 = st.columns(2)
    with c1:
        if st.button("⬅️ 이전"): st.session_state.idx = (st.session_state.idx - 1) % len(current_list); st.rerun()
    with c2:
        if st.button("다음 ➡️"): st.session_state.idx = (st.session_state.idx + 1) % len(current_list); st.rerun()

    st.write("---")
    
    # 녹음 영역
    audio = mic_recorder(start_prompt="🎤 녹음 시작", stop_prompt="🛑 녹음 완료", key=f'rec_{p_id}')

    if audio:
        st.session_state.counts[p_id] = count + 1
        st.audio(audio['bytes'])
        
        # [핵심 기능 3] 즉각적인 분석 및 오답 표시
        st.write("🧐 **선생님 확인용 입력** (아이의 발음을 적어주세요)")
        user_in = st.text_input("여기에 입력하면 바로 별점과 오답이 나옵니다:", key=f'input_{p_id}')
        
        if user_in:
            # 1. 빨간색 표시 로직 (더 정확하게 수정)
            res_html = []
            # 글자 단위로 비교하여 틀린 부분 강조
            diff = difflib.ndiff(target, user_in)
            for char in diff:
                if char[0] == ' ': # 정답
                    res_html.append(f'<span class="correct">{char[-1]}</span>')
                elif char[0] == '-': # 원본에 있는데 틀림/누락 (빨간색)
                    res_html.append(f'<span class="wrong">{char[-1]}</span>')
                elif char[0] == '+': # 원본에 없는데 추가됨 (빨간색)
                    res_html.append(f'<span class="wrong">{char[-1]}</span>')

            # 2. 즉각 별점 계산
            score = difflib.SequenceMatcher(None, target.replace(" ",""), user_in.replace(" ","")).ratio()
            stars = int(score * 5)
            if score > 0.98: stars = 5 # 거의 완벽할 때

            # 3. 화면 출력
            st.markdown(f'<div class="star-rating">{"★"*stars}{"☆"*(5-stars)}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="result-box">{"".join(res_html)}</div>', unsafe_allow_html=True)
            
            if stars == 5:
                st.balloons()
                st.success("우와! 완벽해요! 🌟")
