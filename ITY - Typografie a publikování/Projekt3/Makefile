# LaTeX Makefile

PROJ=proj3


.PHONY: clean pack pdflatex

$(PROJ).pdf: $(PROJ).ps
	ps2pdf -sPAPERSIZE=a4 $^

$(PROJ).ps: $(PROJ).dvi
	dvips $^

$(PROJ).dvi: $(PROJ).tex
	latex $^
	latex $^

pdflatex: $(PROJ).tex
	pdflatex $^

