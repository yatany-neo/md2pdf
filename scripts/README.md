# Scripts Directory

这个目录包含了Markdown到PDF转换的核心脚本。

## 文件说明

### `final_clickable_toc.py` (推荐使用)
**主要PDF转换脚本**，具有以下特性：

- **中文支持**：完美支持中文字符显示
- **可点击目录**：PDF内目录支持点击跳转
- **侧栏书签**：PDF侧边栏显示可点击的书签
- **格式优化**：段落缩进、列表间距等格式优化
- **特殊字符处理**：正确处理标题中的特殊字符
- **稳定性**：经过充分测试，可靠性高
- **适用场景**：无emoji的正式文档转换

### `final_clickable_toc_emoji_simple.py` (备用)
**简化版emoji清理转换器**，具有以下特性：

- **emoji清理**：智能清理常见emoji字符
- **Markdown保护**：保护粗体、斜体等Markdown语法
- **简化处理**：避免复杂的正则表达式处理
- **适用场景**：包含emoji的文档转换
- **注意事项**：相比稳定版，处理逻辑稍复杂

## 使用方法

### 推荐使用 (无emoji文档)
```bash
python3 final_clickable_toc.py [markdown文件路径]
```

### 备用使用 (含emoji文档)
```bash
python3 final_clickable_toc_emoji_simple.py [markdown文件路径]
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

### `final_clickable_toc.py` (稳定版)
- **v12**: 修复标题中 & 字符显示问题
- **v11**: 添加段落缩进优化
- **v10**: 修复标题转义问题
- **v7**: 稳定的目录功能版本
- **v6**: 列表格式优化
- **v5**: 文本截断修复
- **v4**: 格式一致性优化
- **v3**: 目录编号优化
- **v2**: 中文显示优化

### `final_clickable_toc_emoji_simple.py` (简化版)
- **v1**: 简化emoji清理，避免复杂处理
- **特性**: 智能清理常见emoji，保护Markdown语法
- **适用**: 包含emoji的文档转换

## 选择建议

**推荐使用 `final_clickable_toc.py`**：
- 文档不包含emoji
- 需要最高稳定性
- 正式文档转换

**备用使用 `final_clickable_toc_emoji_simple.py`**：
- 文档包含emoji
- 需要清理emoji显示
- 可以接受稍复杂的处理逻辑
