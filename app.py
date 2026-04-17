import streamlit as st
from streamlit_mic_recorder import mic_recorder
from gtts import gTTS
import io
import difflib
import easyocr
import numpy as np
from PIL import Image

# 페이지 설정
st.set_page_config(page_title="무럭무럭 국어 싹트기", page_icon="🌱")

# OCR 엔진 초기화 (한글/영어)
@st.cache_resource
def get_reader():
    return easyocr.Reader(['ko', 'en'])

reader = get_reader()

# 스타일 설정
st.markdown("""
    <style>
    .stApp { background-color: #F8FBFE; }
    .main-card { background-color: #FFFFFF; padding: 20px; border-radius: 20px; border: 3px solid #AED6F1; text-align: center; }
    .target-text { font-size: 2.2rem !important; color: #1B4F72; font-weight: bold; }
    .correct { color: #28B463; }
    .wrong { color: #E74C3C; text-decoration: underline; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

if 'custom_text' not in st.session_state: st.session_state.custom_text = ""

st.title("🌱 국어 싹트기: 사진 학습")

# --- 단계 1: 사진 찍고 글자 고르기 ---
with st.expander("📸 1단계: 교과서 사진 찍어서 글자 가져오기", expanded=True):
    uploaded_file = st.file_uploader("교과서 사진을 올려주세요", type=['jpg', 'jpeg', 'png'])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="선택한 사진", use_container_width=True)
        
        if st.button("🔍 사진 속 글자 모두 읽기"):
            with st.spinner("글자를 찾는 중입니다..."):
                img_np = np.array(image)
                results = reader.readtext(img_np)
                # 인식된 글자들을 문장 단위로 합침
                full_text = " ".join([res[1] for res in results])
                st.session_state.all_lines = [res[1] for res in results]
                st.success("글자를 모두 찾아냈습니다!")

        if 'all_lines' in st.session_state:
            st.write("▼ **읽고 싶은 문장을 클릭하세요!**")
            # 아이들이 드래그 대신 문장을 선택할 수 있게 버튼으로 나열
            selected_line = st.selectbox("어느 부분을 공부할까요?", st.session_state.all_lines)
            if st.button("📖 이 문장으로 결정!"):
                st.session_state.custom_text = selected_line
                st.info(f"선택됨: {selected_line}")

# --- 단계 2: 선택한 글자로 연습하기 ---
if st.session_state.custom_text:
    st.write("---")
    target = st.session_state.custom_text
    
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    st.write("아래 글자를 듣고 따라 읽어보세요")
    st.markdown(f'<p class="target-text">{target}</p>', unsafe_allow_html=True)
    
    # AI가 읽어주기 (TTS)
    if st.button("🔊 AI 선생님 목소리 듣기"):
        tts = gTTS(text=target, lang='ko')
        audio_io = io.BytesIO()
        tts.write_to_fp(audio_io)
        st.audio(audio_io.getvalue())
    st.markdown('</div>', unsafe_allow_html=True)

    # 녹음 및 분석
    st.write("### 🎤 내 목소리 녹음하기")
    audio = mic_recorder(start_prompt="녹음 시작", stop_prompt="녹음 완료", key='final_rec')

    if audio:
        st.audio(audio['bytes'])
        user_in = st.text_input("아이가 읽은 내용을 입력해 분석하기 (선생님/학부모)")
        if user_in:
            # 빨간색 오답 표시
            res_html = []
            diff = difflib.ndiff(target, user_in)
            for char in diff:
                if char[0] == ' ': res_html.append(f'<span class="correct">{char[-1]}</span>')
                else: res_html.append(f'<span class="wrong">{char[-1]}</span>')
            
            st.markdown(f'<div style="font-size:1.5rem; text-align:center;">{"".join(res_html)}</div>', unsafe_allow_html=True)
            
            score = difflib.SequenceMatcher(None, target, user_in).ratio()
            st.write(f"### 🎯 정확도: {int(score*100)}%")
            if score > 0.9: st.balloons()
