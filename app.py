import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# 페이지 설정
st.set_page_config(
    page_title="DAU Funnel 시뮬레이터",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a3e 50%, #0d1b2a 100%);
        font-family: 'Noto Sans KR', sans-serif;
    }
    
    /* 메인 영역 글자 색상 밝게 */
    .stApp, .stApp p, .stApp span, .stApp label, .stApp div {
        color: #e0e0e0 !important;
    }
    
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5 {
        color: #ffffff !important;
    }
    
    /* 사이드바 글자 색상 */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a3e 0%, #0d1b2a 100%);
    }
    
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] div {
        color: #e0e0e0 !important;
    }
    
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4 {
        color: #ffffff !important;
    }
    
    /* 탭 글자 색상 */
    .stTabs [data-baseweb="tab"] {
        background: rgba(255,255,255,0.1);
        border-radius: 8px;
        color: #ffffff !important;
        padding: 10px 20px;
    }
    
    .stTabs [data-baseweb="tab"] p,
    .stTabs [data-baseweb="tab"] span {
        color: #ffffff !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(90deg, #00d4aa, #7b68ee);
    }
    
    .stTabs [aria-selected="true"] p,
    .stTabs [aria-selected="true"] span {
        color: #ffffff !important;
        font-weight: 600;
    }
    
    .main-header {
        background: linear-gradient(90deg, #00d4aa 0%, #7b68ee 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        padding: 1rem 0;
    }
    
    .metric-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 16px;
        padding: 1.5rem;
        backdrop-filter: blur(10px);
    }
    
    .node-title {
        color: #00d4aa !important;
        font-weight: 600;
        font-size: 1.1rem;
    }
    
    .stSlider > div > div > div {
        background: linear-gradient(90deg, #00d4aa, #7b68ee);
    }
    
    /* 슬라이더 레이블 */
    .stSlider label {
        color: #e0e0e0 !important;
    }
    
    div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
        color: #ffffff !important;
    }
    
    div[data-testid="stMetricLabel"] {
        color: #b0b0b0 !important;
    }
    
    /* Expander 헤더 */
    .streamlit-expanderHeader {
        color: #ffffff !important;
        font-weight: 500;
    }
    
    /* 입력 필드 */
    .stNumberInput label, .stTextInput label, .stSelectbox label {
        color: #e0e0e0 !important;
    }
    
    /* 버튼 */
    .stButton button {
        color: #ffffff !important;
    }
    
    /* 캡션 */
    .stCaption, small {
        color: #a0a0a0 !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
</style>
""", unsafe_allow_html=True)

# 헤더
st.markdown('<h1 class="main-header">⚽ DAU Funnel 시뮬레이터</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align:center; color:#888; margin-bottom:2rem;">경기 노드별 유저 흐름 & 리스크 관리 대시보드</p>', unsafe_allow_html=True)

# ==================== 사이드바: 입력 변수 ====================
with st.sidebar:
    st.markdown("### 🎛️ 시뮬레이션 설정")
    
    # 노드 목록 (먼저 정의)
    nodes_list = ["경기전", "전반전", "하프타임", "후반전", "경기직후"]
    
    # 세션 상태 초기화 - 외생변수 (통제 불가능한 외부 요인)
    if 'exo_factors' not in st.session_state:
        st.session_state.exo_factors = {
            "경기전": {
                "⚽ 경기 기대감": {"value": 0.8, "weight": 0.4},
                "📢 사전 알림 효과": {"value": 0.7, "weight": 0.3},
                "🌟 경기 중요도": {"value": 0.6, "weight": 0.3},
            },
            "전반전": {
                "⚽ 경기 재미": {"value": 0.9, "weight": 0.6},
                "🔥 경기 긴장감": {"value": 0.7, "weight": 0.4},
            },
            "하프타임": {
                "⚽ 전반 경기 평가": {"value": 0.6, "weight": 0.5},
                "🎯 후반 기대감": {"value": 0.7, "weight": 0.5},
            },
            "후반전": {
                "⚽ 경기 재미": {"value": 0.95, "weight": 0.5},
                "🔥 클라이맥스 효과": {"value": 0.9, "weight": 0.3},
                "🎯 승부 결정 긴장감": {"value": 0.85, "weight": 0.2},
            },
            "경기직후": {
                "🏆 경기 결과 만족도": {"value": 0.7, "weight": 0.6},
                "📊 경기 내용 평가": {"value": 0.8, "weight": 0.4},
            },
        }
    
    # 세션 상태 초기화 - 내재변수 (통제 가능한 앱 내 콘텐츠)
    if 'endo_factors' not in st.session_state:
        st.session_state.endo_factors = {
            "경기전": {
                "🔮 경기예측": {"value": 0.7, "weight": 0.25},
                "💬 게시글": {"value": 0.6, "weight": 0.2},
                "💎 GemShopping": {"value": 0.5, "weight": 0.15},
                "❤️ HeartShopping": {"value": 0.5, "weight": 0.15},
                "🏙️ CityConquest": {"value": 0.6, "weight": 0.15},
                "📱 앱 접근성": {"value": 0.9, "weight": 0.1},
            },
            "전반전": {
                "💬 실시간채팅": {"value": 0.8, "weight": 0.3},
                "🔮 경기예측": {"value": 0.7, "weight": 0.25},
                "💬 게시글": {"value": 0.6, "weight": 0.15},
                "📊 실시간 통계": {"value": 0.8, "weight": 0.15},
                "❤️ HeartShopping": {"value": 0.5, "weight": 0.15},
            },
            "하프타임": {
                "🏙️ CityConquest": {"value": 0.7, "weight": 0.25},
                "💬 게시글": {"value": 0.6, "weight": 0.2},
                "💬 실시간채팅": {"value": 0.7, "weight": 0.2},
                "💎 GemShopping": {"value": 0.6, "weight": 0.15},
                "❤️ HeartShopping": {"value": 0.5, "weight": 0.1},
                "🔮 경기예측": {"value": 0.8, "weight": 0.1},
            },
            "후반전": {
                "💬 실시간채팅": {"value": 0.85, "weight": 0.35},
                "🔮 경기예측": {"value": 0.75, "weight": 0.25},
                "📊 실시간 통계": {"value": 0.8, "weight": 0.2},
                "💬 게시글": {"value": 0.6, "weight": 0.1},
                "❤️ HeartShopping": {"value": 0.5, "weight": 0.1},
            },
            "경기직후": {
                "💬 게시글": {"value": 0.8, "weight": 0.25},
                "💬 실시간채팅": {"value": 0.7, "weight": 0.2},
                "🎁 보상 수령": {"value": 0.85, "weight": 0.2},
                "💎 GemShopping": {"value": 0.6, "weight": 0.15},
                "🏙️ CityConquest": {"value": 0.65, "weight": 0.1},
                "❤️ HeartShopping": {"value": 0.5, "weight": 0.1},
            },
        }
    
    # 외생/내재 가중치 비율
    if 'exo_endo_ratio' not in st.session_state:
        st.session_state.exo_endo_ratio = 0.4  # 외생 40%, 내재 60%
    
    # 🎮 노드별 성공률 계수 (가장 위)
    with st.expander("🎮 노드별 성공률 계수", expanded=True):
        st.caption("내재변수(콘텐츠)로 성공률 결정, 외생변수는 통제 불가(0점)")
        
        # 외생/내재 비율 설정
        st.markdown("**⚖️ 외생/내재 비율**")
        exo_ratio = st.slider(
            "외생변수 비율 (통제불가 영역)",
            0.0, 1.0,
            st.session_state.exo_endo_ratio,
            0.05,
            key="exo_ratio_slider",
            help="외생(경기 재미 등, 0점 처리) vs 내재(앱 콘텐츠)"
        )
        st.session_state.exo_endo_ratio = exo_ratio
        endo_ratio = 1.0 - exo_ratio
        
        st.warning(f"🌍 외생변수: **{exo_ratio:.0%}** (통제불가, 0점 처리)")
        st.success(f"🎮 내재변수: **{endo_ratio:.0%}** (콘텐츠로 관리)")
        
        st.markdown("---")
        
        # 노드 선택 탭
        node_tabs = st.tabs(nodes_list)
        
        success_rate = {}
        node_factor_details = {}  # 시각화용 저장
        
        for node_idx, (node_tab, node_name) in enumerate(zip(node_tabs, nodes_list)):
            with node_tab:
                # 외생변수는 0점으로 고정
                exo_score = 0.0
                
                # === 내재변수 섹션 ===
                st.markdown("**🎮 내재변수** (앱 콘텐츠)")
                endo_factors = st.session_state.endo_factors[node_name]
                
                # 새 내재변수 추가
                col_add1, col_add2 = st.columns([3, 1])
                with col_add1:
                    new_factor = st.text_input(
                        "새 콘텐츠", 
                        placeholder="예: 🎁 신규 콘텐츠",
                        key=f"new_endo_{node_name}",
                        label_visibility="collapsed"
                    )
                with col_add2:
                    if st.button("➕", key=f"add_endo_{node_name}", help="콘텐츠 추가"):
                        if new_factor and new_factor not in endo_factors:
                            st.session_state.endo_factors[node_name][new_factor] = {"value": 0.5, "weight": 0.1}
                            st.rerun()
                
                endo_weighted_sum = 0
                endo_total_weight = 0
                keys_to_delete = []
                
                for endo_idx, (endo_name, endo_data) in enumerate(endo_factors.items()):
                    name_col, del_col = st.columns([5, 1])
                    with name_col:
                        st.markdown(f"**{endo_name}**")
                    with del_col:
                        if st.button("🗑", key=f"del_endo_{node_name}_{endo_idx}"):
                            keys_to_delete.append(endo_name)
                    
                    val_col, wgt_col = st.columns(2)
                    with val_col:
                        new_value = st.slider(
                            "점수",
                            0.0, 1.0,
                            float(endo_data["value"]),
                            0.05,
                            key=f"endo_val_{node_name}_{endo_idx}",
                        )
                        st.session_state.endo_factors[node_name][endo_name]["value"] = new_value
                    
                    with wgt_col:
                        new_weight = st.slider(
                            "가중치",
                            0.0, 1.0,
                            float(endo_data["weight"]),
                            0.05,
                            key=f"endo_wgt_{node_name}_{endo_idx}",
                        )
                        st.session_state.endo_factors[node_name][endo_name]["weight"] = new_weight
                    
                    st.markdown("---")
                    
                    endo_weighted_sum += new_value * new_weight
                    endo_total_weight += new_weight
                
                # 삭제 처리
                for key in keys_to_delete:
                    del st.session_state.endo_factors[node_name][key]
                    st.rerun()
                
                endo_score = endo_weighted_sum / max(endo_total_weight, 0.01)
                st.info(f"내재 점수: **{endo_score:.0%}**")
                
                # === 최종 성공률 계산 ===
                final_score = (exo_score * exo_ratio) + (endo_score * endo_ratio)
                success_rate[node_name] = min(1.0, max(0.0, final_score))
                
                node_factor_details[node_name] = {
                    "exo_factors": dict(st.session_state.exo_factors[node_name]),
                    "endo_factors": dict(st.session_state.endo_factors[node_name]),
                    "exo_score": exo_score,
                    "endo_score": endo_score,
                    "calculated_rate": final_score
                }
                
                # 결과 표시
                max_achievable = endo_ratio  # 내재로 달성 가능한 최대치
                st.success(f"**최종 성공률: {success_rate[node_name]:.0%}** (내재 {endo_score:.0%} × {endo_ratio:.0%} = 최대 {max_achievable:.0%} 중 {success_rate[node_name]:.0%})")
    
    # 📥 신규 유저 입력
    with st.expander("📥 신규 유저 입력", expanded=False):
        total_new_users = st.number_input("🆕 총 신규 유저 수", min_value=0, value=2100, step=100)
        
        st.markdown("**노드별 신규 유저 비중**")
        new_user_weight = {
            "경기전": st.slider("경기전 비중", 0.0, 1.0, 0.48, 0.01, key="nw_pre"),
            "전반전": st.slider("전반전 비중", 0.0, 1.0, 0.24, 0.01, key="nw_1st"),
            "하프타임": st.slider("하프타임 비중", 0.0, 1.0, 0.10, 0.01, key="nw_half"),
            "후반전": st.slider("후반전 비중", 0.0, 1.0, 0.14, 0.01, key="nw_2nd"),
            "경기직후": st.slider("경기직후 비중", 0.0, 1.0, 0.05, 0.01, key="nw_post"),
        }
        
        # 비중 합계 표시
        total_weight = sum(new_user_weight.values())
        if abs(total_weight - 1.0) > 0.01:
            st.warning(f"⚠️ 비중 합계: {total_weight:.0%} (100%가 되어야 합니다)")
        else:
            st.success(f"✅ 비중 합계: {total_weight:.0%}")
        
        # 실제 신규 유저 수 계산
        new_users = {
            node: int(total_new_users * (weight / total_weight)) if total_weight > 0 else 0
            for node, weight in new_user_weight.items()
        }
        
        # 계산 결과 표시
        st.markdown("**📊 계산된 신규 유저 수**")
        for node, count in new_users.items():
            st.caption(f"{node}: {count:,}명")
    
    # 🔄 복귀 비중
    with st.expander("🔄 복귀 비중 (Re-Weight)", expanded=False):
        re_weight = {
            "경기전": st.slider("경기전 복귀비중", 0.0, 1.0, 0.20, 0.05),
            "전반전": st.slider("전반전 복귀비중", 0.0, 1.0, 0.50, 0.05),
            "하프타임": st.slider("하프타임 복귀비중", 0.0, 1.0, 0.10, 0.05),
            "후반전": st.slider("후반전 복귀비중", 0.0, 1.0, 0.15, 0.05),
            "경기직후": st.slider("경기직후 복귀비중", 0.0, 1.0, 0.05, 0.05),
        }
    
    # 🌟 부활 비중
    with st.expander("🌟 부활 비중 (Sur-Weight)", expanded=False):
        sur_weight = {
            "경기전": st.slider("경기전 부활비중", 0.0, 1.0, 0.10, 0.05),
            "전반전": st.slider("전반전 부활비중", 0.0, 1.0, 0.60, 0.05),
            "하프타임": st.slider("하프타임 부활비중", 0.0, 1.0, 0.10, 0.05),
            "후반전": st.slider("후반전 부활비중", 0.0, 1.0, 0.15, 0.05),
            "경기직후": st.slider("경기직후 부활비중", 0.0, 1.0, 0.05, 0.05),
        }
    
    # ⚠️ 리스크 관리 설정
    with st.expander("⚠️ 리스크 관리 설정", expanded=False):
        risk_conversion = {
            "at_risk_dau": st.slider("At Risk DAU 전환율", 0.0, 1.0, 0.60, 0.05),
            "at_risk_wau": st.slider("At Risk WAU 전환율", 0.0, 1.0, 0.30, 0.05),
            "dead_users": st.slider("Dead Users 전환율", 0.0, 1.0, 0.10, 0.05),
        }
    
    # 전역 변수용 (시각화 호환)
    global_multiplier = 1.0
    multiplier_values = {}
    content_fun = match_fun = ux_quality = push_effect = 1.0

# ==================== 계산 로직 ====================
nodes = ["경기전", "전반전", "하프타임", "후반전", "경기직후"]

# 초기 React Pool과 Sur Pool (순환 참조 해결을 위한 반복 계산)
react_pool = 0
sur_pool = 0

# 5번 반복하여 수렴시킴 (순환 참조 근사)
for iteration in range(10):
    results = []
    prev_success = 0  # 첫 노드는 이전 성공 = 0으로 시작 (또는 마지막 노드의 성공을 순환)
    
    for i, node in enumerate(nodes):
        if i == 0:
            # 경기전은 경기직후의 성공수를 이전유지로 받음 (순환)
            retained = prev_success if iteration == 0 else results_prev[-1]["성공수"]
        else:
            retained = results[i-1]["성공수"]
        
        new = new_users[node]
        react_qty = react_pool * re_weight[node]
        resur_qty = sur_pool * sur_weight[node]
        
        total = retained + new + react_qty + resur_qty
        curr = success_rate[node]
        churn = 1 - curr
        success = total * curr
        at_risk = total * churn
        
        results.append({
            "노드": node,
            "이전유지": retained,
            "신규": new,
            "복귀비중": re_weight[node],
            "복귀수": react_qty,
            "부활비중": sur_weight[node],
            "부활수": resur_qty,
            "총활성": total,
            "성공률": curr,
            "이탈률": churn,
            "성공수": success,
            "이탈수": at_risk,
        })
    
    results_prev = results
    
    # 리스크 관리 계산
    total_at_risk = sum(r["이탈수"] for r in results)
    
    # at risk DAU
    at_risk_dau_pool = total_at_risk
    at_risk_dau_success = at_risk_dau_pool * risk_conversion["at_risk_dau"]
    at_risk_dau_loss = at_risk_dau_pool * (1 - risk_conversion["at_risk_dau"])
    
    # at risk WAU
    at_risk_wau_pool = at_risk_dau_loss
    at_risk_wau_success = at_risk_wau_pool * risk_conversion["at_risk_wau"]
    at_risk_wau_loss = at_risk_wau_pool * (1 - risk_conversion["at_risk_wau"])
    
    # Dead Users
    dead_users_pool = at_risk_wau_loss
    dead_users_success = dead_users_pool * risk_conversion["dead_users"]
    dead_users_loss = dead_users_pool * (1 - risk_conversion["dead_users"])
    
    # Pool 업데이트
    react_pool = at_risk_dau_success + at_risk_wau_success
    sur_pool = dead_users_success

df = pd.DataFrame(results)

# ==================== 메인 대시보드 ====================
tab_forecast, tab1, tab2, tab3, tab4 = st.tabs(["📈 예상치 관리", "📊 노드별 현황", "🔄 Funnel Flow", "⚠️ 리스크 관리", "📋 상세 데이터"])

# ==================== TAB 1: 노드별 현황 ====================
with tab1:
    # 상단 KPI 카드
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="총 활성 유저",
            value=f"{df['총활성'].sum():,.0f}",
            delta=f"신규 {sum(new_users.values()):,}"
        )
    
    with col2:
        st.metric(
            label="전체 성공 유저",
            value=f"{df['성공수'].sum():,.0f}",
            delta=f"{(df['성공수'].sum() / df['총활성'].sum() * 100):.1f}%"
        )
    
    with col3:
        st.metric(
            label="전체 이탈 유저",
            value=f"{df['이탈수'].sum():,.0f}",
            delta=f"-{(df['이탈수'].sum() / df['총활성'].sum() * 100):.1f}%",
            delta_color="inverse"
        )
    
    with col4:
        st.metric(
            label="React Pool",
            value=f"{react_pool:,.0f}",
            delta=f"Sur Pool: {sur_pool:,.0f}"
        )
    
    # 노드별 성공률 현황
    st.markdown("---")
    st.markdown("### 🎮 노드별 성공률 현황")
    
    # 노드별 성공률 메트릭
    rate_cols = st.columns(5)
    for idx, node in enumerate(nodes):
        with rate_cols[idx]:
            rate = success_rate.get(node, 0.5)
            # 색상 결정
            if rate >= 0.8:
                delta_color = "normal"
                delta_text = "높음"
            elif rate >= 0.6:
                delta_color = "off"
                delta_text = "보통"
            else:
                delta_color = "inverse"
                delta_text = "낮음"
            st.metric(node, f"{rate:.0%}", delta_text, delta_color=delta_color)
    
    # 노드별 계수 상세 차트
    with st.expander("📊 노드별 콘텐츠 기여도 분석"):
        selected_node = st.selectbox("노드 선택", nodes, key="factor_analysis_node")
        
        if selected_node in node_factor_details:
            details = node_factor_details[selected_node]
            endo_factors = details.get("endo_factors", {})
            endo_score = details.get("endo_score", 0)
            
            exo_ratio_val = st.session_state.exo_endo_ratio
            endo_ratio_val = 1 - exo_ratio_val
            
            # 상단 정보
            col_info1, col_info2, col_info3 = st.columns(3)
            with col_info1:
                st.metric("🌍 외생 (통제불가)", f"{exo_ratio_val:.0%}", "0점 처리", delta_color="inverse")
            with col_info2:
                st.metric("🎮 내재 콘텐츠 점수", f"{endo_score:.0%}")
            with col_info3:
                final = endo_score * endo_ratio_val
                st.metric("📊 최종 성공률", f"{final:.0%}")
            
            st.markdown("---")
            
            # 내재변수 차트
            st.markdown("#### 🎮 콘텐츠별 기여도")
            endo_names = list(endo_factors.keys())
            endo_values = [f["value"] for f in endo_factors.values()]
            endo_weights = [f["weight"] for f in endo_factors.values()]
            endo_contributions = [v * w for v, w in zip(endo_values, endo_weights)]
            
            fig_endo = go.Figure()
            fig_endo.add_trace(go.Bar(
                name='점수',
                x=endo_names,
                y=endo_values,
                marker_color='#4ecdc4',
                text=[f'{v:.0%}' for v in endo_values],
                textposition='outside'
            ))
            fig_endo.add_trace(go.Bar(
                name='가중치',
                x=endo_names,
                y=endo_weights,
                marker_color='#ffe66d',
                text=[f'{w:.0%}' for w in endo_weights],
                textposition='outside'
            ))
            fig_endo.update_layout(
                title=f"{selected_node} 콘텐츠별 점수 & 가중치",
                barmode='group',
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=350,
                yaxis=dict(range=[0, 1.2])
            )
            st.plotly_chart(fig_endo, use_container_width=True)
            
            # 기여도 파이차트
            fig_pie = go.Figure(data=[go.Pie(
                labels=endo_names,
                values=endo_contributions,
                hole=0.4,
                textinfo='label+percent',
                marker_colors=['#4ecdc4', '#ff6b6b', '#ffe66d', '#a06cd5', '#45b7d1', '#96ceb4', '#ff8c42', '#c084fc']
            )])
            
            fig_pie.update_layout(
                title=f"{selected_node} 콘텐츠별 성공률 기여도",
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                height=350
            )
            
            st.plotly_chart(fig_pie, use_container_width=True)
    
    st.markdown("---")
    
    # 노드별 바 차트
    col1, col2 = st.columns(2)
    
    with col1:
        fig_composition = go.Figure()
        
        fig_composition.add_trace(go.Bar(
            name='이전유지',
            x=df['노드'],
            y=df['이전유지'],
            marker_color='#4ecdc4'
        ))
        fig_composition.add_trace(go.Bar(
            name='신규',
            x=df['노드'],
            y=df['신규'],
            marker_color='#ff6b6b'
        ))
        fig_composition.add_trace(go.Bar(
            name='복귀수',
            x=df['노드'],
            y=df['복귀수'],
            marker_color='#ffe66d'
        ))
        fig_composition.add_trace(go.Bar(
            name='부활수',
            x=df['노드'],
            y=df['부활수'],
            marker_color='#a06cd5'
        ))
        
        fig_composition.update_layout(
            title="노드별 유저 구성",
            barmode='stack',
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=400
        )
        
        st.plotly_chart(fig_composition, use_container_width=True)
    
    with col2:
        fig_success = go.Figure()
        
        fig_success.add_trace(go.Bar(
            name='성공수',
            x=df['노드'],
            y=df['성공수'],
            marker_color='#00d4aa'
        ))
        fig_success.add_trace(go.Bar(
            name='이탈수',
            x=df['노드'],
            y=df['이탈수'],
            marker_color='#ff4757'
        ))
        
        fig_success.update_layout(
            title="노드별 성공 vs 이탈",
            barmode='group',
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=400
        )
        
        st.plotly_chart(fig_success, use_container_width=True)
    
    # 성공률 게이지
    st.markdown("### 📈 노드별 성공률")
    cols = st.columns(5)
    
    for i, (col, node) in enumerate(zip(cols, nodes)):
        with col:
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=success_rate[node] * 100,
                title={'text': node, 'font': {'size': 14, 'color': 'white'}},
                number={'suffix': '%', 'font': {'color': 'white'}},
                gauge={
                    'axis': {'range': [0, 100], 'tickcolor': 'white'},
                    'bar': {'color': '#00d4aa'},
                    'bgcolor': 'rgba(255,255,255,0.1)',
                    'steps': [
                        {'range': [0, 50], 'color': 'rgba(255,71,87,0.3)'},
                        {'range': [50, 75], 'color': 'rgba(255,230,109,0.3)'},
                        {'range': [75, 100], 'color': 'rgba(0,212,170,0.3)'}
                    ],
                }
            ))
            fig_gauge.update_layout(
                height=200,
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=40, b=20)
            )
            st.plotly_chart(fig_gauge, use_container_width=True)

# ==================== TAB 2: Funnel Flow ====================
with tab2:
    st.markdown("### 🔄 유저 흐름 Sankey 다이어그램")
    
    # Sankey 데이터 준비
    labels = []
    sources = []
    targets = []
    values = []
    colors = []
    
    # 노드 라벨 생성 (인덱스 0-4)
    for node in nodes:
        labels.append(f"{node}\n(총: {df[df['노드']==node]['총활성'].values[0]:,.0f})")
    
    # 추가 노드들
    labels.append(f"At Risk DAU\n({at_risk_dau_pool:,.0f})")  # 5
    labels.append(f"At Risk WAU\n({at_risk_wau_pool:,.0f})")  # 6
    labels.append(f"Dead Users\n({dead_users_pool:,.0f})")     # 7
    labels.append(f"React Pool\n({react_pool:,.0f})")          # 8
    labels.append(f"Sur Pool\n({sur_pool:,.0f})")              # 9
    labels.append(f"다음 사이클\n({df[df['노드']==nodes[-1]]['성공수'].values[0]:,.0f})")  # 10
    labels.append(f"완전 이탈\n({dead_users_loss:,.0f})")       # 11
    
    # 인덱스 정의
    node_indices = {name: i for i, name in enumerate(nodes)}
    at_risk_dau_idx = 5
    at_risk_wau_idx = 6
    dead_users_idx = 7
    react_idx = 8
    sur_idx = 9
    next_cycle_idx = 10
    final_churn_idx = 11
    
    # 색상 정의 (시간대별 같은 색 계열)
    # 경기 노드: 청록색 계열
    node_colors_flow = [
        'rgba(78,205,196,0.6)',   # 경기전
        'rgba(69,183,209,0.6)',   # 전반전  
        'rgba(60,161,222,0.6)',   # 하프타임
        'rgba(51,139,235,0.6)',   # 후반전
        'rgba(42,117,248,0.6)',   # 경기직후
    ]
    
    # 1. 노드 간 성공 흐름 (경기전 → 전반전 → ... → 경기직후)
    for i in range(len(nodes) - 1):
        sources.append(node_indices[nodes[i]])
        targets.append(node_indices[nodes[i + 1]])
        values.append(df[df['노드']==nodes[i]]['성공수'].values[0])
        colors.append(node_colors_flow[i])
    
    # 2. 마지막 노드 성공 → 다음 사이클
    last_success = df[df['노드']==nodes[-1]]['성공수'].values[0]
    sources.append(node_indices[nodes[-1]])
    targets.append(next_cycle_idx)
    values.append(last_success)
    colors.append('rgba(0,212,170,0.7)')
    
    # 3. 각 노드에서 이탈 → At Risk DAU (같은 빨간색 계열)
    for i, node in enumerate(nodes):
        sources.append(node_indices[node])
        targets.append(at_risk_dau_idx)
        values.append(df[df['노드']==node]['이탈수'].values[0])
        colors.append('rgba(255,107,107,0.5)')
    
    # 4. At Risk DAU → React Pool (성공) - 노란색 계열
    sources.append(at_risk_dau_idx)
    targets.append(react_idx)
    values.append(at_risk_dau_success)
    colors.append('rgba(255,217,61,0.6)')
    
    # 5. At Risk DAU → At Risk WAU (손실) - 주황색 계열
    sources.append(at_risk_dau_idx)
    targets.append(at_risk_wau_idx)
    values.append(at_risk_dau_loss)
    colors.append('rgba(255,140,66,0.5)')
    
    # 6. At Risk WAU → React Pool (성공) - 노란색 계열
    sources.append(at_risk_wau_idx)
    targets.append(react_idx)
    values.append(at_risk_wau_success)
    colors.append('rgba(255,217,61,0.6)')
    
    # 7. At Risk WAU → Dead Users (손실) - 보라색 계열
    sources.append(at_risk_wau_idx)
    targets.append(dead_users_idx)
    values.append(at_risk_wau_loss)
    colors.append('rgba(160,108,213,0.5)')
    
    # 8. Dead Users → Sur Pool (성공) - 연보라색 계열
    sources.append(dead_users_idx)
    targets.append(sur_idx)
    values.append(dead_users_success)
    colors.append('rgba(192,132,252,0.6)')
    
    # 9. Dead Users → 완전 이탈 (손실) - 회색 계열
    sources.append(dead_users_idx)
    targets.append(final_churn_idx)
    values.append(dead_users_loss)
    colors.append('rgba(107,114,128,0.5)')
    
    # 노드 색상 (시간대별 청록색 그라데이션 + 기타)
    node_colors = [
        '#4ecdc4',  # 0: 경기전 (밝은 청록)
        '#45b7d1',  # 1: 전반전
        '#3ca1de',  # 2: 하프타임
        '#338beb',  # 3: 후반전
        '#2a75f8',  # 4: 경기직후 (진한 파랑)
        '#ff6b6b',  # 5: At Risk DAU (빨강)
        '#ff8c42',  # 6: At Risk WAU (주황)
        '#a06cd5',  # 7: Dead Users (보라)
        '#ffd93d',  # 8: React Pool (노랑)
        '#c084fc',  # 9: Sur Pool (연보라)
        '#22c55e',  # 10: 다음 사이클 (녹색)
        '#6b7280',  # 11: 완전 이탈 (회색)
    ]
    
    # 노드 위치 수동 지정 (x: 0~1 왼쪽→오른쪽, y: 0~1 아래→위)
    node_x = [
        0.01,  # 경기전
        0.15,  # 전반전
        0.30,  # 하프타임
        0.45,  # 후반전
        0.60,  # 경기직후
        0.65,  # At Risk DAU
        0.7,  # At Risk WAU
        0.8,  # Dead Users
        0.8,  # React Pool
        0.85,  # Sur Pool
        0.8,  # 다음 사이클
        1,  # 완전 이탈
    ]
    
    node_y = [
        0.3,   # 경기전 (중앙)
        0.5,   # 전반전
        0.6,   # 하프타임
        0.7,   # 후반전
        0.8,   # 경기직후
        0.1,  # At Risk DAU (위쪽)
        0.45,  # At Risk WAU
        0.45,  # Dead Users
        0.05,  # React Pool (맨 위)
        0.65,  # Sur Pool
        0.75,  # 다음 사이클 (아래쪽)
        0.5,  # 완전 이탈
    ]
    
    fig_sankey = go.Figure(data=[go.Sankey(
        arrangement='snap',
        node=dict(
            pad=30,
            thickness=20,
            line=dict(color="white", width=0.5),
            label=labels,
            color=node_colors,
            x=node_x,
            y=node_y
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=colors
        )
    )])
    
    fig_sankey.update_layout(
        title="유저 흐름 시각화 (전체 라이프사이클)",
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        height=700,
        font=dict(size=11, color='white')
    )
    
    st.plotly_chart(fig_sankey, use_container_width=True)
    
    # 흐름 설명
    with st.expander("📖 흐름 설명"):
        st.markdown("""
        **🔵 경기 흐름 (청록→파랑 그라데이션)**
        - 경기전 → 전반전 → 하프타임 → 후반전 → 경기직후
        - 시간순으로 색이 진해집니다
        
        **🟢 다음 사이클 (녹색)**
        - 경기직후 성공 유저 → 다음 경기 사이클로 이동
        
        **🔴 이탈 흐름 (빨강)**
        - 각 노드에서 이탈 → At Risk DAU
        
        **🟠 리스크 파이프라인 (주황)**
        - At Risk DAU 손실 → At Risk WAU
        - At Risk WAU 손실 → Dead Users
        
        **🟡 React Pool (노랑)**
        - DAU/WAU에서 성공적으로 복귀한 유저
        
        **🟣 Sur Pool (보라)**
        - Dead Users에서 부활한 유저
        
        **⚫ 완전 이탈 (회색)**
        - Dead Users 손실 → 시스템 영구 이탈
        """)
    
    # 추가: 노드별 유입 구성 파이차트
    st.markdown("### 📊 노드별 유입 구성")
    
    selected_node = st.selectbox("노드 선택", nodes)
    node_data = df[df['노드'] == selected_node].iloc[0]
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_pie = go.Figure(data=[go.Pie(
            labels=['이전유지', '신규', '복귀수', '부활수'],
            values=[node_data['이전유지'], node_data['신규'], node_data['복귀수'], node_data['부활수']],
            hole=0.4,
            marker_colors=['#4ecdc4', '#ff6b6b', '#ffe66d', '#a06cd5']
        )])
        
        fig_pie.update_layout(
            title=f"{selected_node} 유입 구성",
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            height=350
        )
        
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        fig_pie2 = go.Figure(data=[go.Pie(
            labels=['성공', '이탈'],
            values=[node_data['성공수'], node_data['이탈수']],
            hole=0.4,
            marker_colors=['#00d4aa', '#ff4757']
        )])
        
        fig_pie2.update_layout(
            title=f"{selected_node} 성공 vs 이탈",
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            height=350
        )
        
        st.plotly_chart(fig_pie2, use_container_width=True)

# ==================== TAB 3: 리스크 관리 ====================
with tab3:
    st.markdown("### ⚠️ 리스크 관리 파이프라인")
    
    # 리스크 단계별 데이터
    risk_data = pd.DataFrame([
        {
            "단계": "At Risk DAU",
            "인원": at_risk_dau_pool,
            "전환율": risk_conversion["at_risk_dau"],
            "성공수": at_risk_dau_success,
            "손실율": 1 - risk_conversion["at_risk_dau"],
            "손실수": at_risk_dau_loss
        },
        {
            "단계": "At Risk WAU",
            "인원": at_risk_wau_pool,
            "전환율": risk_conversion["at_risk_wau"],
            "성공수": at_risk_wau_success,
            "손실율": 1 - risk_conversion["at_risk_wau"],
            "손실수": at_risk_wau_loss
        },
        {
            "단계": "Dead Users",
            "인원": dead_users_pool,
            "전환율": risk_conversion["dead_users"],
            "성공수": dead_users_success,
            "손실율": 1 - risk_conversion["dead_users"],
            "손실수": dead_users_loss
        }
    ])
    
    # 리스크 KPI
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "총 이탈 유저 (At Risk DAU)",
            f"{at_risk_dau_pool:,.0f}",
            f"전환율: {risk_conversion['at_risk_dau']*100:.0f}%"
        )
    
    with col2:
        st.metric(
            "React Pool (복귀 가능)",
            f"{react_pool:,.0f}",
            f"DAU+WAU 성공"
        )
    
    with col3:
        st.metric(
            "Sur Pool (부활 가능)",
            f"{sur_pool:,.0f}",
            f"Dead Users 성공"
        )
    
    st.markdown("---")
    
    # 리스크 워터폴 차트
    fig_waterfall = go.Figure(go.Waterfall(
        name="리스크 파이프라인",
        orientation="v",
        measure=["absolute", "relative", "relative", "relative", "relative", "total"],
        x=["총 이탈", "DAU 전환", "DAU 손실→WAU", "WAU 전환", "WAU 손실→Dead", "최종 손실"],
        y=[at_risk_dau_pool, -at_risk_dau_success, 0, -at_risk_wau_success, 0, None],
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        decreasing={"marker": {"color": "#00d4aa"}},
        increasing={"marker": {"color": "#ff4757"}},
        totals={"marker": {"color": "#ffa502"}}
    ))
    
    fig_waterfall.update_layout(
        title="리스크 파이프라인 워터폴",
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=400
    )
    
    st.plotly_chart(fig_waterfall, use_container_width=True)
    
    # 리스크 단계별 상세
    col1, col2 = st.columns(2)
    
    with col1:
        fig_funnel = go.Figure(go.Funnel(
            y=["총 이탈 (At Risk)", "At Risk DAU 전환", "At Risk WAU 전환", "Dead Users 전환"],
            x=[at_risk_dau_pool, at_risk_dau_success, at_risk_wau_success, dead_users_success],
            textinfo="value+percent initial",
            marker={"color": ["#ff4757", "#ffa502", "#ffe66d", "#a06cd5"]}
        ))
        
        fig_funnel.update_layout(
            title="리스크 전환 퍼널",
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            height=400
        )
        
        st.plotly_chart(fig_funnel, use_container_width=True)
    
    with col2:
        st.markdown("#### 📊 리스크 상세 데이터")
        
        st.dataframe(
            risk_data.style.format({
                "인원": "{:,.0f}",
                "전환율": "{:.0%}",
                "성공수": "{:,.0f}",
                "손실율": "{:.0%}",
                "손실수": "{:,.0f}"
            }),
            use_container_width=True,
            height=200
        )
        
        st.markdown("---")
        st.markdown("#### 🔄 Pool 요약")
        st.info(f"""
        **React Pool** = At Risk DAU 성공 ({at_risk_dau_success:,.0f}) + At Risk WAU 성공 ({at_risk_wau_success:,.0f}) = **{react_pool:,.0f}**
        
        **Sur Pool** = Dead Users 성공 = **{sur_pool:,.0f}**
        """)

# ==================== TAB 4: 상세 데이터 ====================
with tab4:
    st.markdown("### 📋 노드별 상세 데이터")
    
    # 데이터프레임 스타일링 (matplotlib 없이)
    styled_df = df.style.format({
        "이전유지": "{:,.0f}",
        "신규": "{:,.0f}",
        "복귀비중": "{:.0%}",
        "복귀수": "{:,.1f}",
        "부활비중": "{:.0%}",
        "부활수": "{:,.1f}",
        "총활성": "{:,.0f}",
        "성공률": "{:.0%}",
        "이탈률": "{:.0%}",
        "성공수": "{:,.0f}",
        "이탈수": "{:,.0f}"
    })
    
    st.dataframe(styled_df, use_container_width=True, height=250)
    
    st.markdown("---")
    
    # 수식 참조 설명
    with st.expander("📖 수식 로직 설명"):
        st.markdown("""
        #### 노드 계산
        - **이전유지 (Retained)** = 이전 노드의 성공수 (경기전은 경기직후의 성공수)
        - **복귀수 (React Qty)** = React Pool × 복귀비중
        - **부활수 (Resur Qty)** = Sur Pool × 부활비중
        - **총활성 (Total)** = 이전유지 + 신규 + 복귀수 + 부활수
        - **성공수 (Success)** = 총활성 × 성공률
        - **이탈수 (At Risk)** = 총활성 × 이탈률
        
        #### 리스크 관리
        - **At Risk DAU** = 모든 노드의 이탈수 합계 → 전환율 적용 → 성공/손실 분리
        - **At Risk WAU** = At Risk DAU 손실분 → 전환율 적용 → 성공/손실 분리
        - **Dead Users** = At Risk WAU 손실분 → 전환율 적용 → 성공/손실 분리
        
        #### Pool 계산
        - **React Pool** = At Risk DAU 성공 + At Risk WAU 성공
        - **Sur Pool** = Dead Users 성공
        """)
    
    # 데이터 다운로드
    st.markdown("---")
    st.markdown("### 📥 데이터 다운로드")
    
    col1, col2 = st.columns(2)
    
    with col1:
        csv = df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📊 노드 데이터 CSV 다운로드",
            data=csv,
            file_name="dau_funnel_nodes.csv",
            mime="text/csv"
        )
    
    with col2:
        risk_csv = risk_data.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="⚠️ 리스크 데이터 CSV 다운로드",
            data=risk_csv,
            file_name="dau_funnel_risk.csv",
            mime="text/csv"
        )

# ==================== TAB 5: 예상치 관리 ====================
with tab_forecast:
    st.markdown("### 📈 시간별 총 유저 수 예측")
    st.caption("경기 사이클을 반복하며 유저 수가 어떻게 변화하는지 시뮬레이션합니다")
    
    # 시뮬레이션 설정
    col_sim1, col_sim2, col_sim3 = st.columns(3)
    
    with col_sim1:
        num_cycles = st.slider("시뮬레이션 사이클 수", 1, 50, 20, help="경기 반복 횟수")
    
    with col_sim2:
        initial_users = st.number_input("초기 유저 수", min_value=0, value=5000, step=500)
    
    with col_sim3:
        st.caption(f"(설정된 총 신규: {total_new_users:,})")
        cycle_new_users = st.number_input("사이클당 신규 유저", min_value=0, value=total_new_users, step=100)
    
    st.markdown("---")
    
    # 현재 설정된 성공률 표시
    st.markdown("**📊 현재 노드별 성공률**")
    rate_cols = st.columns(5)
    for i, node in enumerate(nodes):
        with rate_cols[i]:
            rate = success_rate.get(node, 0.5)
            st.metric(node[:3], f"{rate:.0%}")
    
    # 누적 성공률 계산 (5개 노드를 연속 통과)
    cumulative_rate = 1.0
    for node in nodes:
        cumulative_rate *= success_rate.get(node, 0.5)
    st.info(f"🔄 **누적 성공률 (5노드 연속)**: {cumulative_rate:.1%} — 경기전부터 경기직후까지 살아남는 비율")
    
    st.markdown("---")
    
    # 시뮬레이션 실행
    simulation_data = []
    
    # 초기값
    current_active = initial_users
    current_react_pool = 0
    current_sur_pool = 0
    
    for cycle in range(num_cycles):
        cycle_data = {"사이클": cycle + 1}
        
        # 각 노드를 순회하며 계산
        node_active = current_active
        cycle_total_at_risk = 0
        
        for node_idx, node in enumerate(nodes):
            # 신규 유저 배분 (비중에 따라)
            total_weight_sim = sum(new_user_weight.values())
            node_new = cycle_new_users * (new_user_weight.get(node, 0) / max(total_weight_sim, 0.01))
            
            # 복귀 및 부활
            node_react = current_react_pool * re_weight.get(node, 0)
            node_resur = current_sur_pool * sur_weight.get(node, 0)
            
            # 총 활성
            node_total = node_active + node_new + node_react + node_resur
            
            # 성공/이탈
            node_success_rate = success_rate.get(node, 0.8)
            node_success = node_total * node_success_rate
            node_at_risk = node_total * (1 - node_success_rate)
            
            # 다음 노드로 전달
            node_active = node_success
            cycle_total_at_risk += node_at_risk
        
        # 리스크 파이프라인
        dau_pool = cycle_total_at_risk
        dau_success = dau_pool * risk_conversion["at_risk_dau"]
        dau_loss = dau_pool * (1 - risk_conversion["at_risk_dau"])
        
        wau_pool = dau_loss
        wau_success = wau_pool * risk_conversion["at_risk_wau"]
        wau_loss = wau_pool * (1 - risk_conversion["at_risk_wau"])
        
        dead_pool = wau_loss
        dead_success = dead_pool * risk_conversion["dead_users"]
        dead_loss = dead_pool * (1 - risk_conversion["dead_users"])
        
        # Pool 업데이트
        current_react_pool = dau_success + wau_success
        current_sur_pool = dead_success
        
        # 다음 사이클 시작 유저 = 마지막 노드 성공 유저
        current_active = node_active
        
        # 총 활성 유저 (모든 pool 합산)
        total_ecosystem = current_active + current_react_pool + current_sur_pool
        
        cycle_data["활성 유저"] = current_active
        cycle_data["React Pool"] = current_react_pool
        cycle_data["Sur Pool"] = current_sur_pool
        cycle_data["총 유저"] = total_ecosystem
        cycle_data["이탈 (Dead)"] = dead_loss
        
        simulation_data.append(cycle_data)
    
    sim_df = pd.DataFrame(simulation_data)
    
    # 메인 그래프: 시간별 총 유저 수
    fig_forecast = go.Figure()
    
    fig_forecast.add_trace(go.Scatter(
        x=sim_df["사이클"],
        y=sim_df["총 유저"],
        mode='lines+markers',
        name='총 유저 수',
        line=dict(color='#00d4aa', width=3),
        marker=dict(size=8),
        fill='tozeroy',
        fillcolor='rgba(0,212,170,0.2)'
    ))
    
    fig_forecast.add_trace(go.Scatter(
        x=sim_df["사이클"],
        y=sim_df["활성 유저"],
        mode='lines+markers',
        name='활성 유저',
        line=dict(color='#4ecdc4', width=2, dash='dot'),
        marker=dict(size=6)
    ))
    
    fig_forecast.update_layout(
        title="🔮 시간(사이클)별 예상 총 유저 수",
        xaxis_title="경기 사이클",
        yaxis_title="유저 수",
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=450,
        hovermode='x unified',
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )
    
    st.plotly_chart(fig_forecast, use_container_width=True)
    
    # KPI 요약
    st.markdown("---")
    st.markdown("### 📊 시뮬레이션 결과 요약")
    
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    
    final_total = sim_df["총 유저"].iloc[-1]
    initial_total = sim_df["총 유저"].iloc[0] if len(sim_df) > 0 else initial_users
    growth_rate = ((final_total - initial_total) / max(initial_total, 1)) * 100
    
    with kpi_col1:
        st.metric(
            "최종 총 유저",
            f"{final_total:,.0f}",
            f"{growth_rate:+.1f}% 성장"
        )
    
    with kpi_col2:
        st.metric(
            "최종 활성 유저",
            f"{sim_df['활성 유저'].iloc[-1]:,.0f}"
        )
    
    with kpi_col3:
        st.metric(
            "평균 React Pool",
            f"{sim_df['React Pool'].mean():,.0f}"
        )
    
    with kpi_col4:
        st.metric(
            "누적 이탈",
            f"{sim_df['이탈 (Dead)'].sum():,.0f}"
        )
    
    # 상세 분석 그래프
    with st.expander("📊 상세 분석 차트"):
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            # Pool 변화 추이
            fig_pools = go.Figure()
            
            fig_pools.add_trace(go.Scatter(
                x=sim_df["사이클"],
                y=sim_df["React Pool"],
                mode='lines',
                name='React Pool',
                line=dict(color='#ffe66d', width=2),
                stackgroup='one'
            ))
            
            fig_pools.add_trace(go.Scatter(
                x=sim_df["사이클"],
                y=sim_df["Sur Pool"],
                mode='lines',
                name='Sur Pool',
                line=dict(color='#a06cd5', width=2),
                stackgroup='one'
            ))
            
            fig_pools.update_layout(
                title="Pool 변화 추이",
                xaxis_title="사이클",
                yaxis_title="유저 수",
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=300
            )
            
            st.plotly_chart(fig_pools, use_container_width=True)
        
        with col_chart2:
            # 사이클별 이탈
            fig_churn = go.Figure()
            
            fig_churn.add_trace(go.Bar(
                x=sim_df["사이클"],
                y=sim_df["이탈 (Dead)"],
                name='이탈 유저',
                marker_color='#ff4757'
            ))
            
            fig_churn.update_layout(
                title="사이클별 최종 이탈 유저",
                xaxis_title="사이클",
                yaxis_title="이탈 수",
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=300
            )
            
            st.plotly_chart(fig_churn, use_container_width=True)
    
    # 시뮬레이션 데이터 테이블
    with st.expander("📋 시뮬레이션 상세 데이터"):
        st.dataframe(
            sim_df.style.format({
                "활성 유저": "{:,.0f}",
                "React Pool": "{:,.0f}",
                "Sur Pool": "{:,.0f}",
                "총 유저": "{:,.0f}",
                "이탈 (Dead)": "{:,.0f}"
            }),
            use_container_width=True,
            height=400
        )
        
        # CSV 다운로드
        sim_csv = sim_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 시뮬레이션 데이터 다운로드",
            data=sim_csv,
            file_name="user_forecast_simulation.csv",
            mime="text/csv"
        )

# Footer
st.markdown("---")
st.markdown(
    '<p style="text-align:center; color:#666;">Made with ❤️ using Streamlit | DAU Funnel Simulator v1.0</p>',
    unsafe_allow_html=True
)

