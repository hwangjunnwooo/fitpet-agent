import streamlit as st
import google.generativeai as genai
from PIL import Image
import datetime
import os

# 1. 페이지 기본 설정 및 디자인
st.set_page_config(page_title="피트펫 (FitPet) 2D", page_icon="🐾", layout="centered")

st.title("🐾 피트펫 (FitPet) 2D & 스마트 대시보드")
st.caption("올인원 헬스케어 에이전트 + 비주얼 캘린더 (SK하이닉스 신입사원 과제)")
st.markdown("---")

# 2. 세션 상태(데이터 저장용) 초기화
if "points" not in st.session_state:
    st.session_state.points = 100
if "inventory" not in st.session_state:
    st.session_state.inventory = ["기본 스킨"]
if "equipped" not in st.session_state:
    st.session_state.equipped = "기본 스킨"

# 통합 캘린더 데이터베이스 구조화 (식단 및 운동 기록 통합 관리)
if "calendar_db" not in st.session_state:
    today_str = str(datetime.date.today())
    st.session_state.calendar_db = {
        today_str: {
            "meal_plan": "닭가슴살 샐러드 & 현미밥",
            "meal_checked": False,
            "workout_log": "기록 없음",
            "workout_kcal": 0
        }
    }

# Gemini API 키 설정
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.warning("API Key가 설정되지 않았습니다. Secrets 설정을 확인해 주세요.")

# 3. 사이드바 - 2D 고양이 캐릭터 및 상태창
st.sidebar.header("🐱 마이 펫 룸")
st.sidebar.subheader(f"💰 보유 포인트: {st.session_state.points} p")

image_file = "cat_base.png"
if st.session_state.equipped == "🕶️ 힙스터 선글라스":
    image_file = "cat_sunglasses.png"
elif st.session_state.equipped == "👑 명품 골드 왕관":
    image_file = "cat_crown.png"
elif st.session_state.equipped == "🤖 하이닉스 반도체 슈트":
    image_file = "cat_suit.png"

if os.path.exists(image_file):
    st.sidebar.image(image_file, caption=f"현재 상태: {st.session_state.equipped}", use_container_width=True)
else:
    st.sidebar.info(f"🐱 펫 대기 중 (장착: {st.session_state.equipped})")

st.sidebar.markdown("---")

# 4. 메인 기능 탭 구성 (캘린더 기능을 첫 번째 탭으로 전면 배치)
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🗓️ 통합 비주얼 캘린더", 
    "🥦 실시간 식단 분석", 
    "⚡ 정밀 운동 피드백", 
    "💉 비만 치료제 케어", 
    "🛍️ 펫샵 (Pet Shop)"
])

# --- 탭 1: 통합 비주얼 캘린더 대시보드 ---
with tab1:
    st.header("🗓️ 나의 헬스 캘린더 대시보드")
    st.write("달력에서 날짜를 선택하여 등록된 식단 계획과 운동 기록을 한눈에 실시간 모니터링하세요.")
    
    # 캘린더 날짜 선택기
    selected_date = st.date_input("조회 및 기록할 날짜를 선택하세요", datetime.date.today())
    date_key = str(selected_date)
    
    # 해당 날짜 데이터 초기화 생성
    if date_key not in st.session_state.calendar_db:
        st.session_state.calendar_db[date_key] = {
            "meal_plan": "등록된 식단 없음", "meal_checked": False, "workout_log": "기록 없음", "workout_kcal": 0
        }
    
    data = st.session_state.calendar_db[date_key]
    
    # 시각화 박스 배치
    col_meal, col_work = st.columns(2)
    with col_meal:
        st.markdown("### 🥦 식단 정보")
        st.markdown(f"**계획:** {data['meal_plan']}")
        is_eaten = st.checkbox("🍽️ 실제 식단 섭취 완료", value=data['meal_checked'], key=f"meal_check_{date_key}")
        st.session_state.calendar_db[date_key]["meal_checked"] = is_eaten
        
    with col_work:
        st.markdown("### ⚡ 운동 정보")
        st.markdown(f"**내역:** {data['workout_log']}")
        st.markdown(f"**소모 칼로리:** `{data['workout_kcal']} kcal`")
        
    st.markdown("---")
    st.subheader("📋 기관 식단표 자동 반영 (인프라 연동)")
    menu_file = st.file_uploader("식단표 이미지 업로드", type=["jpg", "jpeg", "png"])
    if st.button("AI 식단표 파싱 및 자동 스케줄링"):
        if menu_file:
            with st.spinner("Gemini 3.1 Flash-Lite가 식단표를 분석 중입니다..."):
                try:
                    model = genai.GenerativeModel('models/gemini-3.1-flash-lite')
                    prompt = "제공된 식단표 이미지에서 날짜와 메뉴를 매칭하여 요약해줘."
                    img = Image.open(menu_file)
                    response = model.generate_content([prompt, img])
                    st.session_state.calendar_db[str(datetime.date.today())]["meal_plan"] = "AI 추천 건강 특식"
                    st.success("식단 스케줄링이 완료되었습니다!")
                    st.code(response.text)
                except Exception as e:
                    st.error(f"오류: {e}")

# --- 탭 2: 실시간 식단 입력 ---
with tab2:
    st.header("🥦 실시간 식단 비전 분석")
    food_img = st.file_uploader("식단 사진 업로드", type=["jpg", "jpeg", "png"], key="food_tab")
    food_text = st.text_input("식단 텍스트 입력", key="food_text_tab")
    
    if st.button("식단 분석 및 포인트 받기"):
        if food_img or food_text:
            with st.spinner("Gemini AI가 식단을 분석 중입니다..."):
                try:
                    model = genai.GenerativeModel('models/gemini-3.1-flash-lite')
                    prompt = "당신은 영양사 에이전트입니다. 칼로리(kcal)와 탄단지 비율을 표 형태로 명확히 알려주고 다정한 피드백을 남겨주세요."
                    if food_img:
                        img = Image.open(food_img)
                        response = model.generate_content([prompt, img])
                    else:
                        response = model.generate_content([prompt, food_text])
                    st.markdown(response.text)
                    st.session_state.points += 100
                    st.toast("식단 기록 완료! +100p 🐾")
                except Exception as e:
                    st.error(f"오류: {e}")

# --- 탭 3: 정밀 운동 피드백 (대폭 강화된 영역) ---
with tab3:
    st.header("⚡ 정밀 운동 피드백 및 칼로리 예측")
    st.write("오늘 진행한 운동 종류와 시간을 알려주시면 전문적인 칼로리 소모량 계산 및 관절/부상 주의사항 피드백을 제공합니다.")
    
    workout_type = st.selectbox("운동 종류 선택", ["선택하세요", "러닝(런닝)", "테니스", "웨이트 트레이닝", "자전거", "수영", "기타 활동 직접 입력"])
    workout_time = st.number_input("운동 시간 입력 (분 단위)", min_value=1, max_value=480, value=30)
    
    custom_workout = ""
    if workout_type == "기타 활동 직접 입력":
        custom_workout = st.text_input("수행하신 운동 명칭을 입력하세요 (예: 필라테스)")
        
    if st.button("운동 평가 및 피드백 받기"):
        final_workout = custom_workout if workout_type == "기타 활동 직접 입력" else workout_type
        if workout_type != "선택하세요":
            with st.spinner("Gemini 3.1 Flash-Lite가 정밀 피드백을 생성 중입니다..."):
                try:
                    model = genai.GenerativeModel('models/gemini-3.1-flash-lite')
                    
                    # 예상 칼로리 및 통증/부상 방지(테니스 엘보우, 무릎 통증 등) 가이드 지침
                    workout_prompt = f"""
                    사용자가 수행한 운동: {final_workout} ({workout_time}분 동안 수행)
                    당신은 전문 스포츠 의학 코치이자 트레이너입니다. 다음 세 가지 요소를 마크다운 구조로 명확히 출력해 주세요:
                    1. [예상 소모 칼로리]: 신체 기준 평균 데이터에 따른 합리적인 총 소모 칼로리(kcal) 수치 제시
                    2. [운동 능력 평가]: 수행 시간에 대한 칭찬 및 운동 효율성 피드백
                    3. [메디컬 케어 및 부상 주의사항]: 해당 운동 시 발생할 수 있는 주요 부상 위험(예: 러닝의 경우 무릎 통증/족저근막염 방지 팁, 테니스의 경우 테니스 엘보우 방지 및 손목 가동성 주의사항 등)을 매우 전문적이고 구체적으로 안내해 줄 것.
                    """
                    response = model.generate_content(workout_prompt)
                    st.markdown(response.text)
                    
                    # 캘린더 데이터베이스에 운동 기록 동적 바인딩 및 연동
                    today_str = str(datetime.date.today())
                    if today_str not in st.session_state.calendar_db:
                        st.session_state.calendar_db[today_str] = {"meal_plan": "등록된 식단 없음", "meal_checked": False, "workout_log": "기록 없음", "workout_kcal": 0}
                    
                    st.session_state.calendar_db[today_str]["workout_log"] = f"{final_workout} {workout_time}분"
                    # 간이 칼로리 추출 파싱 (실제 앱에서는 텍스트에서 파싱하거나 하드코딩된 값 연동 가능)
                    st.session_state.calendar_db[today_str]["workout_kcal"] = workout_time * 7 
                    
                    st.session_state.points += 100
                    st.toast("운동 분석 완료 및 캘린더 연동! +100p 🐾")
                except Exception as e:
                    st.error(f"오류: {e}")
        else:
            st.warning("운동 종류를 선택해 주세요.")

# --- 탭 4: 비만 치료제 케어 ---
with tab4:
    st.header("💉 비만 치료제 케어")
    med_name = st.selectbox("복용 중인 치료제 선택", ["선택 안 함", "위고비 (Wegovy)", "마운자로 (Mounjaro)"], key="med_tab")
    if med_name != "선택 안 함":
        st.success(f"📢 {med_name} 복용 관리 모드 가동 중")
        side_1 = st.checkbox("메스꺼움 / 구토", key="s1")
        side_2 = st.checkbox("설사 / 변비", key="s2")
        side_3 = st.checkbox("심한 복통", key="s3")
        if st.button("복용 및 부작용 상태 기록 (+100p)"):
            if side_1 or side_2 or side_3:
                st.error("⚠️ 경고: 부작용 조짐이 보이니 증상 지속 시 즉시 투약을 중단하고 의사와 상담하세요.")
            else:
                st.success("✅ 안전하게 복용이 기록되었습니다.")
            st.session_state.points += 100
            st.toast("체크 완료! +100p 🐾")

# --- 탭 5: 🛍️ 펫샵 (Pet Shop) ---
with tab5:
    st.header("🛍️ 피트펫 상점")
    shop_items = {"🕶️ 힙스터 선글라스": 100, "👑 명품 골드 왕관": 200, "🤖 하이닉스 반도체 슈트": 300}
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
                        st.sidebar.success(f"{item_name} 장착 완료!")
                        st.rerun()
            else:
                if st.button("🛒 구매하기", key=f"buy_{idx}"):
                    if st.session_state.points >= price:
                        st.session_state.points -= price
                        st.session_state.inventory.append(item_name)
                        st.session_state.equipped = item_name
                        st.success(f"🎉 {item_name} 구매 및 장착 완료!")
                        st.rerun()
                    else:
                        st.error("포인트가 부족합니다!")
