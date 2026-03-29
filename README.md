# LLM Scribe Pro v3.0.0 🎯

### 📌 简介 / Introduction
**LLM Scribe Pro** 是一款为 AI 对话打造的现代化记录与知识库管理工具。它专注本地化、隐私与核心稳定性，自动监控剪贴板，捕获并智能化管理每一次 AI 对话，是构建私有化知识资产的得力助手。

**LLM Scribe Pro** is a modern recording and knowledge base management tool designed for AI conversations. Focusing on localization, privacy, and core stability, it automatically monitors the clipboard, captures, and intelligently organizes every AI dialogue, empowering you to build private knowledge assets.

---

### 🌟 核心功能 / Key Features
- **智能速记 (Scribe Mode)**: 自动捕获剪贴板，实时同步对话记录。
- **Modern UI**: 基于 `CustomTkinter` 的现代化深色主题界面，布局清晰，响应迅速。
- **安全存储 (Secure Storage)**: 数据存储于 `%APPDATA%`，支持硬件绑定加密，100% 离线运行。
- **分层管理 (Hierarchical Org)**: 支持文件夹层级归档、拖拽式组织与会话切换。
- **独立运行 (Standalone EXE)**: 完美打包的独立可执行文件，无控制台窗口，无需 Python 环境，开箱即用。

---

### 🆕 版本重大变更 (v3.0 vs v2.0) / What's New
#### 🇨🇳 中文说明
1.  **稳定性重构与功能聚焦**：本版本移除了 v2.0 的“窗口穿透模式”，彻底解决了该高级功能带来的潜在系统兼容性问题与界面卡顿风险。我们将开发重心回归到**记录、管理与检索**的核心体验上，实现了企业级的运行稳定性。
2.  **可执行文件 (EXE) 打包强化**：针对 v2.0 的打包配置进行了深度优化，生成的 EXE 文件体积更小，启动更快，内存占用更低，且彻底杜绝了运行时控制台的意外闪现，提供纯粹的应用程序体验。
3.  **底层监听引擎再优化**：在 v2.0 基于 Win32 API 重写的引擎基础上，进一步优化了多线程调度与剪贴板内容变更检测逻辑，减少了不必要的系统调用，使后台监听更高效、对前台操作干扰更低。
4.  **数据持久化与恢复增强**：改进了 v2.0 的数据保存机制，增加了更健壮的异常处理与自动恢复流程。即使在非正常退出（如强制结束进程）后，也能最大限度地保护用户数据不丢失，并在下次启动时尝试恢复。
5.  **用户体验细节打磨**：
    *   **更流畅的界面交互**：优化了文件夹树、会话列表的加载与渲染性能。
    *   **更清晰的操作反馈**：为关键操作（如开启速记、添加标签）添加了更明确的视觉与状态提示。
    *   **更完善的数据导出**：支持单条及批量会话导出，格式更规范。

#### 🇺🇸 English Version
1.  **Stability Refactor & Focused Functionality**: This release removes the "Window Click-Through Mode" from v2.0, completely eliminating the potential system compatibility issues and UI stutter risks associated with that advanced feature. We have refocused development on the core experience of **recording, management, and retrieval**, achieving enterprise-grade runtime stability.
2.  **Enhanced Executable (EXE) Packaging**: The PyInstaller configuration from v2.0 has been deeply optimized. The resulting EXE is smaller, starts faster, uses less memory, and completely prevents the accidental flashing of a console window, delivering a pure application experience.
3.  **Core Monitoring Engine Re-optimization**: Building upon the Win32 API-based engine rewritten in v2.0, we further optimized multi-thread scheduling and clipboard change detection logic. This reduces unnecessary system calls, making background monitoring more efficient and less intrusive to foreground operations.
4.  **Enhanced Data Persistence & Recovery**: Improved upon v2.0's data-saving mechanism by adding more robust exception handling and automatic recovery workflows. User data is better protected against loss even after abnormal termination (e.g., force-closing the process), with recovery attempts on the next launch.
5.  **Polished User Experience Details**:
    *   **Smoother UI Interaction**: Optimized the loading and rendering performance of the folder tree and session list.
    *   **Clearer Operation Feedback**: Added more distinct visual and status cues for key operations (e.g., enabling Scribe Mode, adding tags).
    *   **Improved Data Export**: Supports single and batch session export with more standardized formats.

---

### 🛠️ 技术栈 / Tech Stack
- **UI**: https://github.com/TomSchimansky/CustomTkinter (Modern UI Components)
- **Core**: Python 3.9+, https://docs.python.org/3/library/ctypes.html (Windows API)
- **Security**: https://github.com/pyca/cryptography (PBKDF2 + Fernet)
- **Build**: https://www.pyinstaller.org/ (`LLMScribePro.spec`)

---

### 📦 安装与运行 / Installation & Usage
#### 对于最终用户 / For End Users
1.  前往 https://github.com/yourusername/llm-scribe-pro/releases 页面下载 `LLM_Scribe_Pro_v3.0.0.exe`。
2.  双击运行即可，所有数据将自动存储于您的 `%APPDATA%` 目录。

#### 对于开发者 / For Developers
```powershell
# 克隆仓库并进入目录
git clone https://github.com/yourusername/llm-scribe-pro.git
cd llm-scribe-pro

# 安装依赖
pip install -r requirements.txt

# 运行程序
python app.py

# （可选）使用优化配置打包 EXE
python build_exe.py
# 或直接使用 PyInstaller
pyinstaller LLMScribePro.spec
```

---

### 📁 项目结构 / Project Structure (v3.0)
```
LLM_Scribe_Pro/
├── app.py                      # 应用程序主入口
├── core/                       # 核心逻辑模块
│   ├── __init__.py
│   ├── clipboard_monitor.py    # 基于 Win32 API 的剪贴板监听引擎
│   ├── data_manager.py         # 数据持久化与加密管理
│   ├── session_manager.py      # 会话与文件夹逻辑
│   └── text_sanitizer.py       # 文本清洗与格式化
├── ui/                         # 用户界面模块
│   ├── __init__.py
│   ├── main_window.py          # 主窗口类
│   ├── widgets/                # 自定义控件
│   └── styles.py               # 主题与样式定义
├── utils/                      # 工具函数
│   ├── __init__.py
│   ├── logger.py               # 日志系统
│   └── helpers.py              # 通用助手函数
├── build_exe.py                # EXE 打包脚本
├── LLMScribePro.spec           # PyInstaller 打包配置文件
└── requirements.txt            # Python 依赖列表
```

---

### 🔧 配置与数据 / Configuration & Data
- **配置文件路径**: `%APPDATA%\LLM Scribe Pro\config.json`
- **数据存储路径**: `%APPDATA%\LLM Scribe Pro\data\`
- **日志文件路径**: `%APPDATA%\LLM Scribe Pro\logs\`

**⚠️ 注意 / Note**: 首次运行 v3.0 时会自动检测并迁移 v2.0 的用户数据。建议在升级前手动备份 `%APPDATA%\LLM Scribe Pro\` 目录。

---

### 📄 许可证 / License
本项目基于 LICENSE 开源。

---

**让每一次 AI 对话都成为可追溯、可管理的知识资产。**  
**Turn every AI conversation into a traceable, manageable knowledge asset.**