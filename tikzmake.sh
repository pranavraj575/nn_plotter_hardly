#!/bin/bash


python $1.py 
pdflatex $1.tex

rm *.aux *.log *.vscodeLog
rm *.tex

if [[ $2 == "y" ]]; then
  if [[ "$OSTYPE" == "darwin"* ]]; then
      open $1.pdf
  else
      xdg-open $1.pdf
  fi
fi