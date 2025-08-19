#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版：可点击目录 + 侧栏书签 + 格式优化 + 简单Emoji清理
- 使用 Pandoc 默认 LaTeX 模板
- 通过 header-includes 注入 hyperref 与样式
- 启用 linktoc=all 与 hypertexnames=false，修复不跳转问题
- 不显示作者/日期；中文字体；保留 TOC；优化段落与列表间距
- 简单清理emoji：只清理常见emoji，避免破坏Markdown语法
"""

import os
import subprocess
import re
from pathlib import Path
from typing import Optional

def clean_emojis_simple(content: str) -> str:
    """简单清理emoji，只处理常见emoji，避免过度处理"""
    
    # 定义最常见的emoji列表，分批处理
    common_emojis = [
        '🔥', '⭐', '✅', '❌', '💎', '⚡', '💼', '🏆', '🎯', '🚀',
        '📊', '📈', '📉', '💡', '🔧', '⚙️', '🛠️', '📝', '📋', '📄',
        '📁', '📂', '💻', '🖥️', '📱', '📞', '📧', '🔍', '🔎', '🔐',
        '🔒', '🔓', '🔑', '🛡️', '🎪', '🎭', '🎨', '🎬', '🎵', '🎶',
        '💰', '💳', '💸', '💵', '🌐', '🌍', '🌎', '🌏'
    ]
    
    # 直接替换，避免复杂的正则表达式
    for emoji in common_emojis:
        content = content.replace(emoji, '')
    
    # 修复Markdown粗体语法问题
    # 修复 "** 文本**" -> "**文本**"
    content = re.sub(r'\*\* ([^*]+?)\*\*', r'**\1**', content)
    # 修复 "**文本 **" -> "**文本**"  
    content = re.sub(r'\*\*([^*]+?) \*\*', r'**\1**', content)
    # 修复 "** 文本 **" -> "**文本**"
    content = re.sub(r'\*\* ([^*]+?) \*\*', r'**\1**', content)
    
    # 清理可能产生的多余空格，但要小心处理
    lines = content.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # 清理行首的多余空格（但保留缩进）
        if line.startswith('   '):  # 3个或更多空格
            line = '  ' + line.lstrip()  # 规范化为2个空格
        
        # 清理行内的多个连续空格（但避免影响Markdown语法）
        # 避免破坏已经修复的粗体语法
        line = re.sub(r'(?<!\*)  +(?!\*)', ' ', line)  # 2个或更多空格变为1个，但不影响**前后
        
        cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)

def extract_title_from_markdown(content: str) -> str:
    """从Markdown内容中提取标题"""
    # 查找第一个一级标题
    match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if match:
        title = match.group(1).strip()
        # 简单清理标题中的emoji
        title = clean_emojis_simple(title)
        return title
    
    # 如果没找到一级标题，尝试查找第一行的内容作为标题
    lines = content.strip().split('\n')
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            title = clean_emojis_simple(line)
            return title
    
    return "文档"

def build(md_path: str, out_path: Optional[str] = None) -> bool:
    if out_path is None:
        out_dir = Path('../pdf_docs')
        out_dir.mkdir(exist_ok=True)
        out_path = str(out_dir / f"{Path(md_path).stem}_emoji_simple.pdf")
    
    # 预处理Markdown文件
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🧹 开始简单emoji清理...")
    
    # 简单清理emoji
    content = clean_emojis_simple(content)
    
    print("🧹 Emoji清理完成，开始处理文档格式...")
    
    # 提取文档标题（已清理emoji）
    doc_title = extract_title_from_markdown(content)
    
    # 优化Markdown格式，保持原有结构（使用稳定版本的处理逻辑）
    
    # 1. 保护代码块不被修改
    code_blocks = []
    def preserve_code_block(match):
        code_blocks.append(match.group(0))
        return f"__CODE_BLOCK_{len(code_blocks)-1}__"
    
    # 保护所有代码块（包括```和行内代码）
    content = re.sub(r'```[\s\S]*?```', preserve_code_block, content)
    content = re.sub(r'`[^`\n]+`', preserve_code_block, content)
    
    # 2. 改善段落和列表的间距
    # 确保标题后有空行
    content = re.sub(r'(^#{1,6}\s+.*?)(\n)([^#\n])', r'\1\n\n\3', content, flags=re.MULTILINE)
    
    # 确保列表项之间有适当的空行，但不破坏嵌套结构
    # 为主列表项添加空行（不影响子项）
    content = re.sub(r'(\n- [^\n]*)\n(?=- [^\n]*)', r'\1\n\n', content)
    content = re.sub(r'(\n\d+\. [^\n]*)\n(?=\d+\. [^\n]*)', r'\1\n\n', content)
    
    # 3. 确保段落之间有适当的空行
    lines = content.split('\n')
    processed_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        processed_lines.append(line)
        
        # 如果当前行不为空，下一行也不为空，且都不是特殊格式，则添加空行
        if (i < len(lines) - 1 and 
            line.strip() and 
            lines[i + 1].strip() and
            not line.startswith('#') and 
            not lines[i + 1].startswith('#') and
            not line.startswith('-') and
            not lines[i + 1].startswith('-') and
            not line.startswith('*') and
            not lines[i + 1].startswith('*') and
            not re.match(r'^\d+\.', line) and
            not re.match(r'^\d+\.', lines[i + 1]) and
            not line.startswith('>') and
            not lines[i + 1].startswith('>') and
            '__CODE_BLOCK_' not in line and
            '__CODE_BLOCK_' not in lines[i + 1]):
            
            # 检查是否已经有空行
            if i < len(lines) - 1 and lines[i + 1].strip():
                processed_lines.append('')  # 添加空行
        
        i += 1
    
    content = '\n'.join(processed_lines)
    
    # 4. 改善ASCII图表显示
    ascii_art_pattern = r'```\n([\s\S]*?[┌┐└┘│─├┤┬┴┼]+[\s\S]*?)\n```'
    def enhance_ascii_art(match):
        content = match.group(1)
        return f'```{{.ascii}}\n{content}\n```'
    
    # 先恢复代码块
    for i, code_block in enumerate(code_blocks):
        content = content.replace(f"__CODE_BLOCK_{i}__", code_block)
    
    # 然后处理ASCII艺术
    content = re.sub(ascii_art_pattern, enhance_ascii_art, content)
    
    # 5. 改善markdown文本格式
    # 改善引用块的显示
    content = re.sub(r'^> \*\*(.*?)\*\*：(.*?)$', r'> **\1**: \2', content, flags=re.MULTILINE)
    
    # 改善API接口标题的显示
    content = re.sub(r'^#### (\d+\.\d+) (.*?)API$', r'#### \1 \2 API', content, flags=re.MULTILINE)
    
    # 6. 统一处理所有定义标题的格式和内容缩进
    lines = content.split('\n')
    processed_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # 检测所有类型的定义标题
        if re.match(r'^\*\*(功能描述|应用举例|技术实现|使用场景|注意事项|实现细节|返回格式|错误处理)\*\*[：:]', line.strip()):
            # 确保前面有空行
            if processed_lines and processed_lines[-1].strip():
                processed_lines.append('')
            
            processed_lines.append(line)
            i += 1
            
            # 确保后面有空行
            processed_lines.append('')
            
            # 处理定义内容的缩进
            while i < len(lines) and lines[i].strip():
                content_line = lines[i]
                # 如果不是特殊格式，添加缩进
                if (not content_line.startswith('#') and 
                    not content_line.startswith('```') and
                    not re.match(r'^\*\*(.*?)\*\*[：:]', content_line.strip()) and
                    content_line.strip()):
                    # 添加缩进
                    if not content_line.startswith('  '):
                        content_line = '  ' + content_line.lstrip()
                processed_lines.append(content_line)
                i += 1
            continue
        
        processed_lines.append(line)
        i += 1
    
    content = '\n'.join(processed_lines)
    
    # 创建临时处理后的文件
    temp_md = 'temp_emoji_simple.md'
    with open(temp_md, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"🔍 临时文件保存为: {temp_md}")
    print(f"📄 文档标题: {doc_title}")
    print(f"📝 处理后内容长度: {len(content)} 字符")
    
    # header-includes：超链接+中文+行距/段落/列表间距优化
    header = r"""
% 中文与字体（配合 xelatex）
\usepackage{xeCJK}
\usepackage{fontspec}
\setCJKmainfont{PingFang SC}
\setmonofont[Scale=0.9]{Menlo}

% 中文自动换行设置
\XeTeXlinebreaklocale "zh"
\XeTeXlinebreakskip = 0pt plus 2pt
\sloppy
\emergencystretch=15em
\pretolerance=10000
\tolerance=20000
\hbadness=10000

% URL 自动换行
\usepackage{xurl}
\urlstyle{same}

% 改进的代码块和缩进设置
\usepackage{fancyvrb}
\usepackage{xcolor}
\definecolor{codebg}{RGB}{248,248,248}
\definecolor{codeframe}{RGB}{220,220,220}

% 定义列表和段落格式改进
\usepackage{enumitem}

% 改进的列表间距
\setlist[itemize]{
  leftmargin=2.5em,
  itemsep=0.4em,
  parsep=0.2em,
  topsep=0.5em
}

\setlist[enumerate]{
  leftmargin=2.5em,
  itemsep=0.4em,
  parsep=0.2em,
  topsep=0.5em
}

% 段落缩进控制
\setlength{\parindent}{0pt}
\setlength{\parskip}{0.8em}

% 行内代码的改进样式
\let\oldtexttt\texttt
\renewcommand{\texttt}[1]{%
  \colorbox{codebg}{%
    \footnotesize\oldtexttt{\hspace{0.2em}#1\hspace{0.2em}}%
  }%
}

% 改进标题间距
\usepackage{titlesec}
\titlespacing*{\section}{0pt}{*3.5}{*2.5}
\titlespacing*{\subsection}{0pt}{*3}{*2}  
\titlespacing*{\subsubsection}{0pt}{*2.5}{*1.5}
\titlespacing*{\paragraph}{0pt}{*2}{*1}

% 超链接/书签配置
\usepackage[unicode=true]{hyperref}
\hypersetup{
  colorlinks=true,
  linkcolor=blue,
  urlcolor=blue,
  citecolor=blue,
  linktoc=all,
  pdfencoding=auto
}
% 避免重复锚点导致跳回目录
\makeatletter
\@ifpackageloaded{hyperref}{\hypersetup{hypertexnames=false}}{}
\makeatother

% 目录标题本地化
\renewcommand{\contentsname}{目录}

% 段落与行距
\setlength{\parskip}{0.8em}
\setlength{\parindent}{1.2em}
\linespread{1.2}

% 列表间距优化
\setlist[itemize]{leftmargin=2em,itemsep=1.0em,parsep=0.5em,topsep=0.5em,partopsep=0.2em}
\setlist[enumerate]{leftmargin=2em,itemsep=1.0em,parsep=0.5em,topsep=0.5em,partopsep=0.2em}

% 强制每个列表项单独成行，禁用紧凑模式
\renewcommand{\tightlist}{%
  \setlength{\itemsep}{1.0em}%
  \setlength{\parskip}{0.5em}%
  \setlength{\parsep}{0.5em}%
  \setlength{\topsep}{0.5em}%
  \setlength{\partopsep}{0.2em}%
}
"""
    
    header_file = 'pandoc_emoji_simple_setup.tex'
    with open(header_file, 'w', encoding='utf-8') as f:
        f.write(header)

    cmd = [
        'pandoc', temp_md,
        '--pdf-engine=xelatex',
        '--toc',
        '--wrap=none',
        '-V', 'mainfont=Times New Roman',
        '-V', 'CJKmainfont=PingFang SC',
        '-V', 'geometry:margin=2.5cm',
        '-V', 'fontsize=10pt',
        '-V', 'toc-depth=3',
        '-V', 'toc-title=目录',
        '-V', 'linestretch=1.2',
        '-V', 'parskip=0.8em',
        '-V', 'parindent=1.2em',
        '-V', 'itemsep=1.0em',
        '--metadata', f'title={doc_title}',
        '--metadata', 'author=',  # 空
        '--metadata', 'date=',    # 空
        '-H', header_file,
        '-o', out_path,
    ]
    
    print("🚀 开始PDF转换...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        print(f"✅ 成功转换: {md_path} -> {out_path}")
        ok = True
    else:
        print("❌ 转换失败:\n" + res.stderr)
        ok = False
    
    # 清理临时文件
    if os.path.exists(header_file):
        os.remove(header_file)
    # 保留临时文件以便调试
    # if os.path.exists(temp_md):
    #     os.remove(temp_md)
    
    return ok


def main():
    import sys
    print("🧹 简化Emoji清理版（可点击目录 + 书签 + 格式优化）")
    for bin_ in ('pandoc', 'xelatex'):
        try:
            subprocess.run([bin_, '--version'], capture_output=True, check=True)
        except Exception:
            print(f"❌ 缺少 {bin_}")
            return
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        md = sys.argv[1]
    else:
        md = '../docs/score_doc/简化版评分体系设计文档.md'
    
    if not os.path.exists(md):
        print(f"❌ 文件不存在: {md}")
        return
    
    build(md)
    print('🎉 完成，输出目录 pdf_docs/')

if __name__ == '__main__':
    main()
