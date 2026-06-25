import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# 1. 페이지 기본 설정 및 디자인
st.set_page_config(page_title="피트펫 (FitPet)", page_icon="🐾", layout="centered")

st.title("🐾 피트펫 (FitPet)")
st.caption("올인원 헬스 & 메디컬 케어 에이전트 (SK하이닉스 신입사원 과제)")
st.markdown("---")

# 2. 세션 상태(데이터 저장용) 초기화
if "points" not in st.session_state:
    st.session_state.points = 0
if "history" not in st.session_state:
    st.session_state.history = []

# Gemini API 키 설정 (Streamlit Secrets 연동)
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.warning("API Key가 Secrets에 설정되지 않았거나 올바르지 않습니다. 우측 하단 Manage app -> Settings -> Secrets를 확인해 주세요.")

# 3. 사이드바 - 마이 펫 대시보드 (보상 시스템)
st.sidebar.header("🐱 마이 펫 성장 일지")
st.sidebar.subheader(f"현재 누적 포인트: {st.session_state.points} p")

# 포인트별 펫 상태 변화 심리 유도
if st.session_state.points == 0:
    st.sidebar.info("🌱 아기 펫이 주인의 건강 기록을 기다리고 있어요!")
elif st.session_state.points < 300:
    st.sidebar.success("🐱 펫이 한 걸음 성장했습니다! (LV.2 어린이 펫)")
else:
    st.sidebar.success("👑 펫이 멋진 옷을 입었습니다! (LV.MAX 마스터 펫)")

# 4. 메인 기능 탭 구성
tab1, tab2, tab3 = st.tabs(["🥦 식단 관리 (Vision)", "⚡ 운동 관리 (Learning)", "💉 비만 치료제 케어"])

# --- 탭 1: 식단 관리 ---
with tab1:
    st.header("🥦 스마트 식단 비전 분석")
    st.write("식단 사진을 올리거나 텍스트로 입력하면 AI가 자동으로 칼로리와 탄단지를 분석합니다.")
    
    food_img = st.file_uploader("식단 사진 업로드 (선택)", type=["jpg", "jpeg", "png"])
    food_text = st.text_input("식단 텍스트 입력 (예: 점심에 닭가슴살 샐러드랑 아메리카노 먹었어)")
    
    if st.button("식단 분석 및 포인트 받기"):
        if food_img or food_text:
            with st.spinner("Gemini AI가 식단을 분석 중입니다..."):
                try:
                    # 최신 모델 'models/gemini-3.1-flash-lite'로 지정
                    model = genai.GenerativeModel('models/gemini-3.1-flash-lite')
                    prompt = "당신은 영양사 에이전트입니다. 제공된 이미지 또는 텍스트를 보고 해당 식단의 추정 칼로리(kcal)와 탄수화물, 단백질, 지방 비율을 표 형태로 명확히 알려주고 다정한 피드백을 한 줄 남겨주세요."
                    
                    if food_img:
                        img = Image.open(food_img)
                        response = model.generate_content([prompt, img])
                    else:
                        response = model.generate_content([prompt, food_text])
                    
                    st.markdown(response.text)
                    st.session_state.points += 100
                    st.toast("식단 기록 완료! +100p 🐾")
                except Exception as e:
                    st.error(f"오류가 발생했습니다: {e}")
        else:
            st.warning("사진을 업로드하거나 텍스트를 입력해 주세요.")

# --- 탭 2: 운동 관리 ---
with tab2:
    st.header("⚡ 웨어러블 연동 운동 학습")
    st.write("오늘 스마트워치에 기록된 주요 활동이나 소모 칼로리를 알려주세요.")
    
    workout_input = st.text_area("오늘 어떤 운동을 주로 하셨나요? (AI가 패턴을 학습합니다)", 
                                 placeholder="예: 오늘 퇴근하고 헬스장에서 등 운동 50분 하고 유산소 20분 탔어.")
    
    if st.button("운동 일지 등록 (+100p)"):
        if workout_input:
            with st.spinner("운동 패턴 분석 중..."):
                try:
                    # 최신 모델 'models/gemini-3.1-flash-lite'로 지정
                    model = genai.GenerativeModel('models/gemini-3.1-flash-lite')
                    workout_prompt = f"사용자의 운동 기록: '{workout_input}'. 이 패턴을 기반으로 칭찬과 함께 다음 운동 시 주의점이나 팁을 하이닉스 신입사원 트레이너 컨셉으로 다정하게 말해줘."
                    response = model.generate_content(workout_prompt)
                    st.info(response.text)
                    st.session_state.points += 100
                    st.toast("운동 기록 완료! +100p 🐾")
                except Exception as e:
                    st.error(f"오류가 발생했습니다: {e}")
        else:
            st.warning("운동 내용을 입력해 주세요.")

# --- 탭 3: 비만 치료제 케어 ---
with tab3:
    st.header("💉 비만 치료제 (위고비/마운자로) 복용 가이드")
    st.write("치료제 복용 일정을 관리하고 부작용 발생 여부를 안전하게 체크합니다.")
    
    med_name = st.selectbox("복용 중인 치료제 선택", ["선택 안 함", "위고비 (Wegovy)", "마운자로 (Mounjaro)"])
    
    if med_name != "선택 안 함":
        st.success(f"📢 {med_name} 복용 당일 알림: 주차별 정량 투약을 준수하세요.")
        
        st.write("**🚨 오늘 아래와 같은 부작용 증상이 있으신가요? (체크)**")
        side_1 = st.checkbox("메스꺼움 / 구토")
        side_2 = st.checkbox("설사 / 변비")
        side_3 = st.checkbox("심한 복통")
        
        if st.button("복용 및 부작용 상태 기록 (+100p)"):
            if side_1 or side_2 or side_3:
                st.error("⚠️ 경고: GLP-1 계열 약물의 부작용 조짐이 보입니다. 증상이 지속되거나 심해질 경우 즉시 투약을 중단하고 전문의와 상담하시기 바랍니다.")
            else:
                st.success("✅ 이상 없음: 안전하게 복용이 기록되었습니다. 건강한 다이어트를 응원합니다!")
            st.session_state.points += 100
            st.toast("복약 및 부작용 체크 완료! +100p 🐾")
