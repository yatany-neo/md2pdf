# Markdown to PDF Converter

一个高质量的Markdown到PDF转换工具，专门优化中文文档的显示效果。

## 功能特点

- ✅ **中文支持**：完美支持中文字符显示和换行
- ✅ **可点击目录**：PDF内目录支持点击跳转
- ✅ **侧栏书签**：PDF侧边栏显示可点击的书签
- ✅ **格式优化**：段落缩进、列表间距、行距等格式优化
- ✅ **特殊字符处理**：正确处理标题中的特殊字符（如 & 符号）
- ✅ **目录编号**：自动生成目录编号，避免重复

## 环境要求

- Python 3.8+
- Pandoc
- XeLaTeX (MacTeX)

## 安装依赖

### 安装 Homebrew (macOS)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 安装 Pandoc 和 MacTeX
```bash
brew install pandoc
brew install --cask mactex
```

### 刷新环境变量
```bash
eval "$(/usr/libexec/path_helper)"
```

## 使用方法

### 基本使用
```bash
cd scripts
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

## 项目结构

```
AgentMarketplace/
├── scripts/
│   └── final_clickable_toc.py    # 主要转换脚本
├── docs/
│   └── score_doc/                # Markdown源文件
├── pdf_docs/                     # PDF输出目录（被git忽略）
├── .gitignore                    # Git忽略规则
└── README.md                     # 项目说明
```

## 技术细节

### LaTeX模板特性
- 使用 `xeCJK` 包支持中文
- 使用 `hyperref` 包实现可点击链接
- 使用 `enumitem` 包优化列表格式
- 自定义 `\@maketitle` 处理特殊字符
- 优化段落缩进和间距

### Pandoc参数
- `--pdf-engine=xelatex`：使用XeLaTeX引擎
- `--toc`：生成目录
- `-V` 参数：传递LaTeX变量
- `-H` 参数：注入自定义LaTeX代码

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

## 贡献

欢迎提交Issue和Pull Request来改进这个工具！

## 许可证

MIT License
