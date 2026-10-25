# tesseract-ocr

Minimal HTTP wrapper around the `tesseract` CLI binary (`python:3-alpine` +
`tesseract-ocr` + official Dutch `tessdata_best` language model), isolated as
its own lightweight internal container service.

Built daily (and on every `Dockerfile` or `ocr_server.py` change) by
[`.github/workflows/build.yml`](.github/workflows/build.yml), always with
`--pull`, and pushed to GHCR:

- `ghcr.io/grmt/tesseract-ocr:latest`

This keeps the image current with upstream Python/Alpine/Tesseract security
fixes without anyone having to remember to rebuild it by hand.
