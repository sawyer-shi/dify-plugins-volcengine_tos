def get_content_type_by_extension(extension: str) -> str:
    """
    根据文件扩展名获取内容类型(MIME类型)
    
    Args:
        extension (str): 文件扩展名，例如 '.jpg', '.png' 等
    
    Returns:
        str: 对应的MIME类型，如果未找到则返回 'application/octet-stream'
    """
    # 常见文件扩展名到MIME类型的映射
    content_type_map = {
        # 图片类型
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.bmp': 'image/bmp',
        '.webp': 'image/webp',
        '.svg': 'image/svg+xml',
        '.ico': 'image/x-icon',
        
        # 文档类型
        '.txt': 'text/plain',
        '.pdf': 'application/pdf',
        '.doc': 'application/msword',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.xls': 'application/vnd.ms-excel',
        '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        '.ppt': 'application/vnd.ms-powerpoint',
        '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
        
        # 音频类型
        '.mp3': 'audio/mpeg',
        '.wav': 'audio/wav',
        '.ogg': 'audio/ogg',
        '.flac': 'audio/flac',
        
        # 视频类型
        '.mp4': 'video/mp4',
        '.avi': 'video/x-msvideo',
        '.mov': 'video/quicktime',
        '.wmv': 'video/x-ms-wmv',
        '.flv': 'video/x-flv',
        '.mkv': 'video/x-matroska',
        
        # 压缩文件
        '.zip': 'application/zip',
        '.rar': 'application/vnd.rar',
        '.7z': 'application/x-7z-compressed',
        '.tar': 'application/x-tar',
        '.gz': 'application/gzip',
        
        # 代码文件
        '.py': 'text/x-python',
        '.js': 'application/javascript',
        '.css': 'text/css',
        '.html': 'text/html',
        '.htm': 'text/html',
        '.xml': 'application/xml',
        '.json': 'application/json',
        
        # 其他常见类型
        '.csv': 'text/csv',
        '.rtf': 'application/rtf',
    }
    
    # 转换为小写并查找对应的MIME类型
    extension = extension.lower()
    return content_type_map.get(extension, 'application/octet-stream')