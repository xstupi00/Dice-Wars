# VUT FIT 1MITAI
# SUI 2019/2020
# Project
# Author: Vladimir Dusek, xdusek27
# Date: 22/12/2019
# File: docs.tex

# Usage:
#   $ make
#   $ make pdf
#   $ make vlna
#   $ make clean
#   $ make clean-all

NAME = docs

.PHONY: all pdf vlna clean clean-all

all:
	pdflatex $(NAME).tex
	pdflatex $(NAME).tex

pdf: all clean

vlna:
	vlna -l $(NAME).tex

clean:
	-rm -f $(NAME).aux $(NAME).log $(NAME).toc $(NAME).te~

clean-all:
	-rm -f $(NAME).aux $(NAME).log $(NAME).toc $(NAME).te~ $(NAME).pdf
