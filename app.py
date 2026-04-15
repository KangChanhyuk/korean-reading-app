import streamlit as st
from streamlit_mic_recorder import mic_recorder
from gtts import gTTS
from paddleocr import PaddleOCR
from PIL import Image
import io
import difflib
import numpy as np

# 1. 페이지 설정 및 초기화
st.set_page_config(page_title="무럭무럭 국어 싹트기", page_icon="🌱", layout="centered")

# OCR 및 Session State 초기화
@st.cache_resource
def load_ocr():
    return PaddleOCR(use_angle_cls=True, lang='korean', show_log=False)

try:
    ocr = load_ocr()
except:
    st.error("OCR 엔진을 로드하는 중 오류가 발생했습니다. requirements.txt를 확인해주세요.")

if 'data' not in st.session_state:
    st.session_state.data = {
        "1단계 (단어)": ["학교", "선생님", "친구", "운동장", "우리나라"],
        "2단계 (문장)": ["나는 학교가 좋아요.", "하늘에 무지개가 떴어요."],
        "3단계 (문단)": ["오늘은 즐거운 체육 시간입니다. 운동장에서 친구들과 뛰어놀았습니다."],
        "📷 직접 만들기": []
    }
if 'idx' not in st.session_state: st.session_state.idx = 0
if 'level' not in st.session_state: st.session_state.level = "1단계 (단어)"
if 'practice_counts' not in st.session_state: st.session_state.practice_counts = {} # 문제별 연습 횟수

# 스타일 정의
st.markdown("""
    <style>
    .stApp { background-color: #F8FBFE; }
    .main-card { background-color: #FFFFFF; padding: 20px; border-radius: 20px; border: 3px solid #AED6F1; text-align: center; margin-bottom: 10px; }
    .logo-text { font-size: 3rem !important; color: #1B4F72; font-weight: bold; margin-bottom: 5px; }
    .target-text { font-size: 2.8rem !important; color: #1B4F72; font-weight: bold; margin: 10px 0; letter-spacing: 1px; line-height: 1.3;}
    .practice-tag { background-color: #EBF5FB; color: #2E86C1; padding: 5px 10px; border-radius: 15px; font-size: 0.9rem; font-weight: bold;}
    .result-box { background: #FFFFFF; padding: 15px; border-radius: 15px; border: 1px solid #D5DBDB; margin-top: 15px; font-size: 1.3rem; line-height: 1.6; text-align: center; }
    .correct { color: #28B463; }
    .wrong { color: #E74C3C; text-decoration: underline; font-weight: bold; }
    .star-rating { font-size: 2.5rem; color: #F1C40F; margin: 10px 0; }
    div[data-testid="stMetricValue"] { font-size: 1.5rem !important; color: #2E86C1; }
    </style>
    """, unsafe_allow_html=True)

# TTS (먼저 듣기) 함수
def play_tts(text):
    try:
        tts = gTTS(text=text, lang='ko', slow=False)
        audio_data = io.BytesIO()
        tts.write_to_fp(audio_data)
        st.audio(audio_data.getvalue(), format='audio/mp3')
    except:
        st.warning("🎤 목소리 준비 중입니다. 잠시 후 다시 시도해주세요.")

# 데이터 기반 별점 및 분석 함수
def analyze_reading(target, user_input):
    if not user_input: return 0, ""
    
    target_clean = target.replace(" ", "").replace(".", "").replace(",", "")
    user_clean = user_input.replace(" ", "").replace(".", "").replace(",", "")
    
    # 1. 빨갛게 표시할 결과 HTML 생성
    result_html = []
    correct_chars = 0
    diff = difflib.ndiff(target, user_input)
    
    for char in diff:
        if char[0] == ' ':
            result_html.append(f'<span class="correct">{char[-1]}</span>')
            if char[-1].strip(): correct_count =+ 1 # 공백 제외한 맞은 글자 수
        elif char[0] == '-': # 원문에 있는데 빠짐
            result_html.append(f'<span class="wrong">{char[-1]}</span>')
        elif char[0] == '+': # 원문에 없는데 더 읽음
            result_html.append(f'<span class="wrong">{char[-1]}</span>')
    
    # 2. 정확도 기반 별점 계산 (0~5개)
    sm = difflib.SequenceMatcher(None, target_clean, user_clean)
    ratio = sm.ratio()
    
    if ratio >= 0.95: stars = 5
    elif ratio >= 0.85: stars = 4
    elif ratio >= 0.70: stars = 3
    elif ratio >= 0.50: stars = 2
    elif ratio >= 0.30: stars = 1
    else: stars = 0
    
    return stars, "".join(result_html)

# --- 메인 화면 구성 ---

# 로고 및 빈칸 삭제 반영
st.markdown('<div style="text-align:center;">', unsafe_allow_html=True)
st.markdown(f'<p class="logo-text">🌱 국어 싹트기</p>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# 사이드바 메뉴 (직접 만들기 추가)
st.sidebar.title("📖 학습 메뉴")
level_list = list(st.session_state.data.keys())
new_level = st.sidebar.selectbox("단계를 골라보세요", level_list, index=level_list.index(st.session_state.level))

# 단계 변경 시 초기화
if new_level != st.session_state.level:
    st.session_state.level = new_level
    st.session_state.idx = 0
    st.rerun()

# --- '📷 직접 만들기 (OCR)' 모드 실행 ---
if st.session_state.level == "📷 직접 만들기":
    st.subheader("📸 교과서 사진을 찍어보세요")
    uploaded_file = st.file_uploader("사진을 올리면 글자를 읽어드려요", type=['png', 'jpg', 'jpeg'])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='올린 사진', use_column_width=True)
        
        with st.spinner('🔍 사진에서 글자를 찾는 중입니다...'):
            try:
                # PIL 이미지를 numpy array로 변환
                img_array = np.array(image.convert('RGB'))
                result = ocr.ocr(img_array, cls=True)
                
                extracted_text = ""
                if result and result[0]:
                    for line in result[0]:
                        extracted_text += line[1][0] + " "
                
                if extracted_text.strip():
                    st.success("✅ 글자를 찾아냈어요!")
                    final_text = st.text_area("내용을 다듬어주세요:", value=extracted_text.strip(), height=150)
                    
                    if st.button("🚀 이 글로 연습하기 저장"):
                        st.session_state.data["📷 직접 만들기"].append(final_text)
                        st.session_state.idx = len(st.session_state.data["📷 직접 만들기"]) - 1
                        st.success("학습 목록에 추가되었습니다! 위 메뉴에서 확인하세요.")
                        st.rerun()
                else:
                    st.warning("⚠️ 사진에서 글자를 찾지 못했습니다. 더 선명한 사진을 써보세요.")
            except Exception as e:
                st.error(f"OCR 처리 중 오류가 발생했습니다: {e}")

# --- 일반 학습 모드 (단어/문장/문단 및 직접 만든 글) ---
current_list = st.session_state.data[st.session_state.level]

if not current_list:
    if st.session_state.level == "📷 직접 만들기":
        st.info("왼쪽 메뉴에서 사진을 업로드하여 첫 번째 연습 문장을 만들어보세요!")
    else:
        st.write("문제가 없습니다.")
else:
    # 문제 번호가 범위를 벗어나지 않도록 안전장치
    if st.session_state.idx >= len(current_list): st.session_state.idx = 0
    
    target_word = current_list[st.session_state.idx]
    
    # 문제 식별자 (횟수 저장용)
    problem_id = f"{st.session_state.level}_{st.session_state.idx}"
    p_count = st.session_state.practice_counts.get(problem_id, 0)

    # 문제 카드 레이아웃
    st.markdown('<div class="main-card">', unsafe_allow_html=True)
    col_a, col_b, col_c = st.columns([1, 4, 1])
    with col_b:
        st.write(f"**{st.session_state.level}**")
        st.markdown(f'<span class="practice-tag">🔥 {p_count}번째 연습 중</span>', unsafe_allow_html=True)
    
    # 목표 텍스트 표시 및 듣기 버튼
    t_col1, t_col2 = st.columns([5, 1])
    with t_col1:
        st.markdown(f'<p class="target-text">{target_word}</p>', unsafe_allow_html=True)
    with t_col2:
        st.write("") # 정렬용
        if st.button("🔊", help="먼저 들어보기"):
            play_tts(target_word)
            
    st.markdown('</div>', unsafe_allow_html=True)

    # 이전/다음 버튼
    c1, c2 = st.columns(2)
    with c1:
        if st.button("⬅️ 이전", use_container_width=True):
            st.session_state.idx = (st.session_state.idx - 1) % len(current_list)
            st.rerun()
    with c2:
        if st.button("다음 ➡️", use_container_width=True):
            st.session_state.idx = (st.session_state.idx + 1) % len(current_list)
            st.rerun()

    st.write("---")

    # 녹음 기능
    st.write("▼ 아래 버튼을 누르고 또박또박 읽어주세요!")
    audio = mic_recorder(start_prompt="🎤 녹음 시작", stop_prompt="🛑 녹음 완료", key=f'rec_{problem_id}')

    if audio:
        # 연습 횟수 증가 및 저장
        st.session_state.practice_counts[problem_id] = p_count + 1
        
        st.write("### 🎧 내 목소리 듣기")
        st.audio(audio['bytes'])

        st.write("---")
        st.write("🧐 **선생님 피드백 (테스트 모드)**")
        st.info("💡 지금은 아이가 읽은 내용을 선생님이 아래 칸에 직접 적어주세요. (추후 자동 인식 업데이트 예정)")
        user_input = st.text_input("아이가 읽은 내용을 적어주세요:", key=f'in_{problem_id}')
        
        if user_input:
            # 분석 실행
            stars, result_html = analyze_reading(target_word, user_input)
            
            # 별점 표시
            st.markdown(f'<div class="star-rating">{"★" * stars}{"☆" * (5-stars)}</div>', unsafe_allow_html=True)
            
            # 틀린 부분 빨간 표시 결과
            st.markdown(f'<div class="result-box">{result_html}</div>', unsafe_allow_html=True)
            
            if stars == 5:
                st.balloons()
                st.success("참 잘했어요! 만점입니다! 🌟")
            elif stars >= 3:
                st.applaud() # 박수 효과 (일부 버전에서 작동)
                st.info("거의 다 맞았어요! 조금만 더 연습해볼까요?")
