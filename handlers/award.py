from __future__ import print_function #debug
import os

class Award:
	def __init__(self,awardDetails,saveAs):
		self.details = awardDetails
		self.filename = saveAs
		self.awardTemplate = r'''
		\documentclass[landscape]{article}
		\usepackage{wallpaper}
		\usepackage{niceframe}
		\usepackage{xcolor}
		\usepackage{ulem}
		\usepackage{graphicx}
		\usepackage{geometry}
		\geometry{tmargin=.5cm,bmargin=.5cm,
		lmargin=.5cm,rmargin=.5cm}
		\usepackage{multicol}
		\setlength{\columnseprule}{0.4pt}
		\columnwidth=0.3\textwidth

		\begin{document}

		\TileWallPaper{4cm}{2cm}{''' + awardDetails['background'] + r'''}

		\centering
		\scalebox{3.0}{\color{green!30!black!60}
		\begin{minipage}{.33\textwidth}
		\font\border=umrandb
		\generalframe
		{\border \char113} % up left
		{\border \char109} % up
		{\border \char112} % up right
		{\border \char108} % left 
		{\border \char110} % right
		{\border \char114} % lower left
		{\border \char111} % bottom
		{\border \char115} % lower right
		{\centering

		\begin{minipage}{.9\textwidth}
		\centering
		\includegraphics[height=0.9cm]{''' + awardDetails['logo'] + r'''}
		\end{minipage}
		\vspace{-8mm}

		\curlyframe[.9\columnwidth]{

		\textcolor{red!10!black!90}
		{\small ''' + awardDetails['company'] + r'''}\\ 
		\textcolor{green!10!black!90}{
		\tiny ''' + awardDetails['message'] + r'''}

		\smallskip

		\textcolor{black}{\large \textsc{''' + awardDetails['title'] + r'''}}

		\vspace{2mm}

		\small
		{\textcolor{black}{
		\uppercase{''' + awardDetails['employee'] + r'''}}}

		\vspace{8mm}

		{\color{blue!40!black}
		\scalebox{.8}{
		\begin{tabular}{ccc}
		\cline{1-1} 
		\cline{3-3}
		\ ''' + awardDetails['admin1'] + r''' & & ''' + awardDetails['admin2'] + r'''\\
		\ ''' + awardDetails['adminTitle1'] + r''' & & ''' + awardDetails['adminTitle2'] + r'''\\
		\end{tabular}
		}}}}
		\end{minipage}
		}
		\end{document}
		'''
		
	def _genTexFile(self,filename):
		texFile = filename + '.tex'
		with open(texFile,'w') as file:
			file.write(self.awardTemplate)
		
		if os.path.getsize(texFile) == 0:
			raise Exception('Unable to create tex file.')
		
		return texFile
		
	def _genPDF(self,texFile):
		os.system('pdflatex ' + texFile)
		pdf = texFile[:-3] + 'pdf'
			
		return pdf
		
	def _clean(self):
		os.remove(self.filename + '.log')
		os.remove(self.filename + '.aux')
		os.remove(self.filename + '.tex')
		
	def genAward(self):
		texFile = self._genTexFile(self.filename)
		pdf = self._genPDF(texFile)
		self._clean()
		return pdf