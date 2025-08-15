#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终稳定版：可点击目录 + 侧栏书签 + 格式优化（行距/列表间距/中文）
- 使用 Pandoc 默认 LaTeX 模板
- 通过 header-includes 注入 hyperref 与样式
- 启用 linktoc=all 与 hypertexnames=false，修复不跳转问题
- 不显示作者/日期；中文字体；保留 TOC；优化段落与列表间距
"""

import os
import subprocess
from pathlib import Path
from typing import Optional

def build(md_path: str, out_path: Optional[str] = None) -> bool:
	if out_path is None:
		out_dir = Path('../pdf_docs')
		out_dir.mkdir(exist_ok=True)
		out_path = str(out_dir / f"{Path(md_path).stem}_final_clickable_clean.pdf")
	
	# 预处理Markdown文件，确保列表格式正确
	with open(md_path, 'r', encoding='utf-8') as f:
		content = f.read()
	
	# 确保列表项之间有足够的空行
	import re
	# 在每个列表项后添加空行，确保单独成行
	content = re.sub(r'(\n- [^\n]*)\n(?=- )', r'\1\n\n', content)
	content = re.sub(r'(\n\d+\. [^\n]*)\n(?=\n\d+\. )', r'\1\n\n', content)
	
	# 确保段落之间有适当的空行
	content = re.sub(r'([^\n])\n([^\n])', r'\1\n\n\2', content)
	
	# 创建临时处理后的文件
	temp_md = 'temp_processed.md'
	with open(temp_md, 'w', encoding='utf-8') as f:
		f.write(content)
	
	# 使用处理后的文件进行转换
	md_path = temp_md

	# header-includes：超链接+中文+行距/段落/列表间距优化
	header = r"""
% 中文与字体（配合 xelatex）
\usepackage{xeCJK}
\usepackage{fontspec}
% 中文自动换行设置
\XeTeXlinebreaklocale "zh"
\XeTeXlinebreakskip = 0pt plus 0.2pt
\sloppy
\emergencystretch=5em
\pretolerance=500
\tolerance=2000
\hbadness=10000

% URL 自动换行
\usepackage{xurl}
\urlstyle{same}

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

% 处理标题中的特殊字符
\makeatletter
\def\@maketitle{%
  \newpage
  \null
  \vskip 2em%
  \begin{center}%
  \let \footnote \thanks
    {\LARGE \@title \par}%
    \vskip 1.5em%
    {\large \lineskip .5em%
      \begin{tabular}[t]{c}%
        \@author
      \end{tabular}\par}%
    \vskip 1em%
    {\large \@date}%
  \end{center}%
  \par
  \vskip 1.5em}
\makeatother

% 段落与行距 - 确保与原始Markdown格式一致
\setlength{\parskip}{0.8em}
\setlength{\parindent}{1.2em}
\linespread{1.2}

% 列表间距优化 - 确保与原始Markdown格式一致
\usepackage{enumitem}
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
	header_file = 'pandoc_hyperref_setup.tex'
	with open(header_file, 'w', encoding='utf-8') as f:
		f.write(header)

	cmd = [
		'pandoc', md_path,
		'--pdf-engine=xelatex',
		'--toc',
		'-V', 'mainfont=Times New Roman',
		'-V', 'CJKmainfont=STSong',
		'-V', 'geometry:margin=3.0cm',
		'-V', 'fontsize=11pt',
		'-V', 'toc-depth=3',
		'-V', 'toc-title=目录',
		'-V', 'linestretch=1.2',
		'-V', 'parskip=0.8em',
		'-V', 'parindent=1.2em',
		'-V', 'itemsep=1.0em',
		'-V', 'parsep=0.5em',
		'-V', 'topsep=0.5em',
		'-V', 'partopsep=0.2em',
		'--metadata', 'title=AI Agent & Tools 评分体系设计文档',
		'--metadata', 'author=',  # 空
		'--metadata', 'date=',    # 空
		'-H', header_file,
		'-o', out_path,
	]
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
	if os.path.exists(temp_md):
		os.remove(temp_md)
	return ok


def main():
	print("🚀 最终稳定版（可点击目录 + 书签 + 格式优化）")
	for bin_ in ('pandoc', 'xelatex'):
		try:
			subprocess.run([bin_, '--version'], capture_output=True, check=True)
		except Exception:
			print(f"❌ 缺少 {bin_}")
			return
	md = '../docs/score_doc/简化版评分体系设计文档.md'
	if not os.path.exists(md):
		print(f"❌ 文件不存在: {md}")
		return
	build(md)
	print('🎉 完成，输出目录 pdf_docs/')

if __name__ == '__main__':
	main()
