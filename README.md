# 🛡️ RentGuard AI - 租屋合約智能守護系統

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Framework-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![Google GenAI SDK](https://img.shields.io/badge/AI-Gemini%203.5%20Flash%20Lite-8E75C2.svg)](https://ai.google.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

專為台灣租屋族設計的 AI 法律顧問與合約審查系統。透過 Google Gemini 模型與內政部《住宅租賃定型化契約應記載及不得記載事項》進行法規比對，自動檢測不平等條款與違法霸王條款，並一鍵生成得體且堅定的 LINE 談判溝通草稿。

---

## ✨ 核心特色

- **多模態檔案支援**：
  - 支援 **PDF 合約**、**純文字合約 (.txt)**。
  - 支援 **圖片格式（PNG / JPG / JPEG）**，可直接上傳合約相片或房東對話截圖進行視覺分析。
- **智慧前置防護（Guardrails）**：
  - 自動檢驗並過濾非租屋相關內容，確保合約分析精準度。
- **三段式風險燈號分類（JSON 結構化輸出）**：
  - 🔴 **高風險違法條文（紅燈）**：標記明顯違反法規、損害房客合法權益的條款（如苛扣押金、轉嫁修繕責任等）。
  - 🟡 **潛在不利條文（黃燈）**：辨識未直接違法但責任顯失衡平的風險條文。
  - 🟢 **合規條文（綠燈）**：標示符合內政部定型化契約之條文。
- **💬 擬真 LINE 談判草稿生成**：
  - 自動依據紅黃燈爭議點，生成語氣禮貌、依據明確且立場堅定的溝通範本，支援一鍵快速複製。
- **現代化深色儀表板**：
  - 基於 Streamlit 客製化樣式，提供直觀的卡片式分類與聊天室預覽介面。

---

## 🛠️ 技術棧 (Tech Stack)

- **核心語言**：Python 3.10+
- **前端介面**：[Streamlit](https://streamlit.io/)
- **AI 模型**：Google Gemini 3.5 Flash Lite (google-genai 官方 SDK)
- **文件處理**：pypdf（PDF 文字提取）
- **環境設定**：python-dotenv

---

## 🚀 快速開始

### 1. 取得專案原始碼

    git clone https://github.com/bensonchen07/rentguard-ai.git
    cd rentguard-ai

### 2. 建立並啟用虛擬環境

Windows:

    python -m venv venv
    venv\Scripts\activate

macOS / Linux:

    python3 -m venv venv
    source venv/bin/activate

### 3. 安裝相依套件

    pip install -r requirements.txt

(若尚未建立 requirements.txt，可直接執行：pip install streamlit google-genai python-dotenv pypdf)

### 4. 設定環境變數

在專案根目錄建立 .env 檔案：

    GEMINI_API_KEY=你的_GEMINI_API_KEY

> 💡 可至 [Google AI Studio](https://aistudio.google.com/) 取得免費的 Gemini API Key。

### 5. 啟動應用程式

    streamlit run app.py

啟動後，瀏覽器會自動開啟 http://localhost:8501。

---

## 📁 專案結構

    rentguard-ai/
    ├── app.py              # 主程式 (Streamlit 介面與 Gemini API 呼叫邏輯)
    ├── .env.example        # 環境變數設定範本 (不含真實金鑰)
    ├── .gitignore          # Git 忽略名單 (.env, venv/, __pycache__ 等)
    ├── requirements.txt    # 專案相依套件清單
    └── README.md           # 專案說明文件

---

## ⚖️ 法律免責聲明 (Disclaimer)

本系統所產出之 AI 分析結果與談判溝通建議僅供一般性參考，**不構成任何形式的正式法律意見或訴訟保證**。

若面臨重大租賃糾紛，建議洽詢以下專業管道：
- 📞 **消費者服務專線**：手機或市話直撥 1950
- ⚖️ **財團法人法律扶助基金會**：提供平民法律諮詢與協助
- 🏠 **內政部不動產資訊平臺**：查詢最新版定型化契約範本

---

## 📄 授權條款 (License)

本專案採用 [MIT License](LICENSE) 授權開放。

