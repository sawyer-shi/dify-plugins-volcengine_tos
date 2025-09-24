# Volcengine TOS Plugin / 火山引擎TOS插件

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

一个功能强大的Dify插件，提供与火山引擎对象存储服务（TOS）的无缝集成。支持将文件直接上传到火山引擎TOS，并使用URL高效检索文件，提供丰富的配置选项。

### 版本信息

- **当前版本**: v0.0.1
- **发布日期**: 2025-09-22
- **兼容性**: Dify Plugin Framework
- **Python版本**: 3.12

#### 版本历史
- **v0.0.1** (2025-09-22): 初始版本，支持文件上传和检索功能，支持多种目录结构和文件名模式

### 核心特性

#### 文件上传至TOS
- **直接文件上传**: 将任何类型的文件直接上传到火山引擎TOS
- **灵活的目录结构**: 多种存储目录组织选项
  - 扁平结构 (no_subdirectory)
  - 分层日期结构 (yyyy_mm_dd_hierarchy)
  - 合并日期结构 (yyyy_mm_dd_combined)
- **文件名自定义**: 控制文件在TOS中的存储名称
  - 使用原始文件名
  - 在原始文件名后附加时间戳
- **源文件追踪**: 自动捕获并返回原始文件名
- **智能扩展名检测**: 基于内容类型自动确定文件扩展名

#### 通过URL获取文件
- **直接内容访问**: 使用TOS URL直接检索文件内容
- **跨区域支持**: 适用于全球所有火山引擎TOS区域

### 技术优势

- **安全认证**: 强大的凭证处理，支持HTTPS
- **高效存储管理**: 智能文件组织选项
- **全面的错误处理**: 详细的错误消息和状态报告
- **多种文件类型支持**: 适用于所有常见文件格式
- **丰富的参数配置**: 用于自定义工作流程的广泛选项
- **源文件追踪**: 保留原始文件名信息

### 要求

- Python 3.12
- 具有有效AccessKey凭证的火山引擎TOS账户
- Dify平台访问权限
- 所需的Python包（通过requirements.txt安装）

### 安装与配置

1. 安装所需依赖：
   ```bash
   pip install -r requirements.txt
   ```

2. 在Dify中配置插件，输入以下参数：
   - **Endpoint**: 您的火山引擎TOS端点（例如：tos-cn-beijing.volces.com）
   - **Bucket Name**: 您的TOS存储桶名称
   - **AccessKey ID**: 您的火山引擎AccessKey ID
   - **AccessKey Secret**: 您的火山引擎AccessKey Secret
   - **Use HTTPS**: 是否使用HTTPS进行TOS请求（默认：true）

### 使用方法

该插件提供两个强大的工具用于与火山引擎TOS交互：

#### 1. 上传文件至TOS (upload_file)

用于将文件上传到火山引擎TOS的专用工具。
- **参数**:
  - `file`: 要上传的本地文件（必填）
  - `directory`: 存储桶下的一级目录（必填）
  - `directory_mode`: 可选的目录结构模式（默认：`no_subdirectory`）
    - `no_subdirectory`: 直接存储在指定目录中
    - `yyyy_mm_dd_hierarchy`: 存储在基于日期的分层结构中
    - `yyyy_mm_dd_combined`: 存储在合并日期目录中
  - `filename`: 用于TOS存储的可选自定义文件名
  - `filename_mode`: 可选的文件名组成模式（默认：`filename`）
    - `filename`: 使用原始文件名
    - `filename_timestamp`: 使用原始文件名加上时间戳

#### 2. 通过URL获取文件 (get_file_by_url)

用于使用URL从火山引擎TOS检索文件的专用工具。
- **参数**:
  - `file_url`: 火山引擎TOS中文件的URL

### 示例

#### 上传文件 
<img width="2194" height="611" alt="upload-01" src="https://github.com/user-attachments/assets/0210fda6-02d3-4443-8f27-6504060dbdf1" />
<img width="2168" height="814" alt="upload-02" src="https://github.com/user-attachments/assets/a8762f03-39dd-423d-84e7-eb7f190961de" />
<img width="2389" height="994" alt="upload-03" src="https://github.com/user-attachments/assets/290e627e-ed95-4798-9b85-368ed2629088" />




#### 通过URL获取文件
<img width="2350" height="484" alt="download-01" src="https://github.com/user-attachments/assets/7f231651-eab3-432f-a0b3-b69bee87ca51" />
<img width="1948" height="630" alt="download-02" src="https://github.com/user-attachments/assets/f6170547-8399-48a7-9e34-a681f8b8718e" />
<img width="2195" height="545" alt="download-03" src="https://github.com/user-attachments/assets/929c23c8-881d-42e8-927f-74921aa023f9" />





### 注意事项

- 确保您的TOS存储桶配置了正确的权限
- 该插件需要具有适当TOS访问权限的有效火山引擎凭证
- 对于非常大的文件，请考虑使用分片上传功能（目前未实现）

### 开发者信息

- **作者**: `https://github.com/sawyer-shi`
- **邮箱**: sawyer36@foxmail.com
- **许可证**: MIT License
- **源码地址**: `https://github.com/sawyer-shi/dify-plugins-volcengine_tos`
- **支持**: 通过Dify平台和GitHub Issues

---

**Ready to seamlessly integrate with Volcengine TOS? / 准备好与火山引擎TOS无缝集成了吗？**



