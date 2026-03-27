# llm-sidebar-anchor
# LLM Scribe Pro

一个专为大语言模型（LLM）对话设计的本地化、隐私优先的剪贴板记录与知识库管理工具。它拥有现代化的深色主题界面，能够自动监听剪贴板内容，帮助你高效地整理、归档和回溯与 AI 的每一次对话。

LLM Scribe Pro is a localized, privacy-first clipboard logging and knowledge base management tool designed specifically for Large Language Model (LLM) interactions. Featuring a modern dark theme interface, it automatically monitors clipboard content, helping you efficiently organize, archive, and review every AI conversation.

---

## 核心特性 (Core Features)

*   **自动速记模式 (Auto-Scribe Mode)**: 开启后自动监听剪贴板，一旦复制新内容即刻追加到当前会话，无需手动粘贴。
*   **文件夹层级管理 (Hierarchical Folder Management)**: 支持创建文件夹（归档），将会话按主题分类（如“编程”、“写作”、“翻译”），保持知识库井井有条。
*   **智能摘要锚点 (Smart Summary Anchors)**: 选中关键文本一键生成“标签”，双击标签即可瞬间跳转回原文位置，方便在长对话中快速定位。
*   **窗口叠加与穿透模式 (Window Overlay & Click-Through Mode)**: 支持窗口透明度调节与“点击穿透”。您可以让窗口半透明悬浮在其他应用之上，一边工作一边记录，互不干扰。
*   **本地数据安全 (Local Data Security)**: 所有数据以 JSON 格式保存在本地，支持自定义存储路径和单条会话导出，完全离线运行，保障隐私。
*   **现代化深色界面 (Modern Dark UI)**: 采用专业、护眼的深色主题设计，视觉体验舒适，适合长时间专注工作。

---

## 界面预览 (UI Preview)

界面采用经典的深色配色方案，布局清晰，分为三个主要区域：
*   **左侧导航栏 (Left Sidebar)**: 目录树，用于管理所有文件夹和会话。
*   **中央编辑区 (Center Editing Area)**: 主工作区，显示和编辑会话内容，实时显示捕获的文本。
*   **右侧摘要面板 (Right Summary Panel)**: 显示当前会话的所有“标签”（摘要锚点），支持快速导航。

---

## 技术栈 (Tech Stack)

*   **开发语言 (Language)**: Python 3.x
*   **GUI 框架 (GUI Framework)**: Tkinter (Python 标准库)
*   **系统 API (System API)**: Windows API (通过 ctypes 调用) - 用于实现窗口穿透和透明度控制
*   **数据存储 (Data Storage)**: JSON

---

## 安装与运行 (Installation & Run)

本项目基于 Python 标准库开发，无需安装任何第三方依赖，开箱即用。

1.  **获取代码 (Get the Code)**
    将主程序文件保存为 `llm_scribe_modern.py`。

2.  **运行程序 (Run the Application)**
    在终端或命令行中，导航到文件所在目录并执行：
    ```bash
    python llm_scribe_modern.py
    ```

3.  **首次使用 (First Run)**
    *   程序会在运行目录下自动生成 `llm_scribe_data.json` 作为核心数据库文件。
    *   您可以点击顶部的 **路径 (Path)** 按钮更改数据文件的保存位置。

---

## 使用指南 (User Guide)

### 1. 开始速记 (Start Scribing)
点击顶部工具栏的 **🚀 速记 (Scribe) OFF** 按钮，将其切换为 **ON** 状态。此后，在任何地方（例如从 ChatGPT、代码编辑器、网页）复制文本，内容都会自动带时间戳添加到当前激活的会话中。

### 2. 管理知识与会话 (Manage Knowledge & Sessions)
*   **新建会话 (New Session)**: 点击左侧导航栏底部的 **+ 新建 (New)** 按钮。
*   **创建文件夹 (Create Folder)**: 点击 **📁 归档 (Folder)** 按钮创建分类文件夹。
*   **组织内容 (Organize)**: 在左侧树状图中，通过右键菜单的“移动到 (Move to Folder)”选项，将会话拖入文件夹进行归类。
*   **导出数据 (Export)**: 在左侧列表右键点击会话，选择“导出此会话 (Export Session)”，可将其单独导出为 JSON 或 TXT 格式。

### 3. 使用标签导航 (Navigate with Tags)
*   **添加标签 (Add Tag)**:
    *   在右侧面板的输入框中输入描述，点击 **➕ 添加标记 (Add Tag)**。
    *   **快捷方式**: 在中央编辑区选中一段文本，右键选择 **🔖 设为摘要 (Tag as Summary)**，可直接用选中文本创建标签。
*   **快速跳转 (Quick Jump)**: 在右侧标签列表中双击任一标签，编辑区将自动滚动并高亮显示对应的原文行。

### 4. 启用叠加模式 (Enable Overlay Mode)
1.  勾选顶部工具栏的 **👻 穿透 (Click-Through)** 复选框。
2.  使用旁边的滑块降低窗口 **透明度 (Opacity)**。
3.  此时窗口将变为半透明且允许鼠标点击“穿透”到后方应用程序，实现无干扰的悬浮记录。

---

## 文件说明 (File Description)

| 文件名 (File Name) | 描述 (Description) |
| :--- | :--- |
| `llm_scribe_modern.py` | 主程序源代码文件。 |
| `llm_scribe_data.json` | 核心数据库文件，包含所有会话、文件夹和标签数据。程序自动生成。 |
| `scribe_config.json` | 配置文件，记录用户自定义的数据文件存储路径。程序自动生成。 |

---

## 安全与隐私 (Security & Privacy)

*   **输入清洗 (Input Sanitization)**: 程序会自动过滤剪贴板内容中的不可打印字符，防止数据污染和潜在的格式错误。
*   **路径安全 (Path Safety)**: 包含安全检查，禁止将数据文件保存为可执行文件扩展名（如 `.exe`, `.bat` 等），防止误操作。
*   **完全离线 (Fully Offline)**: 程序无需网络连接，所有操作和数据处理均在本地计算机上进行，确保您的对话内容隐私绝对安全。

---

## 更新日志 (Changelog)

*   **v2.0**: 重构了数据结构，支持文件夹层级管理；增加了自定义数据文件路径功能；增强了输入安全性处理。
*   **v1.0**: 初始版本，实现了基础的剪贴板监听与内容记录功能。

---

## 许可证 (License)

本项目基于 LICENSE 开源。