import os
import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv
import pypdf

# 載入環境變數
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# 頁面配置
st.set_page_config(
    page_title="RentGuard AI - 租屋合約智能守護系統",
    page_icon="🛡️",
    layout="centered"
)

# 初始化 Gemini Client
if not api_key:
    st.error("找不到 GEMINI_API_KEY，請確認是否已在 .env 檔案中設定或透過環境變數傳入。")
    st.stop()

client = genai.Client(api_key=api_key)
# 嚴格使用專案指定的模型
MODEL_NAME = 'gemini-3.5-flash-lite'

st.title("🛡️ RentGuard AI 租屋合約智能守護系統")
st.markdown("作為您的專業台灣房地產法律顧問與合約分析師，我們幫您嚴格審查租約與對話截圖中的霸王條款！")

# -----------------------------------------------------------------------------
# 法律免責聲明與求助管道 (側邊欄保留通用防護網)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.header("⚠️ 法律免責聲明與求助")
    st.markdown("""
    本系統提供的 AI 分析與談判草稿僅供參考，**不具正式法律效力**。若遇重大租賃糾紛，強烈建議尋求正式法律與行政途徑：
    
    * 📞 **全國消費者服務專線**：直撥 **1950**（由各縣市政府消費者服務中心處理）。
    * ⚖️ **法律扶助基金會（法扶）**：提供符合資格者免費法律諮詢與訴訟代墊。
    * 🏠 **內政部不動產資訊平臺**：查詢最新「住宅租賃定型化契約應記載及不得記載事項」。
    """)
    st.divider()
    st.info("💡 提示：本系統支援上傳 PDF 合約、純文字檔 (.txt) 以及房東對話截圖 (PNG/JPG。")

# -----------------------------------------------------------------------------
# 檔案上傳元件
# -----------------------------------------------------------------------------
uploaded_file = st.file_uploader(
    "1. 上傳合約文件或對話截圖",
    type=["pdf", "txt", "png", "jpg", "jpeg"],
    help="支援 PDF 檔案、TXT 文字檔或房東對話截圖"
)

file_content = None
file_part = None
mime_type = None

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

    st.success(f"成功接收檔案：{uploaded_file.name}")

if st.button("🚀 開始 Gemini 合約深度健檢", type="primary"):
    if uploaded_file is None:
        st.warning("請先上傳合約檔案或對話截圖！")
    else:
        with st.spinner("AI 正在進行合約內容檢核與法規比對中..."):
            try:
                # -------------------------------------------------------------
                # 防惡搞守衛 (Guardrail)
                # -------------------------------------------------------------
                guardrail_prompt = "請判斷以下上傳的內容是否為『房屋租賃契約』、租屋相關條文、或是『房東與房客的對話紀錄/截圖』。如果內容是無關的檔案（例如數學考卷、程式碼、發票、無關的文章等），請僅回傳『INVALID』；如果是租屋相關合約或對話，請回傳『VALID』。"
                
                guardrail_contents = [guardrail_prompt]
                if file_content:
                    guardrail_contents.append(file_content)
                if file_part:
                    guardrail_contents.append(file_part)
                
                guard_response = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=guardrail_contents
                )
                
                guard_result = guard_response.text.strip()
                
                if "INVALID" in guard_result.upper():
                    st.error("🚫 **偵測到上傳內容可能非租屋合約或對話紀錄**\n\n本系統專門用於檢視台灣租屋合約與租賃爭議。請上傳正確的房屋租賃契約檔案或相關對話截圖，以確保分析品質！")
                else:
                    # -------------------------------------------------------------
                    # 核心合約分析 Prompt（修復標題格式，並加入個別法律援助建議區塊）
                    # -------------------------------------------------------------
                    analysis_prompt = """
                    作為您的專業台灣房地產法律顧問與合約分析師，請根據台灣內政部頒布的最新《住宅租賃定型化契約應記載及不得記載事項》以及民法、租賃專法，對上述上傳的租約或對話紀錄進行嚴格審查。
                    
                    請嚴格按照以下 Markdown 格式輸出報告（標題請使用正確的 ### 格式以確保粗體大標題正常顯示），並在「一鍵LINE談判溝通草稿」區塊前加上固定分隔標籤 `---SPLIT_HERE---`：
                    
                    ### 1. 🔴 紅燈高風險條款（違反內政部定型化契約，依法無效）
                    （條款解析內容...）
                    
                    ### 2. 🟡 黃黃燈注意事項（雖未直接違法，但對房客不利）
                    （條款解析內容...）
                    
                    ### 3. 🟢 綠燈符合規範（合法且合理的條款）
                    （條款解析內容...）

                    ### 4. ⚖️ 個別合約法律援助與行動建議
                    （針對此份合約的違法嚴重程度，提供具體後續行動建議，例如若房東拒絕修改時是否應向 1950 申訴或尋求法扶協助...）
                    
                    ---SPLIT_HERE---
                    ### 5. 💡 一鍵LINE談判溝通草稿
                    （提供一段禮貌且具說服力的 LINE 訊息草稿，讓房客可以直接複製傳給房東要求修正，此部分直接給純文字訊息內容即可，不要包在 markdown 程式碼大框中）
                    """
                    
                    analysis_contents = [analysis_prompt]
                    if file_content:
                        analysis_contents.append(file_content)
                    if file_part:
                        analysis_contents.append(file_part)
                        
                    response = client.models.generate_content(
                        model=MODEL_NAME,
                        contents=analysis_contents
                    )
                    
                    full_report = response.text
                    
                    # 智慧切割：將分析報告與談判草稿分開
                    if "---SPLIT_HERE---" in full_report:
                        report_part, draft_part = full_report.split("---SPLIT_HERE---", 1)
                    else:
                        report_part = full_report
                        draft_part = "無法自動分離草稿，請參閱上方完整報告。"
                    
                    # 顯示 AI 分析報告（包含紅綠燈與個別法律援助建議）
                    st.markdown("---")
                    st.header("2. AI 風險檢測報告")
                    st.markdown(report_part)
                    
                    # 顯示談判草稿
                    st.markdown(draft_part)
                    
                    # -------------------------------------------------------------
                    # 只針對「一鍵 LINE 談判草稿」提供乾淨的複製專區
                    # -------------------------------------------------------------
                    st.markdown("---")
                    st.subheader("📋 一鍵複製談判草稿")
                    st.info("點擊下方區塊右上角的複製按鈕，即可將專屬的 LINE 談判草稿一鍵複製，傳給房東協商：")
                    st.code(draft_part.strip(), language="text")
                    
            except Exception as e:
                st.error(f"分析過程發生錯誤: {e}")
