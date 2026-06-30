# 📋 ADAD (Architecture-Driven Agentic Development) 開發規範與工具鏈

本專案是一個專為 **Antigravity AI Agent** 設計的 Workspace Customization 擴充套件，旨在實行 **ADAD (架構驅動型智能體開發)** 開發模式。

ADAD 的核心理念是：**將「系統設計（架構）」與「程式碼實作（邏輯）」徹底解耦**。由人類把持高價值的架構與驗收 Checkpoint，並指派 Agent 在最小 Context 的約束下進行高精度的原子程式碼生成，以防範 AI 開發中的架構失控與 Context 膨脹問題。

在最新升級中，本專案引進了 **三層架構事實流（Architecture Source ➔ Compile ➔ Architecture IR ➔ Code）**，全面支援**逐步展開（Architecture Growth）**的新工作流。

---

## 📐 三層事實流架構

```
    Human Intent
         ↓
  system_map.md          (Architecture Source) ➔ 人類與 Agent 共同設計，支援逐步展開、TODO、決策記錄等
         ↓
      Compile            (compile_map.py)      ➔ 自動進行格式驗證、生命週期狀態繼承與 dirty 判定
         ↓
  system_map.yaml        (Architecture IR)     ➔ 僅供 Agent 讀取上下文與執行工具，禁止人工編輯
         ↓
  Code Generation        (Implementation)      ➔ 依據 YAML (IR) 產生高質量的原子代碼
```

*   **system_map.md (Architecture Source)**：專為人類與 Agent 協同設計的 Markdown 文件。支援 TODO、Checkpoint、Design Decision、Alternative 等內容。允許暫存、未完成與逐步擴充。
*   **system_map.yaml (Architecture IR)**：完全由編譯器（Compiler）從 Markdown 產生的中間表示檔。用途只有 Context 載入、DAG 依賴分析、Rule of Two 正規化檢查與狀態機執行，**嚴禁人工直接編輯**。
*   **若 Markdown 與 YAML 內容不一致或更新時間不合，工具鏈將自動阻斷代碼生成並提示重新 Compile。**

---

## 📂 專案目錄結構

```
programming_design/
├── .agents/                      # Workspace Customizations 根目錄
│   ├── AGENTS.md                 # Antigravity Rules (定義四大全局規則與 CP 決策限制)
│   └── skills/                   # 自訂 Skills
│       └── adad-workflow/        # ADAD 輔助工具技能
│           ├── SKILL.md          # Skill 定義與 Antigravity 調用引導
│           └── scripts/          # Antigravity 藉由 run_command 執行的輔助 Python 腳本
│               ├── adad_core.py  # 核心引擎 (Markdown 解析、IR 讀寫、DAG 分析、過期阻斷)
│               ├── compile_map.py # [NEW] Architecture Compiler (Markdown ➔ YAML 狀態合併)
│               ├── resume_analysis.py # [NEW] Resume 分析器 (進度統計與智能下一步建議)
│               ├── read_context.py
│               ├── check_normalization.py
│               ├── analyze_cascade.py
│               ├── transit_state.py
│               ├── verify_implementation.py # 實作校驗器 (驗證 Verification 條件如斷言)
│               └── check_invariants.py # Invariants 校驗器 (驗證靜態 AST 導入約束)
├── checkpoints/                  # Checkpoint 決策歷史存檔目錄 (CP-X-XXX.yaml)
├── system_map.md                 # [NEW] 專案架構唯一事實來源 (SSOT - Architecture Source)
├── system_map.yaml               # 專案架構中間表示檔 (SSOT - Architecture IR)
├── 程式開發規範.md               # 人類閱讀的詳細規範說明書
├── install.py                    # 安裝、初始化與打包指令腳本
└── README.md                     # 本說明文件
```

---

## 🛠️ 快速開始

### 1. 初始化與安裝
在專案目錄下執行：
```bash
python install.py init
```
這會初始化 `checkpoints/` 目錄、`system_map.md` 初始架構、`system_map.yaml` 以及 docs 目錄（包括 ADR 與 Patterns）。

### 2. 架構編譯 (Markdown ➔ YAML)
當修改了 `system_map.md` 後，請執行以下指令將其編譯為中間表示 YAML：
```bash
python .agents/skills/adad-workflow/scripts/compile_map.py
```
*Compiler 會比對新舊結構：若模組的 input/output/dependencies 結構未變，將自動繼承舊 YAML 中的生命週期狀態；若有結構性修改，狀態會被智慧重置為 `dirty`。*

### 3. 進度與思路重啟 (Resume)
若在中途重新接手專案，或人類需要了解當前架構進度，可執行：
```bash
python .agents/skills/adad-workflow/scripts/resume_analysis.py
```
*這會輸出詳細的已完成模組、待辦 TODO 項目、未完成 Checkpoint，並根據 DAG 拓撲分析，智能推薦「下一個最合理設計的模組」。*

---

## 🔄 ADAD 核心 CLI 工具說明

| 工具腳本 | 功能說明 | 調用時機 |
| :--- | :--- | :--- |
| `compile_map.py` | 編譯 `system_map.md` ➔ `system_map.yaml` | 修改 Markdown 架構源後首要執行 |
| `resume_analysis.py` | 分析架構 TODO 與智能推薦下一步 | 開發重啟、或人類要求進度概覽時執行 |
| `read_context.py` | 讀取單一節點最小上下文 (已包含 ADR & 模式注入) | Phase 2 開始編寫代碼前，獲取目標簽章 |
| `check_normalization.py` | 執行 Rule of Two 檢查 | Phase 1 架構規劃期，檢測是否重複造輪子 |
| `analyze_cascade.py` | 執行髒點依賴分析 (DAG 走查) | Phase 3 反向同步，架構變更時級聯標記 `dirty` |
| `transit_state.py` | 推進/變更模組生命週期狀態 | CP 審查通過、Lint 通過或被退回時更新狀態 |
| `verify_implementation.py` | 執行代碼實現驗證條件（如 assert）校驗 | 原子代碼生成完畢後進行自檢驗證 |
| `check_invariants.py` | 執行不變量約束（如 deny_imports）校驗 | 原子代碼生成完畢後進行靜態 AST 檢查 |

---

## 🔄 ADAD 人機協作工作流 (逐步展開 - Architecture Growth)

架構不再是一次性全部生成，而是採取「小步前進」的方式：
1. **Human 描述核心需求**。
2. **Agent 建立 `system_map.md` 初始骨架**（仅限 Domain 級別）。➔ 進行 **CP-1** 審查。
3. **人類與 Agent 逐步擴充下一層**：
   * Domain ➔ Subsystem ➔ **CP-1**
   * Subsystem ➔ Module ➔ **CP-1**
   * Module ➔ Interface (Input/Output) ➔ **CP-1**
   * Interface ➔ Invariants & Pattern Constraints ➔ **CP-1**
4. **執行 Compile 編譯產生 `system_map.yaml` (IR)**。
5. **Phase 2: 原子生成**：系統對每一節點使用 `read_context.py` 讀取最小上下文，進行代碼編寫，並自動執行 Invariants 與 Verification 校驗。➔ 進行 **CP-2** 審查與 Deployed 推進。
6. **Phase 3: 反向同步**：若實作期發現架構缺陷，修改 `system_map.md` 後重新 Compile，被波及的依賴節點將自動標記為 `dirty` 並重回 Phase 2。
