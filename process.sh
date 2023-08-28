#!/bin/sh

pandoc --from docx --to markdown "$1" >pandoc_out.md
