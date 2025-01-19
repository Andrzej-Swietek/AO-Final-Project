FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt ./
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY backend/ .

COPY ./entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

EXPOSE 5000

CMD ["/app/entrypoint.sh"]


# # Stage 1: FRONTEND BUILD
# FROM node:18-alpine AS frontend-build

# WORKDIR /frontend
# COPY frontend/package*.json ./
# RUN npm install
# COPY frontend/ .
# RUN npm run build && ls -l /frontend/dist

# # Stage 2: BACKEND
# FROM python:3.11-slim

# WORKDIR /app

# COPY backend/requirements.txt ./
# RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# # RUN pip install --no-cache-dir -r requirements.txt

# COPY backend/ .

# COPY ./entrypoint.sh /app/entrypoint.sh
# RUN chmod +x /app/entrypoint.sh

# COPY --from=frontend-build ./dist ./static

# RUN ls -l /app/static

# EXPOSE 5000

# CMD ["/app/entrypoint.sh"]