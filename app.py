import streamlit as st
import google.generativeai as genai
from PIL import Image
import datetime
import os

# 1. 페이지 기본 설정 및 디자인
st.set_page_config(page_title="피트펫 (FitPet) 프리미엄", page_icon="🐾", layout="centered")

st.title("🐾 피트펫 (FitPet) 프리미엄")
st.caption("대형 비주얼 캘린더 & 멀티 펫 성장 상점 에이전트 (SK하이닉스 신입사원 과제)")
st.markdown("---")

# 2. 세션 상태(데이터 저장용) 초기화
if "points" not in st.session_state:
    st.session_state.points = 200  # 테스트를 원활하게 하실 수 있도록 초기 포인트를 200p로 상향 세팅했습니다!
if "inventory" not in st.session_state:
    st.session_state.inventory = ["기본 고양이"]
if "equipped" not in st.session_state:
    st.session_state.equipped = "기본 고양이"

# 통합 고도화 데이터베이스 구조화
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
st.sidebar.header("🐱🐶 마이 펫 룸")
st.sidebar.subheader(f"💰 보유 포인트: {st.session_state.points} p")

# 어떤 펫 분기인지 파일 매칭 트리 설계
image_file = "cat_base.png"
emoji_avatar = "🐱"

if st.session_state.equipped == "기본 고양이":
    image_file = "cat_base.png"; emoji_avatar = "🐱"
elif st.session_state.equipped == "🕶️ 힙스터 선글라스 (고양이)":
    image_file = "cat_sunglasses.png"; emoji_avatar = "🕶️🐱"
elif st.session_state.equipped == "👑 명품 골드 왕관 (고양이)":
    image_file = "cat_crown.png"; emoji_avatar = "👑🐱"
elif st.session_state.equipped == "🤖 하이닉스 유니폼 (고양이)":
    image_file = "cat_suit.png"; emoji_avatar = "🤖🐱"
elif st.session_state.equipped == "기본 강아지":
    image_file = "dog_base.png"; emoji_avatar = "🐶"
elif st.session_state.equipped == "🕶️ 힙스터 강아지":
    image_file = "dog_sunglasses.png"; emoji_avatar = "🕶️🐶"
elif st.session_state.equipped == "👑 왕관 강아지":
    image_file = "dog_crown.png"; emoji_avatar = "👑🐶"
elif st.session_state.equipped == "🤖 하이닉스 강아지":
    image_file = "dog_suit.png"; emoji_avatar = "🤖🐶"

if os.path.exists(image_file):
    try:
        with Image.open(image_file) as img:
            st.sidebar.image(img, caption=f"현재 파트너: {st.session_state.equipped}", use_container_width=True)
    except Exception as img_err:
        st.sidebar.markdown(f"<div style='font-size: 80px; text-align: center;'>{emoji_avatar}</div>", unsafe_allow_html=True)
else:
    st.sidebar.markdown(f"<div style='font-size: 80px; text-align: center;'>{emoji_avatar}</div>", unsafe_allow_html=True)
    st.sidebar.info(f"💡 {st.session_state.equipped}와 함께 달리는 중!")

# 4. 날짜 선택 제어 인프라
st.markdown("### 📅 작업 및 조회 기준일 선택")
selected_date = st.date_input("데이터를 입력하거나 조회할 날짜를 선택하세요", datetime.date.today())
date_key = str(selected_date)

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

# 5. 메인 기능 탭 구성
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
    st.write("달력 타임라인을 통해 누적 데이터를 실시간 모니터링하세요.")
    st.markdown(f"#### 🎯 {date_key} 건강 요약 통계")
    
    kpi_bmr, kpi_work, kpi_med = st.columns(3)
    kpi_bmr.metric("기초대사량 (BMR)", f"{int(bmr)} kcal")
    kpi_work.metric("운동 소모 칼로리", f"{current_data['workout_kcal']} kcal", delta=f"+{current_data['workout_kcal']}")
    kpi_med.metric("치료제 투약 상태", f"{current_data['med_name']} ({current_data['med_dose']})")
    
    st.markdown("---")
    st.subheader("📊 일자별 타임라인 성적표")
    
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
        with st.spinner("Gemini 3.1 Flash-Lite 분석 중..."):
            try:
                model = genai.GenerativeModel('models/gemini-3.1-flash-lite')
                prompt = f"프로필: BMR {int(bmr)}kcal, 목표 {goal}. 아침:{current_data['meals']['아침']}, 점심:{current_data['meals']['점심']}, 저녁:{current_data['meals']['저녁']}, 간식:{current_data['meals']['간식']}, 야식:{current_data['meals']['야식']}, 카페:{current_data['meals']['카페']}. 칼로리, 나트륨, 카페인, 탄단지를 추정 및 일일 권장량과 [좋음/보통/나쁨]으로 비교하고, 대사 칼로리 밸런스 평가와 한 줄 단문 보완점을 출력해줘."
                if food_img:
                    img = Image.open(food_img)
                    response = model.generate_content([prompt, img])
                else:
                    response = model.generate_content(prompt)
                    
                current_data["ai_analysis"] = response.text
                current_data["bad_feedback"] = "염분량 및 정제당 섭취 통제 권장"
                st.session_state.points += 100
                st.toast("종합 정산 완료! +100p 🐾")
                st.rerun()
            except Exception as e:
                st.error(f"오류: {e}")
                
    if current_data["ai_analysis"]:
        st.markdown(current_data["ai_analysis"])

# --- 탭 3: 정밀 운동 피드백 ---
with tab3:
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
                    workout_prompt = f"{final_workout}을 {workout_time}분 수행했을 때 예상 소모 칼로리와 운동 부상 방지 팁(러닝 시 무릎 보호, 테니스 엘보우 증상 방지 핸들링 등)을 상세히 작성해줘."
                    response = model.generate_content(workout_prompt)
                    st.markdown(response.text)
                    
                    current_data["workout_log"] = f"{final_workout} {workout_time}분"
                    current_data["workout_kcal"] = workout_time * 8
                    st.session_state.points += 100
                    st.toast("운동 기록 완료! +100p 🐾")
                except Exception as e:
                    st.error(f"오류: {e}")

# --- 탭 4: 비만 치료제 케어 ---
with tab4:
    st.header("💉 비만 치료제 케어")
    med_choice = st.selectbox("복용 중인 치료제 선택", ["선택 안 함", "위고비 (Wegovy)", "마운자로 (Mounjaro)"])
    dose_choice = st.select_slider("투약 용량 설정", options=["0mg", "0.25mg", "0.5mg", "1.0mg", "1.7mg", "2.4mg"])
    side_1 = st.checkbox("메스꺼움 / 구토")
    side_2 = st.checkbox("설사 / 변비")
    side_3 = st.checkbox("심한 복통")
    
    if st.button("복용 기록 완료"):
        current_data["med_name"] = med_choice
        current_data["med_dose"] = dose_choice
        if med_choice != "선택 안 함" and (side_1 or side_2 or side_3):
            current_data["bad_feedback"] = f"치료제 투약 이상 징후 (용량: {dose_choice})"
            st.error("⚠️ 부작용 신호 포착. 증상 지속 시 의사와 상담하세요.")
        else:
            st.success("✅ 안전한 복약 일지가 동기화되었습니다.")
        st.session_state.points += 100
        st.toast("복약 체크 완료! +100p 🐾")

# --- 탭 5: 🛍️ 펫샵 (Pet Shop) [고양이방 & 강아지방 다원화] ---
with tab5:
    st.header("🛍️ 피트펫 상점")
    st.write("기록으로 모은 포인트로 새로운 펫을 입양하거나 전용 스킨을 장착해 주세요!")
    
    # 상점 카테고리 분리
    shop_cat = st.radio("상점 카테고리 선택", ["🐱 고양이 룸 에셋", "🐶 강아지 룸 에셋"])
    
    if shop_cat == "🐱 고양이 룸 에셋":
        cat_items = {
            "기본 고양이": 0,
            "🕶️ 힙스터 선글라스 (고양이)": 100,
            "👑 명품 골드 왕관 (고양이)": 200,
            "🤖 하이닉스 유니폼 (고양이)": 300
        }
        items_to_display = cat_items
    else:
        dog_items = {
            "기본 강아지": 100,  # 기본 강아지 분양가 100p 세팅 완료!
            "🕶️ 힙스터 강아지": 150,
            "👑 왕관 강아지": 220,
            "🤖 하이닉스 강아지": 320
        }
        items_to_display = dog_items
        
    col1, col2, col3, col4 = st.columns(4)
    cols = [col1, col2, col3, col4]
    
    for idx, (item_name, price) in enumerate(items_to_display.items()):
        with cols[idx % 4]:
            st.markdown(f"**{item_name}**")
            st.write(f"💰 {price} p")
            
            # 인벤토리 소유 확인 시스템 시스템
            if item_name in st.session_state.inventory:
                if st.session_state.equipped == item_name:
                    st.button("🟢 장착 중", key=f"shop_eq_{item_name}", disabled=True)
                else:
                    if st.button("🔄 장착", key=f"shop_eq_{item_name}"):
                        st.session_state.equipped = item_name
                        st.rerun()
            else:
                if st.button("🛒 구매", key=f"shop_buy_{item_name}"):
                    if st.session_state.points >= price:
                        st.session_state.points -= price
                        st.session_state.inventory.append(item_name)
                        st.session_state.equipped = item_name
                        st.success(f"🎉 구매 완료!")
                        st.rerun()
                    else:
                        st.error("포인트 부족!")
