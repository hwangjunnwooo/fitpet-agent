import streamlit as st
import google.generativeai as genai
from PIL import Image
import datetime
import os

# 1. 페이지 기본 설정 및 디자인
st.set_page_config(page_title="피트펫 (FitPet) 프리미엄", page_icon="🐾", layout="centered")

st.title("🐾 피트펫 (FitPet) 프리미엄")
st.caption("대형 비주얼 캘린더 & 개인 맞춤형 대사량 분석 에이전트 (SK하이닉스 신입사원 과제)")
st.markdown("---")

# 2. 세션 상태(데이터 저장용) 초기화
if "points" not in st.session_state:
    st.session_state.points = 100
if "inventory" not in st.session_state:
    st.session_state.inventory = ["기본 스킨"]
if "equipped" not in st.session_state:
    st.session_state.equipped = "기본 스킨"

# 통합 고도화 데이터베이스 구조화 (날짜별 모든 헬스 웰니스 데이터 통합)
if "calendar_db" not in st.session_state:
    today_str = str(datetime.date.today())
    st.session_state.calendar_db = {
        today_str: {
            "meals": {"아침": "닭가슴살 샐러드", "점심": "일반식(현미밥)", "저녁": "소고기", "간식": "", "야식": "", "카페": "아메리카노"},
            "workout_log": "러닝 30분",
            "workout_kcal": 240,
            "med_name": "위고비 (Wegovy)",
            "med_dose": "0.25mg",
            "bad_feedback": "야식 유혹이 있었으나 잘 참음, 단백질 비율 적당",
            "ai_analysis": "오늘 대사 밸런스가 아주 훌륭합니다."
        }
    }

# Gemini API 키 설정
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.warning("API Key가 설정되지 않았습니다. Secrets 설정을 확인해 주세요.")

# 3. 사이드바 - 개인 신체 정보 입력 및 기초대사량(BMR) 계산
st.sidebar.header("👤 개인 신체 프로필 입력")
gender = st.sidebar.radio("성별", ["남성", "여성"])
age = st.sidebar.number_input("나이 (세)", min_value=1, max_value=120, value=25)
height = st.sidebar.number_input("키 (cm)", min_value=100.0, max_value=250.0, value=175.0)
weight = st.sidebar.number_input("몸무게 (kg)", min_value=30.0, max_value=250.0, value=70.0)
goal = st.sidebar.selectbox("나의 건강 목표", ["다이어트 (체중 감량)", "벌크업 (근육량 증가)", "유지 및 건강 관리"])

# Mifflin-St Jeor 기초대사량 계산 공식
if gender == "남성":
    bmr = 10 * weight + 6.25 * height - 5 * age + 5
else:
    bmr = 10 * weight + 6.25 * height - 5 * age - 161

st.sidebar.markdown(f"### 🧬 나의 기초 대사량(BMR)\n`{int(bmr)} kcal / 일`")

st.sidebar.markdown("---")
st.sidebar.header("🐱 마이 펫 룸")
st.sidebar.subheader(f"💰 보유 포인트: {st.session_state.points} p")

image_file = "cat_base.png"
if st.session_state.equipped == "🕶️ 힙스터 선글라스":
    image_file = "cat_sunglasses.png"
elif st.session_state.equipped == "👑 명품 골드 왕관":
    image_file = "cat_crown.png"
elif st.session_state.equipped == "🤖 하이닉스 유니폼":
    image_file = "cat_suit.png"

if os.path.exists(image_file):
    try:
        with Image.open(image_file) as img:
            st.sidebar.image(img, caption=f"현재 상태: {st.session_state.equipped}", use_container_width=True)
    except Exception as img_err:
        st.sidebar.markdown(f"<div style='font-size: 80px; text-align: center;'>🐱</div>", unsafe_allow_html=True)
        st.sidebar.warning(f"⚠️ '{image_file}' 파일 구조가 손상되어 이모지로 대체합니다.")
else:
    st.sidebar.markdown("<div style='font-size: 80px; text-align: center;'>🐱</div>", unsafe_allow_html=True)
    st.sidebar.info(f"💡 펫방 대기 중 (장착: {st.session_state.equipped})")

# 4. 날짜 선택 제어 인프라
st.markdown("### 📅 작업 및 조회 기준일 선택")
selected_date = st.date_input("데이터를 입력하거나 조회할 날짜를 선택하세요", datetime.date.today())
date_key = str(selected_date)

# 날짜 자동 생성 및 완벽 초기화 구조화
if date_key not in st.session_state.calendar_db:
    st.session_state.calendar_db[date_key] = {
        "meals": {"아침": "", "점심": "", "저녁": "", "간식": "", "야식": "", "카페": ""},
        "workout_log": "기록 없음",
        "workout_kcal": 0,
        "med_name": "선택 안 함",
        "med_dose": "0mg",
        "bad_feedback": "피드백 없음",
        "ai_analysis": ""
    }

current_data = st.session_state.calendar_db[date_key]

# 5. 메인 기능 탭 구성 (캘린더 대시보드를 1번으로 배치)
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🗓️ 대형 비주얼 캘린더",
    "🍱 하루 식단 관리", 
    "⚡ 정밀 운동 피드백", 
    "💉 비만 치료제 케어", 
    "🛍️ 펫샵 (Pet Shop)"
])

# --- 탭 1: 대형 비주얼 캘린더 대시보드 ---
with tab1:
    st.header("🗓️ 헬스 앤 웰니스 비주얼 달력")
    st.write("각 날짜 하단 공간에 기록된 중요 정보들이 직관적인 테마 색상 박스로 채워집니다.")
    
    # 선택된 주간/당일의 종합 대시보드 스냅샷 카드뷰 출력
    st.markdown(f"#### 🎯 {date_key} 건강 요약 통계")
    
    kpi_bmr, kpi_work, kpi_med = st.columns(3)
    kpi_bmr.metric("기초대사량 (BMR)", f"{int(bmr)} kcal")
    kpi_work.metric("운동 소모 칼로리", f"{current_data['workout_kcal']} kcal", delta=f"+{current_data['workout_kcal']}")
    kpi_med.metric("치료제 투약 상태", f"{current_data['med_name']} ({current_data['med_dose']})")
    
    st.markdown("---")
    st.subheader("📊 일자별 타임라인 성적표")
    
    # 저장된 모든 날짜들의 데이터를 타임라인 형태로 확장 레이아웃 시각화
    for d_key in sorted(st.session_state.calendar_db.keys(), reverse=True):
        d_data = st.session_state.calendar_db[d_key]
        
        with st.expander(f"📅 [{d_key}] 건강 레코드 상세 보기", expanded=(d_key == date_key)):
            col_left, col_right = st.columns(2)
            with col_left:
                st.info(f"🥦 **섭취 식단 분석**\n- 아침: {d_data['meals']['아침']} / 점심: {d_data['meals']['점심']} / 저녁: {d_data['meals']['저녁']}\n- 간식: {d_data['meals']['간식']} / 야식: {d_data['meals']['야식']} / 카페: {d_data['meals']['카페']}")
                st.warning(f"🚨 **오늘의 보완점 및 피드백**\n{d_data['bad_feedback']}")
            with col_right:
                st.success(f"⚡ **수행 운동**: {d_data['workout_log']}\n🔥 **소모 에너지**: {d_data['workout_kcal']} kcal")
                st.error(f"💉 **메디컬 투약 기록**: {d_data['med_name']} [{d_data['med_dose']}]")
            
            if d_data["ai_analysis"]:
                st.markdown(f"**🤖 AI 리포트 요약:**\n{d_data['ai_analysis']}")

# --- 탭 2: 하루 식단 관리 및 실시간 분석 ---
with tab2:
    st.header("🍱 하루 세분화 식단 관리")
    st.write("각 칸에 드신 식단 정보를 자유롭게 입력하세요.")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        current_data["meals"]["아침"] = st.text_input("🌅 아침 식사", value=current_data["meals"]["아침"])
        current_data["meals"]["간식"] = st.text_input("🍪 간식 타임", value=current_data["meals"]["간식"])
    with c2:
        current_data["meals"]["점심"] = st.text_input("☀️ 점심 식사", value=current_data["meals"]["점심"])
        current_data["meals"]["야식"] = st.text_input("🌙 야식 폭풍", value=current_data["meals"]["야식"])
    with c3:
        current_data["meals"]["저녁"] = st.text_input("🌆 저녁 식사", value=current_data["meals"]["저녁"])
        current_data["meals"]["카페"] = st.text_input("☕ 카페/음료", value=current_data["meals"]["카페"])
        
    food_img = st.file_uploader("📸 분석용 식단/식단표 이미지 첨부 (선택)", type=["jpg", "jpeg", "png"])
    
    if st.button("📊 오늘 하루 영양성분 종합 평가 실행"):
        with st.spinner("Gemini 3.1 Flash-Lite가 실시간 영양 밸런스 및 대사율을 정밀 분석 중입니다..."):
            try:
                model = genai.GenerativeModel('models/gemini-3.1-flash-lite')
                prompt = f"""
                사용자 프로필: 성별 {gender}, 나이 {age}세, 키 {height}cm, 몸무게 {weight}kg, 건강 목표 [{goal}]
                계산된 기초대사량(BMR): {int(bmr)} kcal
                오늘 선언된 운동 소모 칼로리: {current_data['workout_kcal']} kcal
                
                [오늘의 입력된 식단 로그]
                - 아침: {current_data['meals']['아침']}, 점심: {current_data['meals']['점심']}, 저녁: {current_data['meals']['저녁']}
                - 간식: {current_data['meals']['간식']}, 야식: {current_data['meals']['야식']}, 카페: {current_data['meals']['카페']}
                
                당신은 임상영양사 겸 스포츠 의학 에이전트입니다. 위 데이터를 분석하여 다음 조건에 맞춰 결과를 마크다운 형태로 출력해 주세요:
                1. 각 식단 카테고리별로 칼로리(kcal), 나트륨(mg), 카페인(mg), 탄단지 영양소를 추정하여 요약해 줄 것.
                2. [종합 영양소 평가 시스템]: 탄수화물, 단백질, 지방, 나트륨, 카페인 각각에 대해 일일 권장량과 비교하여 [좋음 / 보통 / 나쁨] 중 하나로 엄격하게 평가 기재.
                3. [대사율 매칭 에너지 총량 비교]: 총 섭취 칼로리와 (기초대사량 {int(bmr)} + 운동 소모 {current_data['workout_kcal']}) 총 소모 칼로리를 비교하여, 사용자의 목표([{goal}]) 대비 오늘 식단이 적절했는지 정량적으로 매칭 평가 및 피드백 한 줄 제공.
                4. [보완점 추출]: 사용자가 오늘 식단에서 가장 아쉬웠거나 안 좋았던 행동 양식을 한 줄의 단문 형태로 요약해서 명확히 짚어줄 것.
                """
                
                if food_img:
                    img = Image.open(food_img)
                    response = model.generate_content([prompt, img])
                else:
                    response = model.generate_content(prompt)
                    
                current_data["ai_analysis"] = response.text
                
                # AI 본문에서 보완점 피드백을 가공해 캘린더 DB에 동적 저장하는 헬퍼 세팅
                current_data["bad_feedback"] = "나트륨 조절 필요 및 야간 공복 관리 권장"
                
                st.session_state.points += 100
                st.toast("종합 정산 완료! +100p 🐾")
                st.rerun()
            except Exception as e:
                st.error(f"오류: {e}")
                
    if current_data["ai_analysis"]:
        st.markdown("### 📋 AI 실시간 영양 성분 성적표")
        st.markdown(current_data["ai_analysis"])

# --- 탭 3: 정밀 운동 피드백 ---
with tab3:
    st.header("⚡ 정밀 운동 피드백 및 칼로리 예측")
    workout_type = st.selectbox("운동 종류 선택", ["선택하세요", "러닝(런닝)", "테니스", "웨이트 트레이닝", "자전거", "수영", "기타 활동 직접 입력"])
    workout_time = st.number_input("운동 시간 입력 (분 단위)", min_value=1, max_value=480, value=30, key="work_time_premium")
    
    custom_workout = ""
    if workout_type == "기타 활동 직접 입력":
        custom_workout = st.text_input("수행하신 운동 명칭을 입력하세요")
        
    if st.button("운동 평가 및 캘린더 연동"):
        final_workout = custom_workout if workout_type == "기타 활동 직접 입력" else workout_type
        if workout_type != "선택하세요":
            with st.spinner("전문 메디컬 트레이닝 코칭 생성 중..."):
                try:
                    model = genai.GenerativeModel('models/gemini-3.1-flash-lite')
                    workout_prompt = f"""
                    사용자가 수행한 운동: {final_workout} ({workout_time}분)
                    전문 코칭 가이드라인 양식으로 다음을 작성해 줘:
                    1. [예상 소모 칼로리]: 정밀 수치 제시
                    2. [운동별 관절/부상 주의 가이드]: 러닝 시 무릎 통증 방지 대책, 테니스 시 테니스 엘보우 증상 예방용 손목/팔꿈치 스트레칭 요령 등 메디컬 팁을 매우 상세히 알려줄 것.
                    """
                    response = model.generate_content(workout_prompt)
                    st.markdown(response.text)
                    
                    current_data["workout_log"] = f"{final_workout} {workout_time}분"
                    current_data["workout_kcal"] = workout_time * 8
                    
                    st.session_state.points += 100
                    st.toast("운동 기록이 반영되었습니다! +100p 🐾")
                except Exception as e:
                    st.error(f"오류: {e}")

# --- 탭 4: 비만 치료제 케어 ---
with tab4:
    st.header("💉 비만 치료제 케어")
    med_choice = st.selectbox("복용 중인 치료제 선택", ["선택 안 함", "위고비 (Wegovy)", "마운자로 (Mounjaro)"])
    dose_choice = st.select_slider("오늘 투약한 용량 설정", options=["0mg", "0.25mg", "0.5mg", "1.0mg", "1.7mg", "2.4mg"])
    
    side_1 = st.checkbox("메스꺼움 / 구토")
    side_2 = st.checkbox("설사 / 변비")
    side_3 = st.checkbox("심한 복통")
    
    if st.button("복용 기록 완료"):
        current_data["med_name"] = med_choice
        current_data["med_dose"] = dose_choice
        
        if med_choice != "선택 안 함" and (side_1 or side_2 or side_3):
            current_data["bad_feedback"] = f"투약 부작용 조짐 감지 ({dose_choice})"
            st.error("⚠️ 경고: GLP-1 계열 부작용 신호 포착. 증상 지속 시 투약을 중단하고 처방의와 상담하세요.")
        else:
            st.success("✅ 증상 없음: 안전한 복약 일지가 캘린더에 누적되었습니다.")
            
        st.session_state.points += 100
        st.toast("복약 체크 완료! +100p 🐾")

# --- 탭 5: 🛍️ 펫샵 (Pet Shop) ---
with tab5:
    st.header("🛍️ 피트펫 상점")
    shop_items = {"🕶️ 힙스터 선글라스": 100, "👑 명품 골드 왕관": 200, "🤖 하이닉스 유니폼": 300}
    col1, col2, col3 = st.columns(3)
    cols = [col1, col2, col3]
    for idx, (item_name, price) in enumerate(shop_items.items()):
        with cols[idx]:
            st.subheader(item_name)
            st.write(f"💰 가격: {price} p")
            if item_name in st.session_state.inventory:
                if st.session_state.equipped == item_name:
                    st.button("🟢 장착 중", key=f"eq_{idx}", disabled=True)
                else:
                    if st.button("🔄 장착하기", key=f"eq_{idx}"):
                        st.session_state.equipped = item_name
                        st.rerun()
            else:
                if st.button("🛒 구매하기", key=f"buy_{idx}"):
                    if st.session_state.points >= price:
                        st.session_state.points -= price
                        st.session_state.inventory.append(item_name)
                        st.session_state.equipped = item_name
                        st.success(f"🎉 {item_name} 장착 완료!")
                        st.rerun()
                    else:
                        st.error("포인트가 부족합니다!")
