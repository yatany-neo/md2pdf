# Scripts Directory

这个目录包含了Markdown到PDF转换的核心脚本。

## 文件说明

### `final_clickable_toc.py`
主要的PDF转换脚本，具有以下特性：

- **中文支持**：完美支持中文字符显示
- **可点击目录**：PDF内目录支持点击跳转
- **侧栏书签**：PDF侧边栏显示可点击的书签
- **格式优化**：段落缩进、列表间距等格式优化
- **特殊字符处理**：正确处理标题中的特殊字符

## 使用方法

### 基本使用
```bash
python3 final_clickable_toc.py
```

### 自定义转换
```python
from final_clickable_toc import build

# 转换单个文件
build('path/to/input.md', 'path/to/output.pdf')

# 使用默认输出路径
build('path/to/input.md')
```

## 环境要求

- Python 3.8+
- Pandoc
- XeLaTeX (MacTeX)

## 技术细节

### 主要功能
1. **预处理Markdown**：确保列表格式正确
2. **LaTeX模板注入**：通过header-includes注入自定义样式
3. **Pandoc调用**：使用XeLaTeX引擎生成PDF
4. **临时文件清理**：自动清理生成的临时文件

### 关键特性
- 使用 `xeCJK` 包支持中文
- 使用 `hyperref` 包实现可点击链接
- 使用 `enumitem` 包优化列表格式
- 自定义 `\@maketitle` 处理特殊字符
- 优化段落缩进和间距

## 版本历史

- **v12**: 修复标题中 & 字符显示问题
- **v11**: 添加段落缩进优化
- **v10**: 修复标题转义问题
- **v7**: 稳定的目录功能版本
- **v6**: 列表格式优化
- **v5**: 文本截断修复
- **v4**: 格式一致性优化
- **v3**: 目录编号优化
- **v2**: 中文显示优化
