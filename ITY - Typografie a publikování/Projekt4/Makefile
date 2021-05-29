PROJ=proj4

.PHONY: clean pack bibtex pdflatex

$(PROJ).pdf: $(PROJ).ps
	ps2pdf -sPAPERSIZE=a4 $^

$(PROJ).ps: $(PROJ).dvi
	dvips $^

$(PROJ).dvi: $(PROJ).tex
	latex $^
	make bibtex
	latex $^
	latex $^

bibtex: $(PROJ).bib
	bibtex $(PROJ)

pdflatex: $(PROJ).tex
	pdflatex $^
	make bibtex
	pdflatex $^
	pdflatex $^

