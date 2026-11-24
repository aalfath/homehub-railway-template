# HomeHub for Railway: the official image, pinned by version and digest, plus a small start wrapper.
# Upstream: https://github.com/surajverma/homehub (MIT)
FROM ghcr.io/surajverma/homehub:0.7.0@sha256:c16dc026f72509dfa8ceb7c754c7963dde9cea9ee2c11bc0058ebd9647a3af01

COPY railway/ /railway/

# Everything HomeHub writes (database, secret key, uploads, PDFs, media, config.yml) lives here.
# Attach a Railway volume at /data.
ENV HOMEHUB_DATA_DIR=/data \
    PORT=5000

EXPOSE 5000

CMD ["/bin/sh", "/railway/start.sh"]
