# Deliberately not python:slim/full or a docling-serve-style image: this
# service exists to isolate exactly one lightweight OCR engine, kept small
# and separate from the WordPress runtime on purpose (see ocr_server.py) --
# tesseract-ocr + Dutch language data is ~27MB installed, vs. multiple GB
# for a PyTorch/EasyOCR-based alternative.
#
# Rebuilt daily by .github/workflows/build.yml and pushed to GHCR, so
# consumers just pull ghcr.io/grmt/tesseract-ocr:latest and get upstream
# Python/Alpine/Tesseract security fixes automatically.
FROM python:3-alpine

# The Alpine package bundles the "fast" (LSTM-lite, lower-accuracy) nld
# model. Swap in the official "best" model instead (~8.5MB, still tiny) --
# on a real scanned page the fast model produced garbage where Document AI
# got clean text; best is the difference between usable and not.
RUN apk add --no-cache tesseract-ocr tesseract-ocr-data-nld wget && \
    wget -q -O /usr/share/tessdata/nld.traineddata \
      https://github.com/tesseract-ocr/tessdata_best/raw/main/nld.traineddata

COPY ocr_server.py /app/ocr_server.py
WORKDIR /app

EXPOSE 8080
CMD ["python3", "ocr_server.py"]
