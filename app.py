import os
import json
import html
from datetime import datetime

import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv
import pypdf

# -----------------------------------------------------------------------------
# 基本設定與頁面配置
# -----------------------------------------------------------------------------
load_dotenv()

st.set_page_config(
    page_title="RentGuard AI｜租屋合約智能守護系統",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

api_key = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-3.5-flash-lite"  # 嚴格保持原模型名稱

# 初始化 Session State 頁面導航狀態
if "current_page" not in st.session_state:
    st.session_state.current_page = "合約檢測"

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None
if "uploaded_name" not in st.session_state:
    st.session_state.uploaded_name = None

# -----------------------------------------------------------------------------
# 高級 Dark Glassmorphism & Neon Lighting CSS 樣式
# -----------------------------------------------------------------------------
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Noto+Sans+TC:wght@400;500;600;700;800&display=swap');

:root {
    --bg-dark: #050c1e;
    --panel-glass: rgba(14, 27, 54, 0.72);
    --panel-glass-border: rgba(95, 155, 255, 0.22);
    --panel-glass-hover: rgba(22, 42, 80, 0.82);
    --neon-cyan: #00f0ff;
    --neon-blue: #3a86ff;
    --neon-purple: #8338ec;
    --text-primary: #f5f8ff;
    --text-secondary: #a0b3d6;
    --text-muted: #6b82aa;
}

html, body, [class*="css"] {
    font-family: 'Inter', 'Noto Sans TC', -apple-system, sans-serif;
}

.stApp {
    background: 
      radial-gradient(circle at 15% 15%, rgba(0, 240, 255, 0.08), transparent 40%),
      radial-gradient(circle at 85% 85%, rgba(131, 56, 236, 0.1), transparent 45%),
      linear-gradient(135deg, #040915 0%, #0a152d 50%, #060c1b 100%);
    color: var(--text-primary);
}

[data-testid="stHeader"] { background: transparent; }
[data-testid="stToolbar"] { right: 1rem; }
.block-container { padding-top: 1.5rem; padding-bottom: 2.5rem; max-width: 1750px; }

/* 側邊欄邊框與玻璃效果 */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, rgba(8, 17, 38, 0.95) 0%, rgba(5, 11, 24, 0.98) 100%);
    border-right: 1px solid rgba(80, 145, 255, 0.2);
    backdrop-filter: blur(20px);
}
[data-testid="stSidebar"] > div { padding-top: 1.2rem; }

/* 側邊欄導航按鈕客製樣式 */
.sidebar-nav-btn {
    width: 100%;
    margin-bottom: 8px;
}

div[data-testid="stSidebar"] .stButton > button {
    width: 100%;
    justify-content: flex-start;
    padding: 10px 16px;
    font-size: 14px;
    font-weight: 600;
    border-radius: 12px;
    border: 1px solid rgba(95, 155, 255, 0.15);
    background: rgba(15, 30, 60, 0.4);
    color: #c0d3f8;
    box-shadow: none;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    min-height: 44px;
}

div[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(30, 60, 110, 0.6);
    border-color: rgba(0, 240, 255, 0.5);
    color: #ffffff;
    transform: translateX(4px);
    box-shadow: 0 0 15px rgba(0, 240, 255, 0.2);
}

/* 側邊欄選中狀態標籤 */
.nav-active-indicator {
    background: linear-gradient(90deg, rgba(0, 240, 255, 0.2) 0%, rgba(58, 134, 255, 0.1) 100%);
    border-left: 3px solid var(--neon-cyan);
    border-radius: 0 8px 8px 0;
    padding: 2px 8px;
    margin-bottom: 6px;
    font-size: 11px;
    font-weight: 700;
    color: var(--neon-cyan);
    letter-spacing: 0.08em;
}

/* 按鈕風格微調 */
.stButton > button, .stDownloadButton > button {
    border: 1px solid rgba(118, 173, 255, 0.35);
    border-radius: 12px;
    color: white;
    font-weight: 700;
    background: linear-gradient(110deg, #1b85ff 0%, #4f46e5 55%, #7c3aed 100%);
    box-shadow: 0 4px 20px rgba(59, 130, 246, 0.3);
    transition: all 0.25s ease;
    min-height: 46px;
}
.stButton > button:hover, .stDownloadButton > button:hover {
    transform: translateY(-2px);
    border-color: rgba(0, 240, 255, 0.8);
    box-shadow: 0 8px 25px rgba(0, 240, 255, 0.4);
    color: white;
}

/* 容器邊框卡片化 */
div[data-testid="stVerticalBlockBorderWrapper"] {
    border: 1px solid var(--panel-glass-border);
    border-radius: 20px;
    background: var(--panel-glass);
    backdrop-filter: blur(16px);
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.08);
}

div[data-testid="stFileUploader"] section {
    background: rgba(10, 22, 46, 0.65);
    border: 1.5px dashed rgba(0, 240, 255, 0.4);
    border-radius: 16px;
    transition: all 0.3s ease;
}
div[data-testid="stFileUploader"] section:hover {
    border-color: var(--neon-cyan);
    background: rgba(15, 32, 65, 0.85);
    box-shadow: 0 0 20px rgba(0, 240, 255, 0.15);
}

/* Brand Area */
.rg-brand {
    display: flex; align-items: center; gap: 14px; padding: 10px 0 24px;
}
.rg-shield {
    width: 52px; height: 52px; border-radius: 16px; display: flex; align-items: center; justify-content: center;
    font-size: 28px; background: linear-gradient(135deg, #00f0ff 0%, #3a86ff 50%, #8338ec 100%);
    box-shadow: 0 0 25px rgba(0, 240, 255, 0.4);
}
.rg-brand-title { font-size: 22px; font-weight: 800; color: #ffffff; letter-spacing: -0.02em; }
.rg-brand-sub { font-size: 12px; color: var(--text-secondary); margin-top: 2px; }

/* Dashboard Header Hero */
.hero {
    padding: 8px 4px 26px;
    display: flex; justify-content: space-between; align-items: center; gap: 20px;
}
.hero-kicker { color: var(--neon-cyan); font-weight: 700; letter-spacing: 0.14em; font-size: 12px; text-transform: uppercase; }
.hero-title { font-size: clamp(26px, 3.2vw, 42px); font-weight: 800; line-height: 1.2; margin: 6px 0; background: linear-gradient(120deg, #ffffff 30%, #a5c7ff 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.hero-sub { color: var(--text-secondary); font-size: 14px; line-height: 1.75; }
.hero-icon { font-size: 58px; filter: drop-shadow(0 0 20px rgba(0, 240, 255, 0.4)); }

.section-heading { display: flex; align-items: center; gap: 12px; font-weight: 800; font-size: 20px; margin-bottom: 16px; color: #fff; }
.section-num {
    width: 32px; height: 32px; border-radius: 10px; display: inline-flex; align-items: center; justify-content: center;
    color: #040915; font-weight: 800; background: linear-gradient(135deg, var(--neon-cyan), var(--neon-blue));
    box-shadow: 0 0 12px rgba(0, 240, 255, 0.3);
}

/* 三色卡片高階 Neon 風格 */
.risk-card {
    height: 100%; min-height: 280px; border-radius: 18px; padding: 20px;
    border: 1px solid; background: rgba(12, 23, 46, 0.8); backdrop-filter: blur(12px);
    transition: all 0.3s ease; position: relative; overflow: hidden;
}
.risk-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px;
}
.risk-red { 
    border-color: rgba(255, 90, 120, 0.4); 
    box-shadow: 0 8px 30px rgba(255, 50, 80, 0.12);
}
.risk-red::before { background: linear-gradient(90deg, #ff3366, #ff6b8b); }
.risk-red:hover { border-color: rgba(255, 90, 120, 0.8); box-shadow: 0 12px 35px rgba(255, 50, 80, 0.25); transform: translateY(-3px); }

.risk-yellow { 
    border-color: rgba(255, 195, 77, 0.4); 
    box-shadow: 0 8px 30px rgba(255, 180, 0, 0.1);
}
.risk-yellow::before { background: linear-gradient(90deg, #ffb703, #ffd166); }
.risk-yellow:hover { border-color: rgba(255, 195, 77, 0.8); box-shadow: 0 12px 35px rgba(255, 180, 0, 0.22); transform: translateY(-3px); }

.risk-green { 
    border-color: rgba(76, 227, 161, 0.4); 
    box-shadow: 0 8px 30px rgba(50, 220, 150, 0.1);
}
.risk-green::before { background: linear-gradient(90deg, #06d6a0, #70e4d5); }
.risk-green:hover { border-color: rgba(76, 227, 161, 0.8); box-shadow: 0 12px 35px rgba(50, 220, 150, 0.22); transform: translateY(-3px); }

.risk-head { font-size: 17px; font-weight: 800; margin-bottom: 12px; display: flex; align-items: center; gap: 8px; }
.risk-content { color: #d5e3fc; font-size: 13.5px; line-height: 1.75; white-space: pre-wrap; overflow-wrap: anywhere; max-height: 380px; overflow-y: auto; padding-right: 4px; }

/* 聊天室與玻璃容器 */
.chat-panel {
    border: 1px solid rgba(0, 240, 255, 0.25); border-radius: 20px; overflow: hidden;
    background: linear-gradient(180deg, rgba(14, 27, 54, 0.95) 0%, rgba(8, 16, 34, 0.95) 100%);
    box-shadow: 0 12px 35px rgba(0, 0, 0, 0.3);
}
.chat-head { padding: 16px 20px; border-bottom: 1px solid rgba(115, 155, 220, 0.18); font-weight: 800; font-size: 17px; background: rgba(20, 40, 80, 0.4); }
.chat-body { padding: 18px; }
.chat-bubble { padding: 13px 16px; border-radius: 16px; margin: 12px 0; line-height: 1.65; font-size: 13.5px; }
.chat-ai { background: rgba(40, 70, 130, 0.35); border: 1px solid rgba(140, 170, 235, 0.18); color: #e1ecff; }
.chat-user { background: linear-gradient(120deg, #00f0ff 0%, #70e4d5 100%); color: #041226; font-weight: 600; margin-left: 10%; }
.chat-note { font-size: 12px; color: var(--text-muted); text-align: center; padding: 6px; }

/* 底部 feature strip */
.feature-strip {
    display: flex; gap: 16px; justify-content: space-around; flex-wrap: wrap; padding: 18px;
    border: 1px solid rgba(95, 155, 255, 0.2); border-radius: 20px;
    background: rgba(12, 25, 50, 0.6); backdrop-filter: blur(12px); margin-top: 24px;
}
.feature { color: #d9e6ff; font-size: 13.5px; font-weight: 700; }
.feature span { color: var(--text-muted); font-size: 11.5px; font-weight: 400; display: block; margin-top: 3px; }
.footer-note { color: var(--text-muted); font-size: 11.5px; text-align: center; margin-top: 20px; }

/* 知識庫與 FAQ 專用面板 */
.kb-card {
    background: rgba(14, 27, 54, 0.65); border: 1px solid rgba(95, 155, 255, 0.2);
    border-radius: 16px; padding: 22px; margin-bottom: 16px; transition: all 0.3s ease;
}
.kb-card:hover { border-color: rgba(0, 240, 255, 0.5); transform: translateY(-2px); }
.kb-title { font-size: 18px; font-weight: 700; color: var(--neon-cyan); margin-bottom: 10px; }
.kb-body { font-size: 14px; color: #d0e0ff; line-height: 1.8; }

</style>
""",
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# Gemini 初始化檢查
# -----------------------------------------------------------------------------
if not api_key:
    st.error("找不到 GEMINI_API_KEY。請確認 .env 檔案中已正確設定 API Key。")
    st.stop()

client = genai.Client(api_key=api_key)

# -----------------------------------------------------------------------------
# Sidebar 導航邏輯 (實作 Session State 切換與獨立高亮)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        """
        <div class="rg-brand">
            <div class="rg-shield">🛡️</div>
            <div>
                <div class="rg-brand-title">RentGuard AI</div>
                <div class="rg-brand-sub">租屋合約智能守護系統</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    st.markdown("<div style='font-size:12px; font-weight:700; color:#7899d0; margin-bottom:10px;'>功能導航選單</div>", unsafe_allow_html=True)
    
    pages = [
        ("合約檢測", "📝 合約深度檢測"),
        ("法律知識庫", "📚 租屋法律知識庫"),
        ("常見問題", "❔ 常見問題 FAQ"),
        ("關於我們", "ℹ️ 關於 RentGuard")
    ]
    
    for page_key, label in pages:
        is_active = (st.session_state.current_page == page_key)
        if is_active:
            st.markdown(f"<div class='nav-active-indicator'>● CURRENT PAGE</div>", unsafe_allow_html=True)
        
        # 點擊按鈕切換 Session State 頁面
        if st.button(label, key=f"nav_btn_{page_key}"):
            st.session_state.current_page = page_key
            st.rerun()

    st.divider()
    
    # 免責聲明與援助卡片
    st.markdown("### ⚖️ 法律免責聲明")
    st.caption(
        "本系統 AI 分析結果僅供輔助參考，不具備正式法律意見效力。"
        "若遇到爭議，建議洽詢專業律師或消費保護機構。"
    )
    with st.expander("📞 免費法律求助管道"):
        st.markdown(
            """
            - **1950** 全國消費者服務專線
            - **法律扶助基金會** 免費法律諮詢
            - **內政部不動產資訊平台** 定型化契約範本
            """
        )
    
    st.info("💡 支援 PDF、TXT 及 PNG/JPG 對話截圖。")
    st.markdown("<div class='footer-note'>RENTGUARD AI · PREMIUM DASHBOARD</div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 頁面路由與展示 (依據 st.session_state.current_page 切換)
# -----------------------------------------------------------------------------

# =============================================================================
# 頁面 1：合約檢測 (核心 AI 分析儀表板)
# =============================================================================
if st.session_state.current_page == "合約檢測":
    
    # Dashboard Header
    st.markdown(
        """
        <div class="hero">
          <div>
            <div class="hero-kicker">AI-powered legal risk analysis</div>
            <div class="hero-title">RentGuard AI 合約深度健檢</div>
            <div class="hero-sub">秒級解析房屋租賃契約條文與房東對話截圖，自動對照內政部定型化契約規範，<br>
            精準標示潛在霸王條款、評估風險等級，並提供即用型 LINE 談判溝通草稿。</div>
          </div>
          <div class="hero-icon">📄🛡️</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    main_col, chat_col = st.columns([2.15, 1], gap="large")

    with main_col:
        # 上傳區塊
        with st.container(border=True):
            st.markdown(
                "<div class='section-heading'><span class='section-num'>1</span> 上傳合約文件或對話截圖</div>",
                unsafe_allow_html=True,
            )
            upload_col, info_col = st.columns([1.55, 1], gap="medium")
            with upload_col:
                uploaded_file = st.file_uploader(
                    "上傳租屋合約",
                    type=["pdf", "txt", "png", "jpg", "jpeg"],
                    label_visibility="collapsed",
                    help="支援 PDF、TXT、PNG、JPG/JPEG",
                )
            with info_col:
                st.markdown(
                    """
                    <div style="padding:16px;border:1px solid rgba(110,160,255,.22);
                    border-radius:14px;background:rgba(13,27,54,.5);height:100%;">
                    <div style="font-weight:700;margin-bottom:12px;color:#35e1ff;">📂 支援檔案格式</div>
                    <div style="display:flex;gap:12px;justify-content:space-around;text-align:center;">
                      <div><div style="font-size:26px;">📕</div><small style="color:#a0b3d6;">PDF 檔</small></div>
                      <div><div style="font-size:26px;">📘</div><small style="color:#a0b3d6;">TXT 檔</small></div>
                      <div><div style="font-size:26px;">🖼️</div><small style="color:#a0b3d6;">對話截圖</small></div>
                    </div>
                    <div style="color:#809bcc;font-size:11.5px;margin-top:12px;">包含紙本拍照、紙本掃瞄 PDF 或 LINE 截圖</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            file_content = None
            file_part = None

            if uploaded_file is not None:
                file_extension = uploaded_file.name.rsplit(".", 1)[-1].lower()

                try:
                    if file_extension == "pdf":
                        reader = pypdf.PdfReader(uploaded_file)
                        file_content = ""
                        for page in reader.pages:
                            extracted = page.extract_text()
                            if extracted:
                                file_content += extracted + "\n"
                    elif file_extension == "txt":
                        file_content = uploaded_file.getvalue().decode("utf-8-sig")
                    elif file_extension in ["png", "jpg", "jpeg"]:
                        file_part = types.Part.from_bytes(
                            data=uploaded_file.getvalue(),
                            mime_type=uploaded_file.type,
                        )
                except Exception as exc:
                    st.error(f"讀取檔案發生錯誤：{exc}")

                st.success(f"已接收檔案：{uploaded_file.name}（{uploaded_file.size / 1024:.1f} KB）")

            analyze_clicked = st.button("✨ 開始 Gemini 合約深度健檢", use_container_width=True)

            if analyze_clicked:
                if uploaded_file is None:
                    st.warning("請先上傳合約檔案或對話截圖。")
                elif not file_content and not file_part:
                    st.warning("無法讀取檔案內容，請確認文件是否有效。")
                else:
                    with st.spinner("Gemini 3.5 Flash-Lite 正在進行深度法規對照，請稍候..."):
                        try:
                            # 1. Guardrail Check
                            guardrail_prompt = (
                                "請判斷以下上傳內容是否為房屋租賃契約、租屋相關條文，"
                                "或房東與房客的對話紀錄/截圖。若無關請只回傳 INVALID，"
                                "若相關請只回傳 VALID。"
                            )
                            guardrail_contents = [guardrail_prompt]
                            if file_content:
                                guardrail_contents.append(file_content)
                            if file_part:
                                guardrail_contents.append(file_part)

                            guard_response = client.models.generate_content(
                                model=MODEL_NAME,
                                contents=guardrail_contents,
                            )
                            guard_text = (guard_response.text or "").strip().upper()

                            if "INVALID" in guard_text:
                                st.session_state.analysis_result = None
                                st.error("🚫 偵測到內容可能與租屋合約或房東對話無關，請上傳正確的租屋文件。")
                            else:
                                # 2. Structured JSON Analysis
                                analysis_prompt = """
你是台灣租屋合約分析助手。請依據台灣住宅租賃相關規範審查上傳內容。
請回傳合法 JSON，不要使用 Markdown code fence，包含以下四個 key：
{
  "red": "明顯違法或高度風險條款",
  "yellow": "未必違法但可能對房客不利的條款",
  "green": "符合規範或相對合理的條款",
  "draft": "給房東的 LINE 溝通草稿，禮貌但堅定"
}
若無相應內容，請明確寫出無明顯發現。不要把 AI 分析描述成正式法律意見。
"""
                                analysis_contents = [analysis_prompt]
                                if file_content:
                                    analysis_contents.append(file_content)
                                if file_part:
                                    analysis_contents.append(file_part)

                                response = client.models.generate_content(
                                    model=MODEL_NAME,
                                    contents=analysis_contents,
                                    config=types.GenerateContentConfig(
                                        response_mime_type="application/json"
                                    ),
                                )
                                result_json = json.loads(response.text)
                                st.session_state.analysis_result = {
                                    "red": str(result_json.get("red", "無資料")),
                                    "yellow": str(result_json.get("yellow", "無資料")),
                                    "green": str(result_json.get("green", "無資料")),
                                    "draft": str(result_json.get("draft", "請參閱分析結果。")),
                                    "filename": uploaded_file.name,
                                    "timestamp": datetime.now().strftime("%H:%M"),
                                }
                                st.session_state.uploaded_name = uploaded_file.name
                        except json.JSONDecodeError:
                            st.error("Gemini 回傳格式解析失敗，請稍後重試。")
                        except Exception as exc:
                            st.error(f"分析過程發生錯誤：{exc}")

        # 2. Risk Report Display
        result = st.session_state.analysis_result
        with st.container(border=True):
            st.markdown(
                "<div class='section-heading'><span class='section-num'>2</span> AI 風險檢測報告</div>",
                unsafe_allow_html=True,
            )
            if result:
                st.caption(f"📄 分析文件：{result['filename']} · 🕒 完成時間：{result['timestamp']}")
                red, yellow, green = st.columns(3, gap="medium")
                cards = [
                    (red, "risk-red", "🔴 高風險條款", "red"),
                    (yellow, "risk-yellow", "🟡 潛在不利條款", "yellow"),
                    (green, "risk-green", "🟢 合規條款", "green"),
                ]
                for col, css_class, title, key in cards:
                    with col:
                        safe_content = html.escape(result[key])
                        st.markdown(
                            f"""
                            <div class="risk-card {css_class}">
                              <div class="risk-head">{title}</div>
                              <div class="risk-content">{safe_content}</div>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
            else:
                st.markdown(
                    """
                    <div style="padding:40px 20px;text-align:center;color:#8ea6d4;">
                      <div style="font-size:42px;margin-bottom:8px;">🔍</div>
                      <div style="font-weight:700;color:#dce8ff;font-size:16px;">等待合約分析</div>
                      <div style="font-size:13px;color:#7895c7;margin-top:4px;">請於上方區塊上傳租屋合約或對話截圖，並點擊健檢按鈕。</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # 右側側邊對話欄與 LINE 草稿
    with chat_col:
        st.markdown(
            """
            <div class="chat-panel">
              <div class="chat-head">🤖 RentGuard 法律 AI 助理 <span style="float:right;color:#00f0ff;font-size:12px;">● 在線處理中</span></div>
              <div class="chat-body">
                <div class="chat-bubble chat-ai">您好！我是您的租屋法律 AI 助理。上傳文件後，我會為您比對內政部定型化契約應記載及不得記載事項。</div>
                <div class="chat-note">AI 分析僅供參考，不代表正式法律意見。</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        result = st.session_state.analysis_result
        if result:
            st.markdown(
                "<div class='chat-bubble chat-ai'>✅ 合約健檢完畢！請檢視左側三色燈號風險卡片。</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                "<div class='chat-bubble chat-user'>幫我生成傳給房東的 LINE 談判草稿</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                "<div class='chat-bubble chat-ai'>已為您整理好談判訊息草稿，請在下方預覽或編輯。</div>",
                unsafe_allow_html=True,
            )
            with st.container(border=True):
                st.markdown("### 💬 LINE 談判草稿")
                st.text_area(
                    "草稿內容（可隨時編輯微調）",
                    value=result["draft"],
                    height=240,
                    key="draft_edit",
                )
                st.download_button(
                    "📥 下載談判草稿 (.txt)",
                    data=st.session_state.get("draft_edit", result["draft"]),
                    file_name="RentGuard_LINE_Negotiation_Draft.txt",
                    mime="text/plain",
                    use_container_width=True,
                )
                st.caption("建議發送前再次核對實際租屋細節與溝通語氣。")
        else:
            st.markdown(
                """
                <div class="chat-bubble chat-ai">
                <b>💡 快速上手指南：</b><br>
                1. 點擊左側上傳合約或對話截圖<br>
                2. 按下「開始 Gemini 合約深度健檢」<br>
                3. 即時獲取風險評估與談判對話
                </div>
                """,
                unsafe_allow_html=True,
            )

# =============================================================================
# 頁面 2：租屋法律知識庫
# =============================================================================
elif st.session_state.current_page == "法律知識庫":
    st.markdown(
        """
        <div class="hero">
          <div>
            <div class="hero-kicker">Knowledge Base</div>
            <div class="hero-title">📚 台灣租屋法律知識庫</div>
            <div class="hero-sub">收錄最新《住宅租賃定型化契約應記載及不得記載事項》重點與常見陷阱。</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_a, col_b = st.columns(2, gap="large")
    
    with col_a:
        st.markdown(
            """
            <div class="kb-card">
                <div class="kb-title">🛑 絕對不可約定事項 (常見紅燈違法霸王條款)</div>
                <div class="kb-body">
                    根據內政部公告，若合約出現以下條款<b>依法直接無效</b>：<br><br>
                    1. <b>轉嫁稅賦</b>：約定房客需負擔房屋稅、地價稅或房東租賃所得稅。<br>
                    2. <b>拋棄提前終止權</b>：限制房客依法法定提前解約的權利。<br>
                    3. <b>過高違約金</b>：提前解約違約金最高不得超過「一個月租金」。<br>
                    4. <b>限制報稅或補助</b>：禁止房客申報租金扣除額、申請政府租金補貼或遷入戶籍。
                </div>
            </div>
            
            <div class="kb-card">
                <div class="kb-title">💰 押金與費用約定規範</div>
                <div class="kb-body">
                    1. <b>押金上限</b>：押金最高不得超過「兩個月租金總額」，多收取部分房客得要求抵扣租金。<br>
                    2. <b>水電費分擔</b>：度數計費不得超過台電所定當月用電最高級距每度金額。<br>
                    3. <b>押金退還</b>：租賃關係消滅，房客交還房屋後，房東應即退還押金或抵扣後之餘額。
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_b:
        st.markdown(
            """
            <div class="kb-card">
                <div class="kb-title">🛠️ 房屋修繕責任歸屬</div>
                <div class="kb-body">
                    1. <b>法定修繕責任</b>：出租期間房屋及附屬設備（水電管線、熱水器、冷氣等）自然耗損，依法應由<b>出租人（房東）負責維修</b>。<br>
                    2. <b>特約例外</b>：若雙方約定由房客負擔，僅限於消耗性物品（如燈泡）或明訂特定品項，不可全盤概括歸責。<br>
                    3. <b>怠於修繕</b>：房東經催告限期修繕仍未修繕者，房客得自行修繕並要求由租金扣除。
                </div>
            </div>

            <div class="kb-card">
                <div class="kb-title">🔑 隱私與住宅侵入問題</div>
                <div class="kb-body">
                    1. <b>隨時檢查權無效</b>：約定「房東得隨時進入檢查屋況」屬侵害居住安寧，依法無效。<br>
                    2. <b>住宅侵入罪</b>：出租後房屋占有權移轉給房客，房東未經允許擅自開門進入，恐構成刑法《侵入住宅罪》。
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# =============================================================================
# 頁面 3：常見問題 (FAQ)
# =============================================================================
elif st.session_state.current_page == "常見問題":
    st.markdown(
        """
        <div class="hero">
          <div>
            <div class="hero-kicker">Frequently Asked Questions</div>
            <div class="hero-title">❔ 常見租屋糾紛 FAQ</div>
            <div class="hero-sub">彙整租客最常遇到的爭議情境與解決方案。</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        st.subheader(" Q1: 房東在合約中寫「退租時押金全額沒收」，這樣有效嗎？")
        st.write("無效。根據《住宅租賃定型化契約應記載及不得記載事項》，提前終止租約之違約金最高不得超過「一個月租金」。超出部分無效，房東不得全額沒收兩個月押金。")

        st.divider()

        st.subheader(" Q2: 房東說「如果報稅或申請補貼就要調漲租金」，合法嗎？")
        st.write("不合法。定型化契約明訂不得約定限制承租人申報租賃費用支出與申請租金補貼。若房東因此片面調漲租金或威脅解約，已違反規定，房客可向直轄市、縣（市）政府消費者服務中心申訴。")

        st.divider()

        st.subheader(" Q3: 上傳合約給 RentGuard AI 檢測會不會洩漏個人隱私？")
        st.write("RentGuard AI 僅在您單次點擊分析時將文字/圖片傳送至 API 處理，系統不會將您的真實個資儲存至外部公開資料庫。若仍有疑慮，建議在拍照或上傳前將姓名、身分證字號等個人敏感資訊做遮蔽。")

        st.divider()

        st.subheader(" Q4: 如果房東堅持不改合約中的違法條文，該怎麼辦？")
        st.write("您可以使用本系統生成的「LINE 談判草稿」先禮貌與房東溝通。若溝通無效且已簽約，該違法條款在法律上依然無效。遭遇重大爭議時，可撥打 1950 消費者服務專線或向法律扶助基金會尋求法律協助。")

# =============================================================================
# 頁面 4：關於我們 (About Us)
# =============================================================================
elif st.session_state.current_page == "關於我們":
    st.markdown(
        """
        <div class="hero">
          <div>
            <div class="hero-kicker">About RentGuard AI</div>
            <div class="hero-title">ℹ️ 關於 RentGuard AI 租屋守護團隊</div>
            <div class="hero-sub">打造讓租屋族安心、透明且公平的智能契約審查工具。</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        st.markdown(
            """
            ### 🎯 我們的使命
            台灣租屋市場長期存在資訊不對稱與合約霸王條款問題。許多學生與年輕上班族在簽約時往往因為缺乏法律背景，或是迫於租屋壓力而簽下對自己極度不利的合約。
            
            **RentGuard AI** 結合前沿 AI 語言模型（Gemini 3.5 Flash-Lite）與台灣住宅租賃法律知識，旨在為每位租客提供即時、精準且平易近人的合約風險健檢服務。
            
            ---
            
            ### ⚡ 核心功能與技術特色
            * **多模態解析**：支援 PDF 合約、純文字條文以及 LINE 對話截圖。
            * **定型化契約比對**：精準依照內政部應記載及不得記載事項進行三色燈號風險分類（紅燈違法、黃燈不利、綠燈合規）。
            * **談判草稿生成**：生成理性、禮貌且具法律依據的溝通文字，降低與房東溝通的摩擦與心理負擔。
            * **結構化防護 (JSON Schema)**：確保 AI 輸出穩定無錯位。
            
            ---
            
            ### 🛡️ 社會責任與免責聲明
            RentGuard AI 致力於促進租賃市場資訊透明。本系統產出之報告及建議僅供參考，不代表正式法律意見。遭遇複雜訟爭時，請尋求專業律師與消費保護機關之協助。
            """,
            unsafe_allow_html=True,
        )

# -----------------------------------------------------------------------------
# 頁尾資訊
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="feature-strip">
      <div class="feature">🛡️ 定型化契約比對<span>依據台灣內政部法規標準</span></div>
      <div class="feature">⚡ 多模態 AI 解析<span>支援 PDF / TXT / 對話截圖</span></div>
      <div class="feature">🔒 隱私安全防範<span>即時運算不留存敏感個資</span></div>
    </div>
    <div class="footer-note">RentGuard AI · 租屋合約智能守護系統 · Version 2.0 Premium Dashboard</div>
    """,
    unsafe_allow_html=True,
)
