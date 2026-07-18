FROM node:22-alpine
WORKDIR /app
RUN apk add --no-cache openssl
COPY package.json package-lock.json ./
RUN npm ci --omit=dev
COPY server.js ./
COPY lib ./lib
COPY public ./public
RUN openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /app/tls.key -out /app/tls.crt \
    -subj "/CN=rutaexpress-demo-comite.eastus.cloudapp.azure.com" \
    -addext "subjectAltName=DNS:rutaexpress-demo-comite.eastus.cloudapp.azure.com,DNS:localhost,IP:127.0.0.1"
ENV PORT=3080
ENV TLS_PORT=3443
EXPOSE 3080 3443
CMD ["node", "server.js"]
