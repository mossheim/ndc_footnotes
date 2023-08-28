#!/bin/sh

pandoc --from docx --to markdown "$1" >pandoc_out.md
./script.py pandoc_out.md >script_out.md
