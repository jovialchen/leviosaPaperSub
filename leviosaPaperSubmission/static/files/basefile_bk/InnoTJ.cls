\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{InnoTJ}[2018/06/04 V1.0a by JoyceC]

%% Article options

\DeclareOption{10pt}{
  \PassOptionsToClass{\CurrentOption}{article}
}

\DeclareOption{a4paper}{
  \PassOptionsToClass{\CurrentOption}{article}
}

\DeclareOption{onecolumn}{
  \PassOptionsToClass{\CurrentOption}{article}
}

\DeclareOption{twoside}{
  \PassOptionsToClass{\CurrentOption}{article}
}

\ProcessOptions
\ExecuteOptions{10pt,a4paper,onecolumn,twoside}
\LoadClass{book}


\RequirePackage[twoside, bindingoffset=1cm, top=2cm, bottom=2cm, outer=1.5cm, inner=1.5cm, headsep=14pt]{geometry}
\RequirePackage{tocloft}
\RequirePackage{fancyhdr}
\RequirePackage[style=numeric,autocite=plain,sorting=none, backend=biber]{biblatex}
%\RequirePackage[style=IEEE, backend=biber]{biblatex}
\RequirePackage[export]{adjustbox}
\RequirePackage{graphicx}
\RequirePackage{tabularx}
\RequirePackage{multirow}
\RequirePackage{float}
\RequirePackage{listings}
\RequirePackage{color}

%\RequirePackage{incgraph}
\RequirePackage{pdfpages}

\definecolor{dkgreen}{rgb}{0,0.6,0}
\definecolor{gray}{rgb}{0.5,0.5,0.5}
\definecolor{mauve}{rgb}{0.58,0,0.82}

\lstset{frame=tb,
  language=Java,
  aboveskip=3mm,
  belowskip=3mm,
  showstringspaces=false,
  columns=flexible,
  basicstyle={\small\ttfamily},
  numbers=none,
  numberstyle=\tiny\color{gray},
  keywordstyle=\color{blue},
  commentstyle=\color{dkgreen},
  stringstyle=\color{mauve},
  breaklines=true,
  breakatwhitespace=true,
  tabsize=3
}

\definecolor{lightgray}{rgb}{.9,.9,.9}
\definecolor{darkgray}{rgb}{.4,.4,.4}
\definecolor{purple}{rgb}{0.65, 0.12, 0.82}

\lstdefinelanguage{JavaScript}{
  keywords={typeof, new, true, false, catch, function, return, null, catch, switch, var, if, in, while, do, else, case, break},
  keywordstyle=\color{blue}\bfseries,
  ndkeywords={class, export, boolean, throw, implements, import, this},
  ndkeywordstyle=\color{darkgray}\bfseries,
  identifierstyle=\color{black},
  sensitive=false,
  comment=[l]{//},
  morecomment=[s]{/*}{*/},
  commentstyle=\color{purple}\ttfamily,
  stringstyle=\color{red}\ttfamily,
  morestring=[b]',
  morestring=[b]"
}

\lstset{
   language=JavaScript,
   backgroundcolor=\color{lightgray},
   extendedchars=true,
   basicstyle=\footnotesize\ttfamily,
   showstringspaces=false,
   showspaces=false,
   numbers=left,
   numberstyle=\footnotesize,
   numbersep=9pt,
   tabsize=2,
   breaklines=true,
   showtabs=false,
   captionpos=b
}


%table of contents
\setcounter{tocdepth}{0}
\setcounter{secnumdepth}{5}
\renewcommand{\cftchapleader}{\cftdotfill{\cftdotsep}}


%TJ Areas 
\renewcommand{\thepart}{}
\renewcommand{\partname}{}

%title of each paper
\renewcommand{\chaptername}{}
\renewcommand{\thechapter}{}
\newcommand {\papertitle}[1]{\chapter[#1]{\centering #1}}


%header and footer

\pagestyle{fancy}
%redefine \leftmark and \rightmark
\newcommand{\partmark}[1]{\markboth{\thepart #1}{}}
\let\oldpart=\@part
\def\@part[#1]#2{\oldpart [#1]{#2}\partmark{#1}}
\renewcommand{\chaptermark}[1]{\markright{\chaptername{} \thechapter{} #1}}
\renewcommand{\sectionmark}[1]{}
%header and footer content
\fancyhf{}
\fancyhead[le,ro]{\rightmark}
\fancyhead[re,lo]{\leftmark}
\fancyfoot[ce,co]{\slshape JournalName}
\fancyfoot[le,ro]{\thepage}

%paragraph fomratting
\setlength{\parindent}{0em}
\setlength{\parskip}{1em}

%author block
\newcounter{mycounter}
\newcommand{\setnoofauthors}[1]{\setcounter{mycounter}{#1}}
%the block itself
\newcommand\paperauthor[6]{%
    \def\authora{#1}%
    \def\authorb{#2}%
    \def\authorc{#3}%
    \def\authord{#4}%
    \def\authore{#5}%
    \def\authorf{#6}%
}
\newcommand\paperdepartment[6]{%
    \def\dpmta{#1}%
    \def\dpmtb{#2}%
    \def\dpmtc{#3}%
    \def\dpmtd{#4}%
    \def\dpmte{#5}%
    \def\dpmtf{#5}%
}
\newcommand\paperemail[6]{%
    \def\emaila{#1}%
    \def\emailb{#2}%
    \def\emailc{#3}%
    \def\emaild{#4}%
    \def\emaile{#5}%
    \def\emailf{#5}%
}
\newcommand{\printpaperauthor}{
\begin{center}
	\ifnum \value{mycounter}=1
  		\authora\\ 
  		\dpmta\\  
  		\emaila \\  
	\else
	  	\ifnum \value{mycounter}=2
			\begin{tabular}
			{ c c  }
  			\authora& \authorb\\ 
  			\dpmta 	& \dpmtb\\  
  			\emaila &\emailb \\  
			\end{tabular}
		\else
	  		\ifnum \value{mycounter}=3
				\begin{tabular}
				{ c c c }
				\authora& \authorb & \authorc\\ 
  				\dpmta & \dpmtb &\dpmtc\\  
  				\emaila &\emailb &\emailc\\  
				\end{tabular}
			\else
		  		\ifnum \value{mycounter}=4
					\begin{tabular}
					{ c c  }
  					\authora& \authorb\\ 
  					\dpmta 	& \dpmtb\\  
  					\emaila &\emailb \\  
					\\
  					\authorc& \authord\\ 
  					\dpmtc 	& \dpmtd\\  
  					\emailc &\emaild \\  
					\end{tabular}
				\else
					\ifnum \value{mycounter}=5
						\begin{tabular}
						{ c c c }
						\authora& \authorb & \authorc\\ 
  						\dpmta & \dpmtb &\dpmtc\\  
  						\emaila &\emailb &\emailc\\  
						\end{tabular}

						\begin{tabular}
						{ c c  }
  						\authord& \authore\\ 
  						\dpmtd 	& \dpmte\\  
  						\emaild &\emaile \\  
						\end{tabular}
					\else
						\ifnum \value{mycounter}=6
							\begin{tabular}
							{ c c c }
							\authora& \authorb & \authorc\\ 
  							\dpmta & \dpmtb &\dpmtc\\  
  							\emaila &\emailb &\emailc\\  
								\\
							\authord& \authore & \authorf\\ 
  							\dpmtd & \dpmte &\dpmtf\\  
  							\emaild &\emaile &\emailf\\  
							\end{tabular}
						\fi
					\fi
				\fi

	  		\fi
	  	\fi
	\fi
\end{center}
}


%abstract
\newcommand{\abstractname}{Abstract}
\newenvironment{abstract}{
  \normalfont
  \list{}{
    \labelwidth0pt
    \leftmargin0pt \rightmargin\leftmargin
    \listparindent\parindent \itemindent0pt
    \parsep0pt
    \let\fullwidthdisplay\relax}
  \item[\hskip\labelsep\bfseries\abstractname\enspace --] \small}{\endlist}

%keywords
\newcommand{\keywordsname}{Keywords}
\newenvironment{keywords}{
  \normalfont
  \list{}{
    \labelwidth0pt
    \leftmargin0pt \rightmargin\leftmargin
    \listparindent\parindent \itemindent0pt
    \parsep0pt
    \let\fullwidthdisplay\relax}
  \item[\hskip\labelsep\bfseries\keywordsname:] \small}{\endlist}

%the section in each paper
\renewcommand{\thesection}{\arabic{section}}
\renewcommand{\figurename}{}
\renewcommand{\thefigure}{Figure \arabic{figure}}
\renewcommand{\theequation}{Equation \arabic{equation}}
\renewcommand{\tablename}{}
\renewcommand{\thetable}{Table \arabic{table}}

%About the authors
\newcommand{\aboutheauthor}[2]{\begin{table}[H]
    %\begin{tabular}{ c c }
    \begin{tabular}{m{2.8cm} m{0.8\textwidth}}
    %\includegraphics[width=0.3\textwidth, height=0.4\textwidth]{#1}
    \includegraphics[width=2cm, height=2.7cm]{#1}
      & #2
\end{tabular}
\end{table}

}

