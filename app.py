import streamlit as st
from streamlit_mic_recorder import mic_recorder
from gtts import gTTS
import io
import difflib
import easyocr
import numpy as np
from PIL import Image

# 1. 페이지 설정 및 OCR 엔진 로드
st.set_page_config(page_title="무럭무럭 국어 싹트기", page_icon="🌱", layout="centered")

@st.cache_resource
def load_ocr():
    # 한글 인식 엔진 (최초 실행 시 로딩 시간이 걸릴 수 있습니다)
    return easyocr.Reader(['ko'])

reader = load_ocr()

# 디자인 테마 (별점 및 결과창 스타일 강화)
st.markdown("""
    <style>
    .stApp { background-color: #F8FBFE; }
    .main-card { background-color: #FFFFFF; padding: 25px; border-radius: 20px; border: 3px solid #AED6F1; text-align: center; }
    .logo-text { font-size: 2.8rem; color: #1B4F72; font-weight: bold; margin-bottom: 0px; }
    .target-text { font-size: 2.2rem !important; color: #1B4F72; font-weight: bold; margin: 15px 0; line-height: 1.4; }
    .correct { color: #28B463; font-weight: normal; }
    .wrong { color: #E74C3C; text-decoration: underline; font-weight: bold; }
    .star-rating { font-size: 3rem; color: #F1C40F; margin: 10px 0; text-shadow: 1px 1px 2px #BBB; }
    .result-box { background: #FDFEFE; padding: 15px; border-radius: 15px; border: 1px solid #D5DBDB; margin-top: 15px; font-size: 1.4rem; text-align: center; }
    .practice-tag { background-color: #EBF5FB; color: #2E86C1; padding: 5px 12px; border-radius: 15px; font-size: 0.9rem; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# 데이터 초기화
if 'data' not in st.session_state:
    st.session_state.data = {
        "1단계 (단어)": ["학교", "선생님", "친구"],
        "2단계 (문장)": ["나는 학교가 좋아요."],
        "3단계 (문단)": ["오늘은 즐거운 체육 시간입니다."],
        "📸 사진으로 공부하기": []
    }
if 'idx' not in st.session_state: st.session_state.idx = 0
if 'level' not in st.session_state: st.session_state.level = "1단계 (단어)"
if 'counts' not in st.session_state: st.session_state.counts = {}
if 'ocr_results' not in st.session_state: st.session_state.ocr_results = []

# --- 로고 ---
st.markdown('<p class="logo-text" style="text-align:center;">🌱 국어 싹트기</p>', unsafe_allow_html=True)

# 사이드바
st.sidebar.title("📖 학습 메뉴")
level_list = list(st.session_state.data.keys())
new_level = st.sidebar.selectbox("단계를 골라보세요", level_list, index=level_list.index(st.session_state.level))

if new_level != st.session_state.level:
    st.session
