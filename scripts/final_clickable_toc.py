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

def extract_title_from_markdown(content: str) -> str:
	"""从Markdown内容中提取标题"""
	import re
	# 查找第一个一级标题
	match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
	if match:
		return match.group(1).strip()
	
	# 如果没找到一级标题，尝试查找第一行的内容作为标题
	lines = content.strip().split('\n')
	for line in lines:
		line = line.strip()
		if line and not line.startswith('#'):
			return line
	
	return "文档"

def build(md_path: str, out_path: Optional[str] = None) -> bool:
	if out_path is None:
		out_dir = Path('../pdf_docs')
		out_dir.mkdir(exist_ok=True)
		out_path = str(out_dir / f"{Path(md_path).stem}_final_clickable_clean.pdf")
	
	# 预处理Markdown文件，确保列表格式正确
	with open(md_path, 'r', encoding='utf-8') as f:
		content = f.read()
	
	# 提取文档标题
	doc_title = extract_title_from_markdown(content)
	
	# 确保列表项之间有足够的空行
	import re
	# 在每个列表项后添加空行，确保单独成行
	content = re.sub(r'(\n- [^\n]*)\n(?=- )', r'\1\n\n', content)
	content = re.sub(r'(\n\d+\. [^\n]*)\n(?=\n\d+\. )', r'\1\n\n', content)
	
	# 确保段落之间有适当的空行
	content = re.sub(r'([^\n])\n([^\n])', r'\1\n\n\2', content)
	
	# 统一缩进方案 - 根据文档结构制定协调的缩进规则
	
	# 1. 长公式多行显示（主要公式）
	content = re.sub(r'(Feature得分 = \(.*?× 0\.4 \+ .*?× 0\.25 \+ .*?× 0\.15 \+ .*?× 0\.15 \+ ROI得分 × 0\.05\))', 
	                 r'Feature得分 = (\n    功能覆盖度得分 × 0.4 +\n    响应速度得分 × 0.25 +\n    稳定性得分 × 0.15 +\n    性价比得分 × 0.15 +\n    ROI得分 × 0.05\n  )', content)
	
	content = re.sub(r'(Signal得分 = \(.*?× 0\.25 \+ .*?× 0\.3 \+ .*?× 0\.25 \+ .*?× 0\.2\))', 
	                 r'Signal得分 = (\n    CTR得分 × 0.25 +\n    使用率得分 × 0.3 +\n    重复使用率得分 × 0.25 +\n    用户评分得分 × 0.2\n  )', content)
	
	content = re.sub(r'(最终评分 = .*?× 0\.8 \+ .*?× 0\.2)', 
	                 r'最终评分 = (\n    Feature得分 × 0.8 +\n    Signal得分 × 0.2\n  )', content)
	
	content = re.sub(r'(Combined Score = .*)', 
	                 r'Combined Score = (\n    最终评分\n  )', content)
	
	# 2. 简单公式缩进（2个空格）
	content = re.sub(r'(CTR = \(.*?\) × 100%)', r'  CTR = (点击次数 / 展示次数) × 100%', content)
	content = re.sub(r'(CTR得分 = CTR × 100)', r'  CTR得分 = CTR × 100', content)
	content = re.sub(r'(使用率 = \(.*?\) × 100%)', r'  使用率 = (实际使用次数 / 总访问次数) × 100%', content)
	content = re.sub(r'(使用率得分 = 使用率 × 100)', r'  使用率得分 = 使用率 × 100', content)
	content = re.sub(r'(重复使用率 = \(.*?\) × 100%)', r'  重复使用率 = (重复使用次数 / 首次使用次数) × 100%', content)
	content = re.sub(r'(重复使用率得分 = 重复使用率 × 100)', r'  重复使用率得分 = 重复使用率 × 100', content)
	content = re.sub(r'(用户评分得分 = 平均评分 × 20)', r'  用户评分得分 = 平均评分 × 20', content)
	
	# 3. 功能相关公式缩进（2个空格）
	content = re.sub(r'(功能覆盖度 = \(.*?\) × 100%)', r'  功能覆盖度 = (加权功能得分 / 行业标准加权功能得分) × 100%', content)
	content = re.sub(r'(响应速度评分 = max\(0, 100 - \(.*?\) × 扣分系数\))', r'  响应速度评分 = max(0, 100 - (平均响应时间 - 基准时间) × 扣分系数)', content)
	content = re.sub(r'(稳定性评分 = \(1 - 变异系数\) × 100)', r'  稳定性评分 = (1 - 变异系数) × 100', content)
	content = re.sub(r'(变异系数 = 标准差 / 平均值)', r'  变异系数 = 标准差 / 平均值', content)
	
	# 4. ROI相关公式缩进（2个空格）
	content = re.sub(r'(ROI评分 = min\(100,\(.*?\)/工具成本 × 100\))', r'  ROI评分 = min(100,(量化价值提升 - 工具成本)/工具成本 × 100)', content)
	content = re.sub(r'(量化价值提升 = .*?价值 \+ .*?价值 \+ .*?价值)', r'  量化价值提升 = 效率提升价值 + 质量提升价值 + 容量提升价值', content)
	
	# 5. 子公式缩进（4个空格）
	content = re.sub(r'(效率提升价值 = .*?× .*?× .*?)', r'    效率提升价值 = 节省工时 × 平均人工成本 × 使用频率', content)
	content = re.sub(r'(质量提升价值 = .*?× .*?× .*?)', r'    质量提升价值 = 减少错误次数 × 单次错误成本 × 使用频率', content)
	content = re.sub(r'(容量提升价值 = .*?× .*?× .*?)', r'    容量提升价值 = 新增处理能力 × 单位处理价值 × 使用频率', content)
	
	# 6. 性价比相关公式缩进（2个空格）
	content = re.sub(r'(性价比评分 = min\(100, 功能得分/价格得分 × 100\))', r'  性价比评分 = min(100, 功能得分/价格得分 × 100)', content)
	content = re.sub(r'(功能得分 = 功能覆盖度得分 × 0\.6 \+ 性能得分 × 0\.4)', r'    功能得分 = 功能覆盖度得分 × 0.6 + 性能得分 × 0.4', content)
	content = re.sub(r'(性能得分 = 响应速度得分 × 0\.6 \+ 稳定性得分 × 0\.4)', r'      性能得分 = 响应速度得分 × 0.6 + 稳定性得分 × 0.4', content)
	content = re.sub(r'(价格得分 = 100 - 价格排名百分比)', r'    价格得分 = 100 - 价格排名百分比', content)
	
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
\XeTeXlinebreakskip = 0pt plus 2pt
\sloppy
\emergencystretch=15em
\pretolerance=10000
\tolerance=20000
\hbadness=10000

% URL 自动换行
\usepackage{xurl}
\urlstyle{same}



% 防止文本截断的额外设置
\raggedright
\setlength{\emergencystretch}{25em}
\setlength{\tolerance}{100000}
\setlength{\pretolerance}{30000}
\setlength{\hbadness}{10000}

% 强制文本换行设置
\sloppy
\emergencystretch=25em
\pretolerance=30000
\tolerance=100000
\hbadness=10000

% 额外的文本截断防护
\sloppy
\emergencystretch=8em
\pretolerance=2000
\tolerance=5000
\hbadness=10000

% 强制文本换行设置
\setlength{\emergencystretch}{10em}
\setlength{\tolerance}{10000}
\setlength{\pretolerance}{5000}
\setlength{\hbadness}{10000}

% 全局宽松排版
\sloppy
\emergencystretch=10em
\pretolerance=5000
\tolerance=10000
\hbadness=10000

% 全局文本处理设置
\AtBeginDocument{%
  \sloppy
  \emergencystretch=25em
  \pretolerance=30000
  \tolerance=100000
  \hbadness=10000
  \setlength{\emergencystretch}{25em}
  \setlength{\tolerance}{100000}
  \setlength{\pretolerance}{30000}
  \setlength{\hbadness}{10000}
}

% 代码块优化设置 - 使用fancyvrb包
\usepackage{fancyvrb}
\DefineVerbatimEnvironment{Verbatim}{Verbatim}{%
  fontsize=\small,
  frame=single,
  breaklines=true,
  breakanywhere=true,
  commandchars=\\\{\},
  xleftmargin=2em,
  xrightmargin=1em
}

% 长公式处理
\newcommand{\longformula}[1]{\sloppypar\noindent\texttt{#1}\par}

% 强制长文本换行
\newcommand{\forcebreak}[1]{%
  \sloppy
  \emergencystretch=20em
  \pretolerance=20000
  \tolerance=50000
  \hbadness=10000
  #1
}

% 专门处理长公式的环境
\newenvironment{longformulaenv}{%
  \sloppypar
  \emergencystretch=25em
  \pretolerance=30000
  \tolerance=100000
  \hbadness=10000
  \setlength{\emergencystretch}{25em}
  \setlength{\tolerance}{100000}
  \setlength{\pretolerance}{30000}
  \setlength{\hbadness}{10000}
}{}





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
		'--wrap=none',
		'-V', 'mainfont=Times New Roman',
		'-V', 'CJKmainfont=STSong',
		'-V', 'geometry:margin=2.5cm',
		'-V', 'fontsize=10pt',
		'-V', 'toc-depth=3',
		'-V', 'toc-title=目录',
		'-V', 'linestretch=1.2',
		'-V', 'parskip=0.8em',
		'-V', 'parindent=1.2em',
		'-V', 'itemsep=1.0em',
		'-V', 'emergencystretch=25em',
		'-V', 'tolerance=100000',
		'-V', 'pretolerance=30000',
		'-V', 'parsep=0.5em',
		'-V', 'topsep=0.5em',
		'-V', 'partopsep=0.2em',
		'--metadata', f'title={doc_title}',
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
	import sys
	print("🚀 最终稳定版（可点击目录 + 书签 + 格式优化）")
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
