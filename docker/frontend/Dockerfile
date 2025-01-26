FROM node:20-alpine

WORKDIR /app

COPY frontend/package*.json ./

RUN npm cache clean --force

RUN npm install -g vite @rollup/rollup-linux-x64-musl

RUN npm rebuild rollup --force

RUN npm install  --include=dev --force

COPY frontend/ .

EXPOSE 5173
CMD ["npm", "run", "dev", "--","--host", "0.0.0.0"]

