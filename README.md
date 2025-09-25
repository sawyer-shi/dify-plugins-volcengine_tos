# Volcengine TOS Object Storage / 火山引擎TOS对象存储

[English](#english) | [中文](#中文)

---

## English

A powerful Dify plugin providing seamless integration with Volcengine Object Storage Service (TOS). Enables direct file uploads to Volcengine TOS and efficient file retrieval using URLs, with rich configuration options.

### Version Information

- **Current Version**: v0.0.1
- **Release Date**: 2025-09-22
- **Compatibility**: Dify Plugin Framework
- **Python Version**: 3.12

#### Version History
- **v0.0.1** (2025-09-22): Initial release with file upload and retrieval capabilities, support for multiple directory structures and filename modes

### Core Features

#### File Upload to TOS
- **Direct File Upload**: Upload any file type directly to Volcengine TOS
- **Flexible Directory Structure**: Multiple storage directory organization options
  - Flat structure (no_subdirectory)
  - Hierarchical date structure (yyyy_mm_dd_hierarchy)
  - Combined date structure (yyyy_mm_dd_combined)
- **Filename Customization**: Control how filenames are stored in TOS
  - Use original filename
  - Append timestamp to original filename
- **Source File Tracking**: Automatically captures and returns the original filename
- **Smart Extension Detection**: Automatically determine file extensions based on content type

#### File Retrieval by URL
- **Direct Content Access**: Retrieve file content directly using TOS URLs
- **Cross-Region Support**: Works with all Volcengine TOS regions worldwide

### Technical Advantages

- **Secure Authentication**: Robust credential handling with support for HTTPS
- **Efficient Storage Management**: Intelligent file organization options
- **Comprehensive Error Handling**: Detailed error messages and status reporting
- **Multiple File Type Support**: Works with all common file formats
- **Rich Parameter Configuration**: Extensive options for customized workflows
- **Source File Tracking**: Preserves original filename information

### Requirements

- Python 3.12
- Volcengine TOS account with valid AccessKey credentials
- Dify Platform access
- Required Python packages (installed via requirements.txt)

### Installation & Configuration

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure the plugin in Dify with the following parameters:
   - **Endpoint**: Your Volcengine TOS endpoint (e.g., tos-cn-beijing.volces.com)
   - **Bucket Name**: Your TOS bucket name
   - **AccessKey ID**: Your Volcengine AccessKey ID
   - **AccessKey Secret**: Your Volcengine AccessKey Secret
   - **Use HTTPS**: Whether to use HTTPS for TOS requests (default: true)

### Usage

The plugin provides two powerful tools for interacting with Volcengine TOS:

#### 1. Upload File to TOS (upload_file)

Dedicated tool for uploading files to Volcengine TOS.
- **Parameters**:
  - `file`: The local file to upload (required)
  - `directory`: First-level directory under the bucket (required)
  - `directory_mode`: Optional directory structure mode (default: `no_subdirectory`)
    - `no_subdirectory`: Store directly in specified directory
    - `yyyy_mm_dd_hierarchy`: Store in date-based hierarchical structure
    - `yyyy_mm_dd_combined`: Store in combined date directory
  - `filename`: Optional custom filename for TOS storage
  - `filename_mode`: Optional filename composition mode (default: `filename`)
    - `filename`: Use original filename
    - `filename_timestamp`: Use original filename plus timestamp

#### 2. Get File by URL (get_file_by_url)

Dedicated tool for retrieving files from Volcengine TOS using URLs.
- **Parameters**:
  - `file_url`: The URL of the file in Volcengine TOS

### Examples

#### Upload File
<img width="2194" height="611" alt="upload-01" src="https://github.com/user-attachments/assets/acb73086-c647-4a52-95b7-521531e7c0bc" />
<img width="2168" height="814" alt="upload-02" src="https://github.com/user-attachments/assets/e4e84e00-31ce-401d-a5a3-aaf953072907" />
<img width="2389" height="994" alt="upload-03" src="https://github.com/user-attachments/assets/af3525c9-87b6-44a4-8d99-4b4a9d5db5f5" />




#### Get File by URL
<img width="2350" height="484" alt="download-01" src="https://github.com/user-attachments/assets/86d544a6-ec2d-48d6-9e4e-a25bec19b32f" />
<img width="1948" height="630" alt="download-02" src="https://github.com/user-attachments/assets/21669d01-d9d3-4c3c-aada-dab597da521f" />
<img width="2195" height="545" alt="download-03" src="https://github.com/user-attachments/assets/0a5e8144-990b-4d0e-a342-41ce4e996e3f" />




### Notes

- Ensure your TOS bucket has the correct permissions configured
- The plugin requires valid Volcengine credentials with appropriate TOS access permissions
- For very large files, consider using multipart upload functionality (not currently implemented)

### Developer Information

- **Author**: `https://github.com/sawyer-shi`
- **Email**: sawyer36@foxmail.com
- **License**: MIT License
- **Support**: Through Dify platform and GitHub Issues

---

## 中文

一个功能强大的 Dify 插件，提供与火山引擎对象存储服务（TOS）的无缝集成。支持将文件直接上传至 TOS，并基于 URL 高效获取文件内容，提供丰富的配置选项。

### 版本信息

- 当前版本：v0.0.1
- 发布日期：2025-09-22
- 兼容性：Dify 插件框架
- Python 版本：3.12

#### 版本历史
- v0.0.1（2025-09-22）：首个版本，包含文件上传与下载能力，支持多种目录结构与文件名模式

### 核心功能

#### 上传到 TOS
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

#### 通过 URL 获取文件
- 直接使用 TOS URL 获取文件内容
- 支持跨区域访问

### 技术优势

- 安全认证：支持 HTTPS 的安全传输
- 高效存储管理：智能的文件组织方式
- 完整错误处理：详尽的错误信息与状态上报
- 多文件类型支持：兼容常见文件格式
- 丰富参数配置：满足定制化工作流
- 源文件追踪：保留原始文件名信息

### 要求

- Python 3.12
- 火山引擎账户（有效的 AccessKey 凭据）
- Dify 平台访问权限
- 通过 requirements.txt 安装所需依赖

### 安装与配置

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

### 使用

本插件提供两个工具：

#### 1. 上传文件到 TOS（upload_file）
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

#### 2. 通过 URL 获取文件（get_file_by_url）
- 参数：
  - file_url：TOS 中文件的访问 URL

### 示例

（保留现有图片）

### 备注

- 确保 TOS 存储桶已正确配置权限
- 插件需要具备 TOS 访问权限的有效凭据
- 超大文件建议使用分片上传（当前未实现）

### 开发者信息

- 作者：https://github.com/sawyer-shi
- 邮箱：sawyer36@foxmail.com
- 许可协议：MIT License
- 支持：通过 Dify 平台与 GitHub Issues

---

**Ready to seamlessly integrate with Volcengine TOS? / 鍑嗗濂戒笌鐏北寮曟搸TOS鏃犵紳闆嗘垚浜嗗悧锛?*




