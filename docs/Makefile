
#
#  Simple wrapper Makefile to produce documentation from LyX/LaTeX
#

## Macro Definitions
#
#  The following define the programs to use to generate various documentation
#  types, as follows:
#
#    * HTML:		latex2html
#    * PostScript:	dvips 
#    * PDF:		dvipdf 
#
#  Command-line options can be added/changed here, or other software with a
#  compatible interface can be substituted.

L2H = latex2html -split 0 -show_section_numbers -toc_depth 5 -ascii_mode -images
DVIPS = dvips
DVIPDF = dvipdf
L2RTF = latex2rtf


## File Lists
## Adjust $GARBAGE to add extra files for deletion in `make clean`

GRAPHICS = SimpleFrame.eps

LATEX_GARBAGE = *.aux *.lof *.dvi *.log *.toc *.lot
GARBAGE = $(LATEX_GARBAGE) *~


PS = manual.ps
PDF = manual.pdf
RTF = # List of RTF Files
HTML = # List HTML Files


## Basic Dependencies

# Default target makes all doc types
all: ps pdf html rtf

ps: $(PS)
pdf: $(PDF)
html: $(HTML)
rtf: $(RTF)

#
# Export graphics from various file formats into EPS for easy inclusion

%.eps: %.dia
	dia -e $@ $<

%.eps: %.jpg
	convert $< $@

%.eps: %.png
	convert $< $@


# Export from LyX to LaTeX
%.tex: %.lyx
	lyx -e latex $<

# Run LaTeX a few times to generate DVI file
%.dvi: %.tex $(GRAPHICS)
	latex $<
	latex $<
	latex $<
	latex $<


# DVI converters for different formats
%.ps: %.dvi
	$(DVIPS) -o $@ $<

%.pdf: %.dvi
	$(DVIPDF) $< $@

%/index.html: %.tex
	$(L2H) $<

%.rtf: %.dvi
	$(L2RTF) $*.tex


##  Cleanup Commands

clean:
	rm -rf $(GARBAGE)

clobber: clean
	rm -rf $(PDF) $(PS) $(HTML) $(RTF)


