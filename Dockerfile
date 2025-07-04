FROM node:18-alpine AS react-build
WORKDIR /app/site
COPY site/package*.json ./
RUN npm install
COPY site/ .
RUN npm run build

FROM python:3.12-slim AS run-stage
WORKDIR /app
COPY --from=react-build /app/site/build ./site/build

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "serve:app", "--host", "0.0.0.0"]