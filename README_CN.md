# 火山引擎TOS对象存储

一个功能强大的 Dify 插件，提供与火山引擎对象存储服务（TOS）的无缝集成。支持将文件直接上传至 TOS，并基于 URL 高效获取文件内容，提供丰富的配置选项。

## 版本信息

- 当前版本：v0.0.1
- 发布日期：2025-09-22
- 兼容性：Dify 插件框架
- Python 版本：3.12

## 快速开始
1. 从 Dify 市场下载 `volcengine_tos` 插件。
2. 配置 Volcengine TOS 的授权信息。
3. 完成上述配置就能马上使用该插件了。

### 版本历史
- v0.0.1（2025-09-22）：首个版本，包含文件上传与下载能力，支持多种目录结构与文件名模式

## 核心功能

### 上传到 TOS
- 直接上传任意类型文件到火山引擎 TOS
- 灵活的目录结构：
  - 无子目录（no_subdirectory）
  - 分层日期结构（yyyy_mm_dd_hierarchy）
  - 合并日期结构（yyyy_mm_dd_combined）
- 文件名自定义：
  - 使用原始文件名
  - 原始文件名追加时间戳
- 源文件追踪：自动记录并返回原始文件名
- 智能扩展名识别：根据内容类型自动判断扩展名

### 通过 URL 获取文件
- 直接使用 TOS URL 获取文件内容
- 支持跨区域访问

## 技术优势

- 安全认证：支持 HTTPS 的安全传输
- 高效存储管理：智能的文件组织方式
- 完整错误处理：详尽的错误信息与状态上报
- 多文件类型支持：兼容常见文件格式
- 丰富参数配置：满足定制化工作流
- 源文件追踪：保留原始文件名信息

## 要求

- Python 3.12
- 火山引擎账户（有效的 AccessKey 凭据）
- Dify 平台访问权限
- 通过 requirements.txt 安装所需依赖

## 安装与配置

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 在 Dify 中配置插件，填写以下参数：
- Endpoint：你的 TOS 访问域名（如：tos-cn-beijing.volces.com）
- Bucket Name：TOS 存储桶名称
- AccessKey ID：火山引擎 AccessKey ID
- AccessKey Secret：火山引擎 AccessKey Secret
- Use HTTPS：是否使用 HTTPS（默认：true）

## 使用

本插件提供三个工具：

### 1. 上传文件到 TOS（upload_file）
- 参数：
  - file（必填）：需要上传的本地文件
  - directory（可选）：存储桶下的一级目录（为空表示根目录）
  - directory_mode（可选，默认：no_subdirectory）：目录结构模式
    - no_subdirectory：直接存储在指定目录或根目录
    - yyyy_mm_dd_hierarchy：按日期分层存储
    - yyyy_mm_dd_combined：按日期合并目录存储
  - filename（可选）：自定义 TOS 存储文件名
  - filename_mode（可选，默认：filename）：文件名组合模式
    - filename：使用原始文件名
    - filename_timestamp：原始文件名追加时间戳

### 2. 批量上传文件到 TOS（multi_upload_files）
- 参数：
  - files（必填）：需要上传的本地文件列表（最多10个文件）
  - directory（可选）：存储桶下的一级目录（为空表示根目录）
  - directory_mode（可选，默认：no_subdirectory）：目录结构模式
    - no_subdirectory：直接存储在指定目录或根目录
    - yyyy_mm_dd_hierarchy：按日期分层存储
    - yyyy_mm_dd_combined：按日期合并目录存储
  - filename_mode（可选，默认：filename）：文件名组合模式
    - filename：使用原始文件名
    - filename_timestamp：原始文件名追加时间戳

### 3. 通过 URL 获取文件（get_file_by_url）
- 参数：
  - file_url：TOS 中文件的访问 URL

## 示例

### 上传文件
<img width="2066" height="1034" alt="upload-01" src="https://github.com/user-attachments/assets/36efab38-aaca-4a51-938c-26daa791f4a0" />

### 批量上传文件
<img width="2040" height="736" alt="upload-02" src="https://github.com/user-attachments/assets/178410d5-bfc4-4b9a-83ac-1c7a12159323" />

### 获取(下载)文件
<img width="2231" height="645" alt="download-01" src="https://github.com/user-attachments/assets/1bd2c648-a30b-45a3-9fed-d0ed362390b6" />
<img width="2131" height="564" alt="download-02" src="https://github.com/user-attachments/assets/9ebcdd32-efde-4908-b702-9eccfee66d44" />

## 备注

- 确保 TOS 存储桶已正确配置权限
- 插件需要具备 TOS 访问权限的有效凭据
- 超大文件建议使用分片上传（当前未实现）

## 开发者信息

- 作者：https://github.com/sawyer-shi
- 源码：`https://github.com/sawyer-shi/dify-plugins-volcengine_tos`
- 邮箱：sawyer36@foxmail.com
- 许可协议：MIT License
- 支持：通过 Dify 平台与 GitHub Issues

---

**准备好与火山引擎TOS无缝集成了吗？**