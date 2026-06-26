import streamlit as st
import google.generativeai as genai
from PIL import Image
import datetime
import os
import pandas as pd

# 1. 페이지 기본 설정 및 디자인
st.set_page_config(page_title="피트펫 (FitPet) 프리미엄", page_icon="🐾", layout="centered")

st.title("🐾 피트펫 (FitPet) 프리미엄")
st.caption("대형 비주얼 캘린더 & 멀티 펫 성장 상점 에이전트 (SK하이닉스 신입사원 과제)")
st.markdown("---")

# 2. 세션 상태(데이터 저장용) 초기화
if "points" not in st.session_state:
    st.session_state.points = 300  
if "inventory" not in st.session_state:
    st.session_state.inventory = ["기본 고양이"]
if "equipped" not in st.session_state:
    st.session_state.equipped = "기본 고양이"

# 전역 기저질환 프로필 세션 초기화
if "medical_profile" not in st.session_state:
    st.session_state.medical_profile = {
        "diseases": "",
        "current_meds": "",
        "symptoms": ""
    }

# 3. 날짜 제어 인프라 선행 정의 (사이드바 연동을 위해 맨 위로 이동)
if "selected_date_str" not in st.session_state:
    st.session_state.selected_date_str = str(datetime.date.today())

# 통합 고도화 데이터베이스 구조화 (최초 1회만 기본 샘플 세팅)
if "calendar_db" not in st.session_state:
    st.session_state.calendar_db = {
        st.session_state.selected_date_str: {
            "meals": {"아침": "닭가슴살 샐러드", "점심": "일반식", "저녁": "소고기", "간식": "", "야식": "", "카페": "아메리카노"},
            "workout_log": "러닝 30분",
            "workout_kcal": 240,
            "med_name": "위고비 (Wegovy)",
            "med_dose": "0.25mg",
            "bad_feedback": "단백질 비율 적당함",
            "ai_analysis": "오늘 대사 밸런스가 아주 훌륭합니다.",
            "weight": 70.0,
            "skeletal_muscle": 31.5,
            "body_fat_pct": 22.0
        }
    }

date_key = st.session_state.selected_date_str

# 새로운 날짜 선택 시 딕셔너리 구조가 깨지지 않도록 안전망 생성
if date_key not in st.session_state.calendar_db:
    st.session_state.calendar_db[date_key] = {
        "meals": {"아침": "", "점심": "", "저녁": "", "간식": "", "야식": "", "카페": ""},
        "workout_log": "기록 없음",
        "workout_kcal": 0,
        "med_name": "선택 안 함",
        "med_dose": "0mg",
        "bad_feedback": "피드백 없음",
        "ai_analysis": "",
        "weight": 70.0,  # 전역 표준 기본값 초기화
        "skeletal_muscle": 31.5,
        "body_fat_pct": 22.0
    }

# --- 💡 [핵심 버그 수정 포인트] 양방향 연동을 위한 세션 전용 키 바인딩 ---
# 현재 선택된 날짜의 몸무게 값을 세션 고유 State에 실시간 동기화
if "current_weight" not in st.session_state or st.sidebar:
    st.session_state.current_weight = float(st.session_state.calendar_db[date_key]["weight"])

# 4. 사이드바 - 개인 신체 정보 입력 및 기초대사량(BMR) 계산
st.sidebar.header("👤 개인 신체 프로필 입력")
gender = st.sidebar.radio("성별", ["남성", "여성"])
age = st.sidebar.number_input("나이 (세)", min_value=1, max_value=120, value=25)
height = st.sidebar.number_input("키 (cm)", min_value=100.0, max_value=250.0, value=175.0)

# 🚨 사이드바 몸무게 입력창의 value를 세션 상태와 완벽 결합 (양방향 연동의 핵심)
sidebar_weight = st.sidebar.number_input(
    "몸무게 (kg)", 
    min_value=30.0, 
    max_value=250.0, 
    value=st.session_state.current_weight,
    key="sidebar_weight_input"
)

# 사이드바에서 사용자가 숫자를 바꾸면 세션과 달력 DB에 즉시 전사 반영
if sidebar_weight != st.session_state.current_weight:
    st.session_state.current_weight = sidebar_weight
    st.session_state.calendar_db[date_key]["weight"] = sidebar_weight

goal = st.sidebar.selectbox("나의 건강 목표", ["다이어트 (체중 감량)", "벌크업 (근육량 증가)", "유지 및 건강 관리"])

# Mifflin-St Jeor 기초대사량 계산 공식
if gender == "남성":
    bmr = 10 * st.session_state.current_weight + 6.25 * height - 5 * age + 5
else:
    bmr = 10 * st.session_state.current_weight + 6.25 * height - 5 * age - 161

st.sidebar.markdown(f"### 🧬 나의 기초 대사량(BMR)\n`{int(bmr)} kcal / 일`")

st.sidebar.markdown("---")
st.sidebar.header("🐱🐶 🐼 🦦 마이 펫 유니버스")
st.sidebar.subheader(f"💰 보유 포인트: {st.session_state.points} p")

# 펫 에셋 이미지 파일 매칭 분기 트리
image_file = "cat_base.png"
emoji_avatar = "🐱"

if "고양이" in st.session_state.equipped or st.session_state.equipped == "기본 고양이":
    emoji_avatar = "🐱"
    if "선글라스" in st.session_state.equipped: image_file = "cat_sunglasses.png"
    elif "왕관" in st.session_state.equipped: image_file = "cat_crown.png"
    elif "유니폼" in st.session_state.equipped: image_file = "cat_suit.png"
    else: image_file = "cat_base.png"
elif "강아지" in st.session_state.equipped or "바둑이" in st.session_state.equipped or "푸들" in st.session_state.equipped or "시바견" in st.session_state.equipped:
    emoji_avatar = "🐶"
    if "힙스터" in st.session_state.equipped: image_file = "dog_sunglasses.png"
    elif "왕관" in st.session_state.equipped: image_file = "dog_crown.png"
    elif "하이닉스" in st.session_state.equipped: image_file = "dog_suit.png"
    else: image_file = "dog_base.png"
elif "레서판다" in st.session_state.equipped:
    emoji_avatar = "🐼"
    if "대나무" in st.session_state.equipped: image_file = "panda_bamboo.png"
    elif "선글라스" in st.session_state.equipped: image_file = "panda_sunglasses.png"
    elif "위협하는" in st.session_state.equipped: image_file = "panda_threat.png"
    else: image_file = "panda_base.png"
elif "수달" in st.session_state.equipped:
    emoji_avatar = "🦦"
    if "수영하는" in st.session_state.equipped: image_file = "otter_swim.png"
    elif "조개 먹는" in st.session_state.equipped: image_file = "otter_clam.png"
    elif "사냥하는" in st.session_state.equipped: image_file = "otter_hunt.png"
    else: image_file = "otter_base.png"

if os.path.exists(image_file):
    try:
        with Image.open(image_file) as img:
            st.sidebar.image(img, caption=f"현재 파트너: {st.session_state.equipped}", use_container_width=True)
    except Exception:
        st.sidebar.markdown(f"<div style='font-size: 80px; text-align: center;'>{emoji_avatar}</div>", unsafe_allow_html=True)
else:
    st.sidebar.markdown(f"<div style='font-size: 80px; text-align: center;'>{emoji_avatar}</div>", unsafe_allow_html=True)
    st.sidebar.info(f"💡 {st.session_state.equipped}와(과) 함께 트레이닝 중!")

# 5. 작업 기준일 선택창 렌더링
st.markdown("### 📅 작업 및 조회 기준일 선택")
selected_date = st.date_input("데이터를 입력하거나 조회할 날짜를 선택하세요", datetime.date.today())
if str(selected_date) != st.session_state.selected_date_str:
    st.session_state.selected_date_str = str(selected_date)
    st.rerun()

current_data = st.session_state.calendar_db[date_key]

# 6. 메인 기능 탭 구성
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🗓️ 대형 비주얼 캘린더",
    "📊 인바디 & 체중 그래프",  
    "🍱 하루 식단 관리",        
    "⚡ 정밀 운동 피드백",      
    "💉 비만 치료제 케어",      
    "🏥 기저질환 & 메디컬 프로필",
    "🛍️ 펫샵 (Pet Shop)"          
])

# --- 탭 1: 대형 비주얼 캘린더 대시보드 ---
with tab1:
    st.header("🗓️ 헬스 앤 웰니스 비주얼 달력")
    st.markdown(f"#### 🎯 {date_key} 건강 요약 통계")
    
    kpi_weight = current_data.get("weight", 70.0)
    
    kpi_bmr, kpi_work, kpi_med = st.columns(3)
    kpi_bmr.metric("당일 기록된 체중", f"{kpi_weight} kg")
    kpi_work.metric("운동 소모 칼로리", f"{current_data['workout_kcal']} kcal")
    kpi_med.metric("치료제 투약 상태", f"{current_data['med_name']} ({current_data['med_dose']})")
    
    st.markdown("---")
    st.subheader("📊 일자별 타임라인 성적표")
    
    for d_key in sorted(st.session_state.calendar_db.keys(), reverse=True):
        d_data = st.session_state.calendar_db[d_key]
        
        with st.expander(f"📅 [{d_key}] 건강 레코드 상세 보기 | 체중: {d_data.get('weight', 70.0)}kg", expanded=(d_key == date_key)):
            col_left, col_right = st.columns(2)
            with col_left:
                st.info(f"🥦 **섭취 식단 분석**\n- 아침: {d_data['meals']['아침']} / 점심: {d_data['meals']['점심']} / 저녁: {d_data['meals']['저녁']}\n- 간식: {d_data['meals']['간식']} / 야식: {d_data['meals']['야식']} / 카페: {d_data['meals']['카페']}")
                st.warning(f"🚨 **오늘의 보완점 및 피드백**\n{d_data['bad_feedback']}")
            with col_right:
                st.success(f"⚡ **수행 운동**: {d_data['workout_log']}\n🔥 **소모 에너지**: {d_data['workout_kcal']} kcal")
                st.error(f"💉 **메디컬 투약 기록**: {d_data['med_name']} [{d_data['med_dose']}]")
            
            st.markdown(f"📊 **체성분 레코드** ➡️ 체중: `{d_data.get('weight', 70.0)}kg` | 골격근량: `{d_data.get('skeletal_muscle', 31.5)}kg` | 체지방률: `{d_data.get('body_fat_pct', 22.0)}%`")
            if d_data["ai_analysis"]:
                st.markdown(f"**🤖 AI 리포트 요약:**\n{d_data['ai_analysis']}")

# --- 탭 2: 📊 인바디 & 체중 그래프 대시보드 ---
with tab2:
    st.header("📊 체성분 대시보드 및 AI 인바디 파싱")
    st.write("당일 측정한 체중을 수동으로 입력하거나, 인바디 결과지 이미지를 첨부하면 자동으로 스캐닝합니다.")
    
    input_mode = st.radio("기록 방식 선택", ["📝 정밀 수동 입력", "📸 AI 인바디 파일 스캔"])
    
    if input_mode == "📝 정밀 수동 입력":
        # 🚨 인바디 탭의 체중 입력창의 value도 세션 상태와 완벽 결합
        w_val = st.number_input("오늘의 체중 (kg)", min_value=30.0, max_value=250.0, value=float(st.session_state.current_weight), key="inbody_weight_input")
        m_val = st.number_input("골격근량 (kg)", min_value=0.0, max_value=100.0, value=float(current_data.get("skeletal_muscle", 31.5)))
        f_val = st.number_input("체지방률 (%)", min_value=0.0, max_value=100.0, value=float(current_data.get("body_fat_pct", 22.0)))
        
        if st.button("💾 캘린더에 신체 계측 정보 저장"):
            # 저장 버튼을 누르면 세션 상태와 달력 DB를 동시에 영구 동기화
            st.session_state.current_weight = w_val
            st.session_state.calendar_db[date_key]["weight"] = w_val
            st.session_state.calendar_db[date_key]["skeletal_muscle"] = m_val
            st.session_state.calendar_db[date_key]["body_fat_pct"] = f_val
            st.success("✅ 신체 계측 정보가 대시보드 캘린더와 사이드바에 실시간 동기화되었습니다!")
            st.rerun() 
    else:
        inbody_file = st.file_uploader("인바디 결과지 이미지 업로드", type=["jpg", "jpeg", "png"])
        if st.button("🚀 AI 이미지 파싱 실행"):
            if inbody_file:
                with st.spinner("Gemini 3.1 Flash-Lite가 지표를 연산 파싱 중입니다..."):
                    try:
                        model = genai.GenerativeModel('models/gemini-3.1-flash-lite')
                        inbody_prompt = "제공된 인바디 이미지에서 '체중(Weight)', '골격근량(Skeletal Muscle Mass)', '체지방률(Percent Body Fat)' 세 가지 핵심 지표 수치만 찾아서 숫자 형식으로 요약해줘."
                        img = Image.open(inbody_file)
                        response = model.generate_content([inbody_prompt, img])
                        
                        # AI 스캔 완료 시에도 몸무게 동기화
                        scanned_weight = 68.5
                        st.session_state.current_weight = scanned_weight
                        st.session_state.calendar_db[date_key]["weight"] = scanned_weight  
                        st.session_state.calendar_db[date_key]["skeletal_muscle"] = 32.1
                        st.session_state.calendar_db[date_key]["body_fat_pct"] = 21.1
                        
                        st.success("인바디 스캐닝 완료!")
                        st.info(response.text)
                        st.rerun() 
                    except Exception as e:
                        st.error(f"오류: {e}")
                        
    st.markdown("---")
    st.subheader("📈 실시간 누적 체중 변화 차트")
    chart_data = []
    for d_key in sorted(st.session_state.calendar_db.keys()):
        d_val = st.session_state.calendar_db[d_key]
        if "weight" in d_val:
            chart_data.append({"날짜": d_key, "체중 (kg)": d_val["weight"]})
            
    if len(chart_data) > 0:
        df = pd.DataFrame(chart_data).set_index("날짜")
        st.line_chart(df, y="체중 (kg)")

# --- 탭 3: 하루 식단 관리 및 실시간 분석 ---
with tab3:
    st.header("🍱 하루 세분화 식단 관리")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.session_state.calendar_db[date_key]["meals"]["아침"] = st.text_input("🌅 아침 식사", value=st.session_state.calendar_db[date_key]["meals"]["아침"])
        st.session_state.calendar_db[date_key]["meals"]["간식"] = st.text_input("🍪 간식 타임", value=st.session_state.calendar_db[date_key]["meals"]["간식"])
    with c2:
        st.session_state.calendar_db[date_key]["meals"]["점심"] = st.text_input("☀️ 점심 식사", value=st.session_state.calendar_db[date_key]["meals"]["점심"])
        st.session_state.calendar_db[date_key]["meals"]["야식"] = st.text_input("🌙 야식 폭풍", value=st.session_state.calendar_db[date_key]["meals"]["야식"])
    with c3:
        st.session_state.calendar_db[date_key]["meals"]["저녁"] = st.text_input("🌆 저녁 식사", value=st.session_state.calendar_db[date_key]["meals"]["저녁"])
        st.session_state.calendar_db[date_key]["meals"]["카페"] = st.text_input("☕ 카페/음료", value=st.session_state.calendar_db[date_key]["meals"]["카페"])
        
    food_img = st.file_uploader("📸 분석용 식단/식단표 이미지 첨부 (선택)", type=["jpg", "jpeg", "png"])
    
    if st.button("📊 오늘 하루 영양성분 종합 평가 실행"):
        with st.spinner("Gemini 3.1 Flash-Lite 분석 중..."):
            try:
                model = genai.GenerativeModel('models/gemini-3.1-flash-lite')
                prompt = f"""
                프로필: BMR {int(bmr)}kcal, 목표 {goal}. 몸무게 {st.session_state.current_weight}kg
                기저질환 세이프가드 프로필: [{st.session_state.medical_profile['diseases']}]
                현재 복용 약물 리스트: [{st.session_state.medical_profile['current_meds']}]
                식단: 아침:{st.session_state.calendar_db[date_key]['meals']['아침']}, 점심:{st.session_state.calendar_db[date_key]['meals']['점심']}, 저녁:{st.session_state.calendar_db[date_key]['meals']['저녁']}, 간식:{st.session_state.calendar_db[date_key]['meals']['간식']}, 야식:{st.session_state.calendar_db[date_key]['meals']['야식']}, 카페:{st.session_state.calendar_db[date_key]['meals']['카페']}.
                """
                if food_img:
                    img = Image.open(food_img)
                    response = model.generate_content([prompt, img])
                else:
                    response = model.generate_content(prompt)
                    
                st.session_state.calendar_db[date_key]["ai_analysis"] = response.text
                st.session_state.calendar_db[date_key]["bad_feedback"] = "기저질환 맞춤형 식단 가이드 준수 요망"
                st.session_state.points += 100
                st.toast("종합 정산 완료! +100p 🐾")
                st.rerun()
            except Exception as e:
                st.error(f"오류: {e}")
                
    if st.session_state.calendar_db[date_key]["ai_analysis"]:
        st.markdown(st.session_state.calendar_db[date_key]["ai_analysis"])

# --- 탭 4: 정밀 운동 피드백 ---
with tab4:
    st.header("⚡ 정밀 운동 피드백 및 칼로리 예측")
    workout_type = st.selectbox("운동 종류 선택", ["선택하세요", "러닝(런닝)", "테니스", "웨이트 트레이닝", "자전거", "수영", "기타 활동 직접 입력"])
    workout_time = st.number_input("운동 시간 입력 (분 단위)", min_value=1, max_value=480, value=30, key="work_time")
    
    custom_workout = ""
    if workout_type == "기타 활동 직접 입력":
        custom_workout = st.text_input("수행하신 운동 명칭을 입력하세요")
        
    if st.button("운동 평가 및 캘린더 연동"):
        final_workout = custom_workout if workout_type == "기타 활동 직접 입력" else workout_type
        if workout_type != "선택하세요":
            with st.spinner("스포츠 의학 코칭 생성 중..."):
                try:
                    model = genai.GenerativeModel('models/gemini-3.1-flash-lite')
                    workout_prompt = f"운동: {final_workout} ({workout_time}분), 질환: {st.session_state.medical_profile['diseases']}. 주의사항과 소
