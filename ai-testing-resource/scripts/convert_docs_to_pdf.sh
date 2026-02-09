#!/bin/bash
# Convert all .docx documents to PDF using LibreOffice headless

DOCS_DIR="static/documents"
BACKUP_DIR="static/documents-source"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Copy originals to backup
echo "Backing up original .docx files..."
cp "$DOCS_DIR"/*.docx "$BACKUP_DIR/"

# Convert each .docx to PDF
echo "Converting .docx to PDF..."
for docx in "$DOCS_DIR"/*.docx; do
  echo "Converting $(basename "$docx")..."
  soffice --headless --convert-to pdf --outdir "$DOCS_DIR" "$docx"
done

# Verify PDFs were created
echo "Verifying PDFs..."
ls -lh "$DOCS_DIR"/*.pdf

echo "Conversion complete. Original .docx files backed up to $BACKUP_DIR/"
