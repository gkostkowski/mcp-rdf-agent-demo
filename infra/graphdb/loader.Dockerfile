FROM alpine:3.22

RUN apk add --no-cache curl jq

COPY load-graphdb.sh /usr/local/bin/graphdb-loader

ENTRYPOINT ["/usr/local/bin/graphdb-loader"]
CMD ["load"]
