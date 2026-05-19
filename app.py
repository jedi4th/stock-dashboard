import streamlit as st
import yfinance as yf
import feedparser
import pandas as pd
from datetime import datetime
import time

# ─────────────────────────────────────────────
# 페이지 기본 설정
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="📈 주식 대시보드",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)
# ─────────────────────────────────────────────
# 커스텀 CSS (모바일 최적화 포함)
# ─────────────────────────────────────────────
st.markdown("""
<style>
    /* 전체 배경 */
    .stApp { background-color: #0f1117; }
    /* 사이드바 */
    section[data-testid="stSidebar"] {
        background-color: #1a1d27;
        border-right: 1px solid #2d3147;
    }
    /* 카드 스타일 */
    .stock-card {
        background: linear-gradient(135deg, #1e2235 0%, #252a3d 100%);
        border: 1px solid #2d3147;
        border-radius: 16px;
        padding: 20px 24px;
        margin-bottom: 15px; /* 모바일에서 간격 더 넓게 */
        box-shadow: 0 4px 24px rgba(0,0,0,0.4);
        transition: all 0.2s ease-in-out;
    }
    .stock-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 30px rgba(0,0,0,0.5);
    }
    /* 종목 헤더 */
    .ticker-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: #e2e8f0;
        letter-spacing: 0.05em;
        margin-bottom: 4px;
    }
    .company-name {
        font-size: 0.9rem;
        color: #7c85a3;
        margin-bottom: 16px;
    }
    /* 메트릭 커스텀 */
    .metric-container {
        background: #0f1117;
        border-radius: 12px;
        padding: 14px 16px;
        border: 1px solid #2d3147;
        text-align: center;
        margin-bottom: 8px; /* 메트릭 간 간격 */
    }
    .metric-label {
        font-size: 0.72rem;
        color: #7c85a3;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 1.15rem;
        font-weight: 700;
        color: #e2e8f0;
    }
    .metric-delta-pos { color: #34d399; font-size: 0.8rem; }
    .metric-delta-neg { color: #f87171; font-size: 0.8rem; }
    .metric-delta-neu { color: #94a3b8; font-size: 0.8rem; }
    /* 뉴스 섹션 */
    .news-title {
        font-size: 0.85rem;
        font-weight: 600;
        color: #a5b4fc;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin: 18px 0 10px 0;
        border-left: 3px solid #6366f1;
        padding-left: 10px;
    }
    .news-item {
        background: #0f1117;
        border-radius: 10px;
        padding: 12px 16px;
        margin-bottom: 8px;
        border: 1px solid #2d3147;
        transition: border-color 0.2s;
    }
    .news-item:hover { border-color: #6366f1; }
    .news-item a {
        color: #c7d2fe;
        text-decoration: none;
        font-size: 0.88rem;
        line-height: 1.5;
    }
    .news-item a:hover { color: #a5b4fc; }
    .news-source {
        font-size: 0.72rem;
        color: #7c85a3;
        margin-top: 4px;
    }
    /* 업데이트 시각 */
    .update-time {
        font-size: 0.75rem;
        color: #4a5378;
        text-align: right;
        margin-top: 8px;
    }
    /* 구분선 */
    hr { border-color: #2d3147; margin: 24px 0; }
    /* 버튼 */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: 600;
        width: 100%;
        padding: 10px;
        font-size: 0.95rem;
        transition: opacity 0.2s;
    }
    .stButton > button:hover { opacity: 0.85; }
    /* 에러 박스 */
    .error-box {
        background: #2d1a1a;
        border: 1px solid #7f1d1d;
        border-radius: 10px;
        padding: 14px;
        color: #fca5a5;
        font-size: 0.85rem;
        margin-bottom: 10px;
    }

    /* 모바일 화면 최적화 (Max-width 768px 이하) */
    @media (max-width: 768px) {
        .stApp { padding-top: 1rem; padding-bottom: 1rem; }
        section[data-testid="stSidebar"] {
            width: 100% !important; /* 사이드바 전체 너비 */
            margin-right: 0 !important;
            padding: 1.5rem;
            border-right: none;
            border-bottom: 1px solid #2d3147;
            position: sticky; /* 스크롤 시 상단 고정 */
            top: 0;
            z-index: 100;
        }
        .stock-card {
            padding: 15px 18px;
            margin-bottom: 10px;
        }
        .ticker-header {
            font-size: 1.3rem;
        }
        .company-name {
            font-size: 0.8rem;
        }
        div[data-testid="stVerticalBlock"] div[data-testid="stHorizontalBlock"] {
            flex-direction: column; /* 컬럼을 세로로 정렬 */
        }
        .metric-container {
            padding: 10px 12px;
            margin-bottom: 6px;
        }
        .metric-label {
            font-size: 0.65rem;
        }
        .metric-value {
            font-size: 1rem;
        }
        .metric-delta-pos, .metric-delta-neg, .metric-delta-neu {
            font-size: 0.7rem;
        }
        .news-title {
            font-size: 0.8rem;
            margin: 15px 0 8px 0;
            padding-left: 8px;
        }
        .news-item a {
            font-size: 0.8rem;
        }
        .news-source {
            font-size: 0.68rem;
        }
        .update-time {
            font-size: 0.7rem;
        }
        .stButton > button {
            padding: 8px;
            font-size: 0.9rem;
        }
        /* Streamlit multiselect 텍스트 크기 조정 */
        .stMultiSelect div[data-testid="stSelectbox"] div[data-testid="stOptionSelectbox"] {
             font-size: 0.9rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 한글 회사명 ↔ 티커 심볼 매핑 딕셔너리 (코스피 200 주요 종목 포함, 약 100개)
# ─────────────────────────────────────────────
# 실제 코스피 200 종목은 계속 변동되므로, 주기적인 업데이트가 필요합니다.
# 여기에 원하는 회사 이름과 티커 심볼을 추가/수정/삭제하세요.
# 대소문자 구분을 없애기 위해 키는 모두 대문자로 저장합니다.
KOREAN_TICKER_MAP = {
    # 한국 코스피 200 주요 종목 (약 100개)
    "삼성전자": "005930.KS",
    "SK 하이닉스": "000660.KS",
    "LG 에너지솔루션": "373220.KS",
    "삼성바이오로직스": "207940.KS",
    "현대자동차": "005380.KS",
    "기아": "000270.KS",
    "NAVER": "035420.KS",
    "카카오": "035720.KS",
    "LG화학": "051910.KS",
    "삼성SDI": "006400.KS",
    "POSCO 홀딩스": "005490.KS",
    "현대모비스": "012330.KS",
    "셀트리온": "068270.KS",
    "KB 금융": "105560.KS",
    "신한지주": "055550.KS",
    "하나금융지주": "086790.KS",
    "LG전자": "066570.KS",
    "삼성물산": "028260.KS",
    "KT&G": "033780.KS",
    "삼성생명": "032830.KS",
    "엔씨소프트": "036570.KS",
    "SK 이노베이션": "096770.KS",
    "아모레퍼시픽": "090430.KS",
    "대한항공": "003490.KS",
    "HMM": "011200.KS",
    "두산에너빌리티": "034020.KS",
    "고려아연": "010130.KS",
    "하이브": "352820.KS",
    "크래프톤": "259960.KS",
    "CJ ENM": "035760.KS",
    "SK": "034730.KS",
    "롯데케미칼": "011170.KS",
    "SK텔레콤": "017670.KS",
    "LG생활건강": "051900.KS",
    "한국전력": "015760.KS",
    "우리금융지주": "316140.KS",
    "삼성화재": "000810.KS",
    "카카오뱅크": "323410.KS",
    "카카오페이": "377300.KS",
    "SK바이오팜": "326030.KS",
    "넷마블": "251270.KS",
    "아모레G": "002790.KS",
    "HD현대중공업": "329180.KS",
    "한국항공우주": "047810.KS",
    "금양": "001570.KS",
    "한화솔루션": "009830.KS",
    "현대건설": "000720.KS",
    "GS건설": "006360.KS",
    "DB하이텍": "000990.KS",
    "한국가스공사": "036460.KS",
    "삼성증권": "016360.KS",
    "미래에셋증권": "006800.KS",
    "메리츠금융지주": "138040.KS",
    "HDC현대산업개발": "294870.KS",
    "강원랜드": "035250.KS",
    "DL이앤씨": "375500.KS",
    "코웨이": "021240.KS",
    "현대글로비스": "086280.KS",
    "LS ELECTRIC": "010120.KS",
    "S-Oil": "010950.KS",
    "롯데쇼핑": "023530.KS",
    "CJ제일제당": "097950.KS",
    "대상": "001700.KS",
    "오리온": "271560.KS",
    "LG유플러스": "032640.KS",
    "KT": "030200.KS",
    "GS": "078930.KS",
    "SKC": "011790.KS",
    "아시아나항공": "020560.KS",
    "이마트": "139480.KS",
    "BGF리테일": "282330.KS",
    "F&F": "383220.KS",
    "제일기획": "030000.KS",
    "삼성전기": "009150.KS",
    "LG이노텍": "011070.KS",
    "HLB": "028300.KS",
    "한미약품": "128940.KS",
    "종근당": "185750.KS",
    "유한양행": "000100.KS",
    "녹십자": "006280.KS",
    "한화생명": "088350.KS",
    "삼성엔지니어링": "028050.KS",
    "현대제철": "004020.KS",
    "동국제강": "001230.KS",
    "세아베스틸지주": "001430.KS",
    "DB손해보험": "005830.KS",
    "메리츠화재": "000060.KS",
    "현대해상": "001450.KS",
    "LG디스플레이": "034220.KS",
    "SK네트웍스": "001740.KS",
    "SK바이오사이언스": "302440.KS",
    "롯데정밀화학": "004000.KS",
    "한전KPS": "051600.KS",
    "LX인터내셔널": "001120.KS",
    "LS": "006260.KS",
    "팬오션": "028670.KS",
    "호텔신라": "008770.KS",
    "신세계": "004170.KS",
    "현대백화점": "069960.KS",
    "롯데제과": "280360.KS",
    "동원산업": "006040.KS",
    "삼양식품": "003230.KS",
    "오뚜기": "007310.KS",
    "농심": "004370.KS",
    "제일약품": "002620.KS",
    "대웅제약": "069620.KS",
    "한미사이언스": "008930.KS",
    # 해외 주요 종목 (예시)
    "애플": "AAPL",
    "마이크로소프트": "MSFT",
    "테슬라": "TSLA",
    "엔비디아": "NVDA",
    "구글": "GOOGL", # GOOGL (클래스 A) 또는 GOOG (클래스 C) 중 하나 선택
    "아마존": "AMZN",
    "넷플릭스": "NFLX",
    "메타": "META", # 페이스북 -> 메타
    "토요타": "7203.T", # 일본
    "소니": "6758.T", # 일본
    "텐센트": "0700.HK", # 홍콩
    "알리바바": "9988.HK", # 홍콩
}

# 기본으로 표시할 7종목 (한글 회사명)
# KOREAN_TICKER_MAP에 정의된 이름만 사용해야 합니다.
DEFAULT_DISPLAY_COMPANIES = [
    "삼성전자", "SK 하이닉스", "현대자동차", "LG 에너지솔루션", "NAVER", "애플", "테슬라"
]

# ─────────────────────────────────────────────
# 유틸 함수
# ─────────────────────────────────────────────
def fmt_number(n, decimals=2, prefix="", suffix="", billions=False):
    """숫자 포맷팅 헬퍼"""
    if n is None or n == "N/A":
        return "—"
    try:
        n = float(n)
        if billions and n >= 1e9:
            return f"{prefix}{n/1e9:.1f}B{suffix}"
        if n >= 1e6:
            return f"{prefix}{n/1e6:.1f}M{suffix}"
        return f"{prefix}{n:,.{decimals}f}{suffix}"
    except Exception:
        return "—"

def get_currency_symbol(info):
    currency = info.get("currency", "USD")
    symbols = {"USD": "$", "KRW": "₩", "EUR": "€", "JPY": "¥", "GBP": "£", "HKD": "HK$"}
    return symbols.get(currency, currency + " ")

def metric_html(label, value, delta=None):
    """커스텀 메트릭 HTML 블록"""
    delta_html = ""
    if delta is not None:
        cls = "metric-delta-pos" if delta > 0 else ("metric-delta-neg" if delta < 0 else "metric-delta-neu")
        sign = "▲" if delta > 0 else ("▼" if delta < 0 else "—")
        delta_html = f'<div class="{cls}">{sign} {abs(delta):.2f}%</div>'
    return f"""
    <div class="metric-container">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """

@st.cache_data(ttl=60) # 60초 캐시 → 새로고침 버튼 누를 때마다 갱신
def fetch_stock_info(ticker_symbol: str):
    """yfinance에서 종목 정보 수집"""
    tk = yf.Ticker(ticker_symbol)
    info = tk.info
    news = tk.news # 최근 뉴스 리스트
    return info, news

def fetch_google_news(query: str):
    """Google News RSS (fallback)"""
    url = f"https://news.google.com/rss/search?q={query}+stock&hl=ko&gl=KR&ceid=KR:ko"
    feed = feedparser.parse(url)
    return feed.entries[:3]

# ─────────────────────────────────────────────
# 사이드바
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📈 주식 대시보드")
    st.markdown("---")
    
    # KOREAN_TICKER_MAP에서 회사 이름 목록 가져오기
    all_company_names = sorted(KOREAN_TICKER_MAP.keys())

    # 기본 선택값 설정 (DEFAULT_DISPLAY_COMPANIES가 map에 있는지 확인)
    default_selection_for_multiselect = [
        name for name in DEFAULT_DISPLAY_COMPANIES if name in all_company_names
    ]

    selected_company_names = st.multiselect(
        "🔍 조회할 회사 선택",
        options=all_company_names,
        default=default_selection_for_multiselect, # 기본 선택 종목
        placeholder="회사를 검색하거나 선택하세요.",
        help="목록에서 회사 이름을 검색하여 선택하세요. 선택하지 않으면 기본 7종목이 표시됩니다."
    )
    
    refresh_btn = st.button("🔄 새로고침 / 업데이트", type="primary")
    if refresh_btn:
        st.cache_data.clear() # 캐시 초기화 → 최신 데이터 강제 fetch
        st.rerun()
        
    st.markdown("---")
    st.markdown(
        "<div style='font-size:0.75rem;color:#4a5378;'>"
        "데이터 출처: Yahoo Finance<br>"
        "뉴스 출처: Google News RSS<br>"
        f"마지막 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        "</div>",
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────
# 메인 컨텐츠
# ─────────────────────────────────────────────
st.markdown(
    "<h1 style='color:#e2e8f0;font-size:1.8rem;font-weight:800;margin-bottom:4px;'>"
    "📈 주식 종합 대시보드</h1>"
    "<p style='color:#7c85a3;font-size:0.9rem;margin-bottom:24px;'>"
    "실시간 주가 · 재무 지표 · 주요 뉴스를 한눈에</p>",
    unsafe_allow_html=True,
)

# 사용자가 선택한 종목이 없으면 기본 종목 사용
if not selected_company_names:
    display_company_names = default_selection_for_multiselect
    st.info("ℹ️ 선택된 종목이 없어 기본 7종목이 표시됩니다. 사이드바에서 원하는 종목을 선택하세요.")
else:
    display_company_names = selected_company_names

# 한글 회사명을 티커 심볼로 변환
tickers_to_display = []
unsupported_names = []
for name in display_company_names:
    # 딕셔너리 키는 대문자로 저장했으므로, 입력도 대문자로 변환하여 검색
    ticker_symbol = KOREAN_TICKER_MAP.get(name.upper()) 
    if ticker_symbol:
        tickers_to_display.append(ticker_symbol)
    else:
        unsupported_names.append(name)

# 지원되지 않는 회사 이름이 있을 경우 경고 메시지 표시
if unsupported_names:
    st.warning(
        f"⚠️ 다음 회사 이름에 대한 정보를 찾을 수 없습니다: **{', '.join(unsupported_names)}**\n"
        "사이드바에서 선택 가능한 회사 목록을 확인해주세요."
    )

if not tickers_to_display:
    st.warning("표시할 종목이 없습니다. 사이드바에서 회사 이름을 선택해주세요.")
    st.stop()

# ─────────────────────────────────────────────
# 종목별 렌더링
# ─────────────────────────────────────────────
for sym in tickers_to_display:
    with st.spinner(f"{sym} 데이터 불러오는 중..."):
        try:
            info, news = fetch_stock_info(sym)
        except Exception as e:
            st.markdown(
                f'<div class="error-box">⚠️ <b>{sym}</b> 데이터 로드 실패: {e}</div>',
                unsafe_allow_html=True,
            )
            continue
            
    # info 딕셔너리가 비어있거나 필수 정보가 없는 경우 처리
    if not info or not info.get("quoteType"): # 최소한의 정보 확인
        st.markdown(
            f'<div class="error-box">⚠️ <b>{sym}</b> 에 대한 상세 정보를 찾을 수 없습니다. 티커 심볼이 정확한지 확인해주세요.</div>',
            unsafe_allow_html=True,
        )
        continue

    cur = get_currency_symbol(info)
    # yfinance에서 가져온 longName이 있으면 사용하고, 없으면 짧은 이름, 그것도 없으면 티커 심볼 사용
    name = info.get("longName") or info.get("shortName") or sym 
    
    # 가격 계산
    price = info.get("currentPrice") or info.get("regularMarketPrice")
    prev = info.get("previousClose") or info.get("regularMarketPreviousClose")

    chg_pct = None
    chg_abs = None
    if price is not None and prev is not None and prev != 0:
        chg_abs = price - prev
        chg_pct = (chg_abs / prev) * 100

    # 52주 범위
    lo52 = info.get("fiftyTwoWeekLow")
    hi52 = info.get("fiftyTwoWeekHigh")
    rng52 = f"{cur}{lo52:,.2f} ~ {cur}{hi52:,.2f}" if lo52 is not None and hi52 is not None else "—"
    
    # 배당수익률
    div_yield = info.get("dividendYield")
    div_str = f"{div_yield*100:.2f}%" if div_yield else "—"
    
    # 목표주가
    target = info.get("targetMeanPrice")
    target_str = fmt_number(target, prefix=cur)
    
    # 업종
    sector = info.get("sector", "—")
    industry = info.get("industry", "—")

    # ── 카드 시작 ──────────────────────────────
    st.markdown('<div class="stock-card">', unsafe_allow_html=True)
    
    # 종목명 + 가격 헤더
    price_color = "#e2e8f0" # 기본 색상
    chg_icon = ""
    chg_str = ""
    
    if chg_pct is not None:
        if chg_pct > 0:
            price_color = "#34d399"
            chg_icon = "▲"
        elif chg_pct < 0:
            price_color = "#f87171"
            chg_icon = "▼"
        chg_str = f"{chg_icon} {abs(chg_abs):,.2f} ({abs(chg_pct):.2f}%)"
    
    price_str = f"{cur}{price:,.2f}" if price is not None else "—"

    st.markdown(
        f'<div class="ticker-header">{sym} &nbsp;<span style="font-size:0.85rem;color:#7c85a3;">{name}</span></div>'
        f'<div style="display:flex;align-items:baseline;gap:14px;margin-bottom:8px;">'
        f' <span style="font-size:2rem;font-weight:800;color:{price_color};">{price_str}</span>'
        f' <span style="font-size:1rem;color:{price_color};font-weight:600;">{chg_str}</span>'
        f'</div>'
        f'<div class="company-name">📌 {sector} &nbsp;|&nbsp; {industry}</div>',
        unsafe_allow_html=True,
    )
    
    # ── 지표 메트릭 2행 ────────────────────────
    # Streamlit의 columns는 고정된 비율을 따르므로, 모바일에서 쌓이도록 직접적인 CSS 조정은 어렵습니다.
    # 대신, @media 쿼리에서 stHorizontalBlock의 flex-direction을 column으로 변경하여 쌓이게 합니다.
    cols1 = st.columns(5)
    metrics_row1 = [
        ("거래량", fmt_number(info.get("volume"), decimals=0)),
        ("시가총액", fmt_number(info.get("marketCap"), decimals=1, prefix=cur, billions=True)),
        ("PER (TTM)", fmt_number(info.get("trailingPE"), decimals=2)),
        ("PBR", fmt_number(info.get("priceToBook"), decimals=2)),
        ("EPS (TTM)", fmt_number(info.get("trailingEps"), decimals=2, prefix=cur)),
    ]
    for col, (lbl, val) in zip(cols1, metrics_row1):
        col.markdown(metric_html(lbl, val), unsafe_allow_html=True)
        
    cols2 = st.columns(5)
    metrics_row2 = [
        ("목표주가", target_str),
        ("52주 최저", fmt_number(lo52, prefix=cur) if lo52 is not None else "—"),
        ("52주 최고", fmt_number(hi52, prefix=cur) if hi52 is not None else "—"),
        ("배당수익률", div_str),
        ("베타", fmt_number(info.get("beta"), decimals=2)),
    ]
    for col, (lbl, val) in zip(cols2, metrics_row2):
        col.markdown(metric_html(lbl, val), unsafe_allow_html=True)
        
    # ── 뉴스 ──────────────────────────────────
    st.markdown('<div class="news-title">📰 주요 뉴스</div>', unsafe_allow_html=True)
    news_items = []
    
    # yfinance 뉴스 (우선)
    if news:
        for article in news[:3]:
            title = article.get("title", "")
            link = article.get("link", "#")
            pub = article.get("publisher", "")
            if title:
                news_items.append((title, link, pub))
                
    # 부족하면 Google News RSS 보충. yfinance의 longName 또는 입력받은 한글 이름을 쿼리에 사용
    if len(news_items) < 3:
        # 뉴스 검색 쿼리는 회사 이름 (yfinance에서 가져온 긴 이름)으로 하는 것이 더 효과적일 수 있습니다.
        news_query = info.get("longName") or info.get("shortName") or name 
        try:
            for entry in fetch_google_news(news_query): # 쿼리를 회사 이름으로 변경
                title = entry.get("title", "")
                link = entry.get("link", "#")
                source_data = entry.get("source", {})
                source = source_data.get("title", "Google News") if isinstance(source_data, dict) else "Google News"
                if title and len(news_items) < 3:
                    news_items.append((title, link, source))
        except Exception:
            pass # Google News 오류는 조용히 넘어감

    if news_items:
        for title, link, source in news_items[:3]:
            st.markdown(
                f'<div class="news-item">'
                f' <a href="{link}" target="_blank">{title}</a>'
                f' <div class="news-source">📡 {source}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
    else:
        st.markdown('<p style="color:#4a5378;font-size:0.85rem;">뉴스를 불러올 수 없습니다.</p>', unsafe_allow_html=True)
        
    st.markdown(
        f'<div class="update-time">🕐 {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} 기준</div>',
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)
