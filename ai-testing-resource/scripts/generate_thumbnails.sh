#!/bin/bash
# Generate thumbnail images from PDF documents for landing page preview

DOCS_DIR="static/documents"
THUMBS_DIR="static/images/documents"

echo "Generating PDF thumbnails..."

# Create thumbnails directory if it doesn't exist
mkdir -p "$THUMBS_DIR"

# Convert each PDF to a thumbnail (first page only, 300 DPI, PNG format)
for pdf in "$DOCS_DIR"/*.pdf; do
  filename=$(basename "$pdf" .pdf)
  echo "Processing $filename..."

  # Use pdftoppm to convert first page to PNG
  # -singlefile: only convert first page
  # -png: output as PNG
  # -scale-to-y 400: scale height to 400px (keeps aspect ratio)
  # -scale-to-x -1: auto-calculate width based on aspect ratio
  pdftoppm -singlefile -png -scale-to-y 400 -scale-to-x -1 "$pdf" "$THUMBS_DIR/$filename"

  # Rename output (pdftoppm adds .png automatically)
  if [ -f "$THUMBS_DIR/$filename.png" ]; then
    echo "  ✓ Created $filename.png (400px height)"
  else
    echo "  ✗ Failed to create $filename.png"
  fi
done

echo ""
echo "Thumbnail generation complete!"
echo "Generated files:"
ls -lh "$THUMBS_DIR"/*.png
