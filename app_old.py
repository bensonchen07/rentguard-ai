import os
import json
import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv
import pypdf

# 載入環境變數
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# 頁面配置 (寬版儀表板佈局)
st.set_page_config(
    page_title="RentGuard AI - 租屋合約智能守護系統",
    page_icon="🛡️",
    layout="wide"
)

# 初始化 Gemini Client
if not api_key:
    st.error("找不到 GEMINI_API_KEY，請確認是否已在 .env 檔案中設定或透過環境變數傳入。")
    st.stop()

client = genai.Client(api_key=api_key)
MODEL_NAME = 'gemini-3.5-flash-lite'

# -----------------------------------------------------------------------------
# 自訂 CSS 樣式
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, #0f2b2d 0%, #16383b 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 0 20px 20px 0;
        padding: 1rem;
    }

    .custom-card {
        padding: 20px;
        border-radius: 16px;
        margin-bottom: 20px;
        min-height: 350px;
        transition: all 0.3s ease-in-out;
    }
    
    .red-card {
        background: rgba(45, 15, 15, 0.6);
        border: 1px solid #ff4d4d;
        box-shadow: 0 0 15px rgba(255, 77, 77, 0.2);
    }
    .red-card:hover {
        box-shadow: 0 0 25px rgba(255, 77, 77, 0.4);
        transform: translateY(-3px);
    }

    .yellow-card {
        background: rgba(45, 38, 15, 0.6);
        border: 1px solid #ffcc00;
        box-shadow: 0 0 15px rgba(255, 204, 0, 0.2);
    }
    .yellow-card:hover {
        box-shadow: 0 0 25px rgba(255, 204, 0, 0.4);
        transform: translateY(-3px);
    }

    .green-card {
        background: rgba(15, 45, 25, 0.6);
        border: 1px solid #2ecc71;
        box-shadow: 0 0 15px rgba(46, 204, 113, 0.2);
    }
    .green-card:hover {
        box-shadow: 0 0 25px rgba(46, 204, 113, 0.4);
        transform: translateY(-3px);
    }

    .line-chat-container {
        background-color: #17212b;
        border-radius: 16px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        max-width: 100%;
    }
    .line-header {
        font-size: 16px;
        font-weight: bold;
        color: #ffffff;
        margin-bottom: 15px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        padding-bottom: 10px;
    }
    .line-bubble-tenant {
        background-color: #85e89d;
        color: #000000;
        padding: 14px 18px;
        border-radius: 16px 16px 4px 16px;
        margin: 10px 0;
        max-width: 90%;
        margin-left: auto;
        font-size: 14px;
        line-height: 1.6;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        white-space: pre-wrap;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #1fa2ff 0%, #12d8fa 50%, #06ffb7 100%);
        color: #000000;
        font-weight: bold;
        border: none;
        border-radius: 12px;
        padding: 0.6rem 1.5rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        opacity: 0.9;
        box-shadow: 0 0 15px rgba(18, 216, 250, 0.5);
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 左側側邊欄 (Sidebar)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚖️ 法律免責聲明與求助")
    st.markdown("""
    本系統提供的 AI 分析與談判草稿僅供參考，**不具正式法律效力**。若遇重大租賃糾紛，強烈建議尋求正式法律與行政途徑：
    
    * 📞 **消費者服務專線**：直撥 **1950**
    * ⚖️ **法律扶助基金會（法扶）**：免費法律諮詢預約
    * 🏠 **內政部不動產資訊平臺**：查詢最新定型化契約
    """)
    st.divider()
    st.markdown("### 💡 系統提示")
    st.info("本系統支援上傳 PDF 合約、純文字檔 (.txt) 以及房東對話截圖 (PNG/JPG)。")

# -----------------------------------------------------------------------------
# 右側主要內容區 (Main Content)
# -----------------------------------------------------------------------------
st.title("🛡️ RentGuard AI 租屋合約智能守護系統")
st.markdown("作為您的專業台灣房地產法律顧問與合約分析師，我們幫您嚴格審查租約與對話截圖中的霸王條款！")

st.markdown("### 1. 上傳合約文件或對話截圖")
uploaded_file = st.file_uploader(
    "請上傳租屋合約（支援 PDF、TXT、圖片格式）",
    type=["pdf", "txt", "png", "jpg", "jpeg"],
    label_visibility="collapsed"
)

file_content = None
file_part = None

if uploaded_file is not None:
    file_extension = uploaded_file.name.split('.')[-1].lower()
    
    if file_extension == 'pdf':
        try:
            reader = pypdf.PdfReader(uploaded_file)
            file_content = ""
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    file_content += text + "\n"
        except Exception as e:
            st.error(f"解析 PDF 發生錯誤: {e}")
            
    elif file_extension == 'txt':
        try:
            file_content = uploaded_file.getvalue().decode("utf-8")
        except Exception as e:
            st.error(f"讀取 TXT 發生錯誤: {e}")
            
    elif file_extension in ['png', 'jpg', 'jpeg']:
        mime_type = uploaded_file.type
        file_bytes = uploaded_file.getvalue()
        file_part = types.Part.from_bytes(data=file_bytes, mime_type=mime_type)

    st.markdown(f"""
    <div style="background-color: rgba(46, 204, 113, 0.15); border: 1px solid #2ecc71; padding: 10px 15px; border-radius: 10px; color: #2ecc71; margin-top: 10px;">
        ✅ 成功接收檔案：{uploaded_file.name}
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

if st.button("⭐ 開始 Gemini 合約深度健檢"):
    if uploaded_file is None:
        st.warning("請先上傳合約檔案或對話截圖！")
    else:
        with st.spinner("AI 正在進行嚴謹的 JSON 結構化法規比對中..."):
            try:
                # 守衛機制
                guardrail_prompt = "請判斷以下上傳的內容是否為『房屋租賃契約』、租屋相關條文、或是『房東與房客的對話紀錄/截圖』。如果無關請回傳『INVALID』，如果是請回傳『VALID』。"
                guardrail_contents = [guardrail_prompt]
                if file_content: guardrail_contents.append(file_content)
                if file_part: guardrail_contents.append(file_part)
                
                guard_response = client.models.generate_content(model=MODEL_NAME, contents=guardrail_contents)
                
                if "INVALID" in guard_response.text.strip().upper():
                    st.error("🚫 偵測到上傳內容可能非租屋合約或對話紀錄，請上傳正確的租屋文件！")
                else:
                    # 採用強制 JSON 輸出格式，保證資料絕對不會亂跑或擠壓
                    analysis_prompt = """
                    作為專業台灣房地產法律顧問與合約分析師，請根據內政部《住宅租賃定型化契約應記載及不得記載事項》嚴格審查上傳內容。
                    
                    請務必回傳一個合法的 JSON 格式（不要包在 markdown 程式碼區塊外，直接輸出 JSON），包含以下四個 key：
                    1. "red": 列出所有明顯違法、剝奪房客權益之「紅燈高風險條款」。若無違法條文，請填寫「本合約無重大違法紅燈條文，恭喜您！」。
                    2. "yellow": 列出雖未直接違法、但對房客不利之「黃燈潛在不利條文」。若無則填寫「無明顯不利之黃燈條文」。
                    3. "green": 列出合法且符合內政部規範之「綠燈合規條文」。
                    4. "draft": 提供一段給房東的 LINE 談判溝通草稿文字（純文字格式），語氣禮貌但堅定。
                    """
                    
                    analysis_contents = [analysis_prompt]
                    if file_content: analysis_contents.append(file_content)
                    if file_part: analysis_contents.append(file_part)
                        
                    # 強制指定以 JSON 格式回應
                    response = client.models.generate_content(
                        model=MODEL_NAME, 
                        contents=analysis_contents,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json"
                        )
                    )
                    
                    # 解析 JSON
                    try:
                        result_json = json.loads(response.text)
                        red_text = result_json.get("red", "無資料")
                        yellow_text = result_json.get("yellow", "無資料")
                        green_text = result_json.get("green", "無資料")
                        draft_text = result_json.get("draft", "請參閱上方分析結果。")
                    except Exception:
                        # 萬一 JSON 解析失敗的備防方案
                        red_text = response.text
                        yellow_text = "解析中..."
                        green_text = "解析中..."
                        draft_text = "房東您好..."

                    # -------------------------------------------------------------
                    # 2. AI 風險檢測報告 (卡片式展示)
                    # -------------------------------------------------------------
                    st.markdown("---")
                    st.header("2. AI 風險檢測報告")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown(f"""
                        <div class="custom-card red-card">
                            <h4 style="color: #ff4d4d; margin-top: 0;">🔴 高風險違法條文</h4>
                            <div style="font-size: 13px; line-height: 1.6; color: #e0e0e0; overflow-y: auto; max-height: 300px;">
                                {red_text.replace(chr(10), '<br>')}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    with col2:
                        st.markdown(f"""
                        <div class="custom-card yellow-card">
                            <h4 style="color: #ffcc00; margin-top: 0;">🟡 潛在不利條文</h4>
                            <div style="font-size: 13px; line-height: 1.6; color: #e0e0e0; overflow-y: auto; max-height: 300px;">
                                {yellow_text.replace(chr(10), '<br>')}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    with col3:
                        st.markdown(f"""
                        <div class="custom-card green-card">
                            <h4 style="color: #2ecc71; margin-top: 0;">🟢 合規條文</h4>
                            <div style="font-size: 13px; line-height: 1.6; color: #e0e0e0; overflow-y: auto; max-height: 300px;">
                                {green_text.replace(chr(10), '<br>')}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                    # -------------------------------------------------------------
                    # 3. 一鍵 LINE 談判草稿 (擬真聊天室 UI)
                    # -------------------------------------------------------------
                    st.markdown("---")
                    st.header("3. 💬 一鍵 LINE 談判草稿")
                    
                    st.markdown(f"""
                    <div class="line-chat-container">
                        <div class="line-header">
                            <span>🟢 陳小華 (租客視角擬真預覽)</span>
                        </div>
                        <div style="font-size: 12px; color: #8c9ba5; text-align: center; margin-bottom: 10px;">下午 5:38</div>
                        <div class="line-bubble-tenant">
                            {draft_text.replace(chr(10), '<br>')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # 複製專區
                    st.subheader("📋 一鍵複製談判草稿")
                    st.code(draft_text, language="text")
                    
            except Exception as e:
                st.error(f"分析過程發生錯誤: {e}")
