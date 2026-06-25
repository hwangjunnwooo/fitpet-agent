import streamlit as st
import google.generativeai as genai
from PIL import Image
import datetime

# 1. 페이지 기본 설정 및 디자인
st.set_page_config(page_title="피트펫 (FitPet) 3D", page_icon="🐾", layout="centered")

st.title("🐾 피트펫 (FitPet) 3D & 펫샵")
st.caption("올인원 헬스케어 에이전트 + 3D 펫 키우기 (SK하이닉스 신입사원 과제)")
st.markdown("---")

# 2. 세션 상태(데이터 저장용) 초기화
if "points" not in st.session_state:
    st.session_state.points = 100  # 테스트를 위해 기본 100p 지급
if "inventory" not in st.session_state:
    st.session_state.inventory = ["기본 스킨"]
if "equipped" not in st.session_state:
    st.session_state.equipped = "기본 스킨"
if "calendar_meals" not in st.session_state:
    # 캘린더 식단 예시 데이터 초기화
    st.session_state.calendar_meals = {
        str(datetime.date.today()): {"plan": "닭가슴살 샐러드 & 현미밥", "checked": False}
    }

# Gemini API 키 설정
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception as e:
    st.warning("API Key가 설정되지 않았습니다. Secrets 설정을 확인해 주세요.")

# 3. 사이드바 - 3D 고양이 캐릭터 및 상태창
st.sidebar.header("🐱 마이 3D 펫 룸")
st.sidebar.subheader(f"💰 보유 포인트: {st.session_state.points} p")

# CSS 3D 큐브/입체 효과를 활용한 3D 고양이 캐릭터 구현
# 장착한 아이템에 따라 고양이의 색상이나 장식이 바뀜
cat_color = "#FFB347"  # 기본 치즈냥이 색상
cat_accessory = ""

if st.session_state.equipped == "🤖 하이닉스 반도체 슈트":
    cat_color = "#00BFFF"
    cat_accessory = "⚡ HBM POWER"
elif st.session_state.equipped == "👑 명품 골드 왕관":
    cat_accessory = "👑 GOLD CROWN"
elif st.session_state.equipped == "🕶️ 힙스터 선글라스":
    cat_accessory = "🕶️ COOL CAT"

# 3D 애니메이션 고양이 HTML 렌더링
st.sidebar.markdown(f"""
<div style="perspective: 400px; width: 100%; text-align: center; padding: 20px 0;">
    <div style="width: 100px; height: 100px; background: {cat_color}; margin: 0 auto; transform: rotateX(20deg) rotateY(20deg); transform-style: preserve-3d; animation: spin 4s linear infinite; border-radius: 20px; position: relative; box-shadow: 5px 5px 15px rgba(0,0,0,0.2);">
        <div style="position: absolute; top: -15px; left: 10px; width: 0; height: 0; border-left: 15px solid transparent; border-right: 15px solid transparent; border-bottom: 20px solid {cat_color};"></div>
        <div style="position: absolute; top: -15px; right: 10px; width: 0; height: 0; border-left: 15px solid transparent; border-right: 15px solid transparent; border-bottom: 20px solid {cat_color};"></div>
        <div style="position: absolute; top: 35px; left: 20px; font-size: 16px;">👀</div>
        <div style="position: absolute; top: 55px; left: 42px; font-size: 12px;">👃</div>
        <div style="position: absolute; bottom: -30px; left: 0; width: 100%; text-align: center; color: #333; font-weight: bold; font-size: 12px;">
            {cat_accessory if cat_accessory else "🐱 알몸 상태"}
        </div>
    </div>
</div>
<style>
@keyframes spin {{
    0% {{ transform: rotateX(15deg) rotateY(-20deg); }}
    50% {{ transform: rotateX(25deg) rotateY(20deg); }}
    100% {{ transform: rotateX(15deg) rotateY(-20deg); }}
}}
</style>
""", unsafe_allow_html=True)

st.sidebar.markdown(f"**현재 장착:** {st.session_state.equipped}")

# 4. 메인 기능 탭 구성 (캘린더 및 펫샵 추가)
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📅 식단 캘린더 & 분석", 
    "🥦 실시간 식단 입력", 
    "⚡ 운동 관리 (Learning)", 
    "💉 비만 치료제 케어", 
    "🛍️ 펫샵 (Pet Shop)"
])

# --- 탭 1: 식단 캘린더 및 식단표 자동 반영 ---
with tab1:
    st.header("📅 스마트 식단 캘린더")
    st.write("기관 식단표 이미지나 주간 식단표 계획을 올리면 AI가 분석하여 해당 날짜 캘린더에 자동으로 입력해 줍니다.")
    
    # 식단표 자동 파싱 기능
    menu_file = st.file_uploader("📋 주간/월간 식단표 이미지 업로드", type=["jpg", "jpeg", "png"])
    if st.button("식단표 분석 후 캘린더 자동 등록"):
        if menu_file:
            with st.spinner("Gemini 3.1 Flash-Lite가 식단표 날짜별 메뉴를 추출 중입니다..."):
                try:
                    model = genai.GenerativeModel('models/gemini-3.1-flash-lite')
                    prompt = "제공된 식단표 이미지에서 날짜와 해당 날짜의 메인 메뉴를 매칭하여 'YYYY-MM-DD: 메뉴명' 형식으로만 요약해줘."
                    img = Image.open(menu_file)
                    response = model.generate_content([prompt, img])
                    
                    # 샘플 분석 결과를 캘린더 세션에 반영 (데모 구현)
                    today_str = str(datetime.date.today())
                    st.session_state.calendar_meals[today_str] = {"plan": "AI가 추출한 건강 균형 식단", "checked": False}
                    st.success("성공적으로 식단표를 분석하여 캘린더에 일정을 등록했습니다!")
                    st.code(response.text)
                except Exception as e:
                    st.error(f"오류 발생: {e}")
                    
    st.markdown("---")
    st.subheader("🗓️ 오늘의 식단 이행 여부 체크")
    
    selected_date = st.date_input("조회할 날짜를 선택하세요", datetime.date.today())
    date_key = str(selected_date)
    
    if date_key in st.session_state.calendar_meals:
        meal_info = st.session_state.calendar_meals[date_key]
        st.info(f"📋 **{date_key} 계획된 식단:** {meal_info['plan']}")
        
        # 실제 먹었는지 스위치로 체크
        is_eaten = st.checkbox("🍽️ 오늘 이 식단을 실제로 섭취하셨나요?", value=meal_info['checked'])
        st.session_state.calendar_meals[date_key]["checked"] = is_eaten
        
        if st.button("체크인 완료 및 보상 받기"):
            if is_eaten and not meal_info['checked']:
                st.session_state.points += 50
                st.toast("계획 식단 실천 완료! +50p 🐾")
                st.rerun()
            else:
                st.success("식단 실천 상태가 업데이트되었습니다.")
    else:
        st.warning("해당 날짜에 등록된 식단 계획이 없습니다. 아래 직접 등록해 보세요.")
        new_plan = st.text_input("새로운 식단 계획 입력")
        if st.button("식단 계획 추가"):
            st.session_state.calendar_meals[date_key] = {"plan": new_plan, "checked": False}
            st.rerun()

# --- 탭 2: 실시간 식단 입력 ---
with tab2:
    st.header("🥦 실시간 식단 비전 분석")
    food_img = st.file_uploader("식단 사진 업로드", type=["jpg", "jpeg", "png"], key="food_tab")
    food_text = st.text_input("식단 텍스트 입력", key="food_text_tab")
    
    if st.button("식단 분석 및 포인트 받기", key="food_btn"):
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
                    st.rerun()
                except Exception as e:
                    st.error(f"오류: {e}")

# --- 탭 3: 운동 관리 ---
with tab3:
    st.header("⚡ 웨어러블 연동 운동 학습")
    workout_input = st.text_area("오늘 어떤 운동을 주로 하셨나요?", placeholder="예: 오늘 런닝구간 5km 뛰었어.")
    if st.button("운동 일지 등록 (+100p)"):
        if workout_input:
            with st.spinner("운동 패턴 분석 중..."):
                try:
                    model = genai.GenerativeModel('models/gemini-3.1-flash-lite')
                    workout_prompt = f"사용자의 운동 기록: '{workout_input}'. 패턴을 기반으로 하이닉스 신입사원 트레이너 컨셉으로 피드백해줘."
                    response = model.generate_content(workout_prompt)
                    st.info(response.text)
                    st.session_state.points += 100
                    st.toast("운동 기록 완료! +100p 🐾")
                    st.rerun()
                except Exception as e:
                    st.error(f"오류: {e}")

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
            st.rerun()

# --- 탭 5: 🛍️ 펫샵 (Pet Shop) ---
with tab5:
    st.header("🛍️ 피트펫 상점")
    st.write("열심히 운동하고 식단 관리를 해서 모은 포인트로 3D 고양이의 아이템을 구매해 보세요!")
    
    # 상점 아이템 리스트 (아이템명, 가격)
    shop_items = {
        "🕶️ 힙스터 선글라스": 100,
        "👑 명품 골드 왕관": 200,
        "🤖 하이닉스 반도체 슈트": 300
    }
    
    col1, col2, col3 = st.columns(3)
    cols = [col1, col2, col3]
    
    for idx, (item_name, price) in enumerate(shop_items.items()):
        with cols[idx]:
            st.subheader(item_name)
            st.write(f"💰 가격: {price} p")
            
            if item_name in st.session_state.inventory:
                # 이미 보유한 경우 장착 기능 제공
                if st.session_state.equipped == item_name:
                    st.button("🟢 장착 중", key=f"eq_{idx}", disabled=True)
                else:
                    if st.button("🔄 장착하기", key=f"eq_{idx}"):
                        st.session_state.equipped = item_name
                        st.rerun()
            else:
                # 미보유 시 구매 기능 제공
                if st.button("🛒 구매하기", key=f"buy_{idx}"):
                    if st.session_state.points >= price:
                        st.session_state.points -= price
                        st.session_state.inventory.append(item_name)
                        st.session_state.equipped = item_name
                        st.success(f"🎉 {item_name} 구매 및 장착 완료!")
                        st.rerun()
                    else:
                        st.error("포인트가 부족합니다! 식단과 운동을 더 기록해 오세요.")
                        
    st.markdown("---")
    if st.button("기본 스킨으로 초기화"):
        st.session_state.equipped = "기본 스킨"
        st.rerun()
