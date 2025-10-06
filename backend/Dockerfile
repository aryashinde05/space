# Use node LTS
FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json* pnpm-lock.yaml* yarn.lock* ./
RUN npm ci || npm install

COPY . .

ENV NODE_ENV=production
RUN npm run build

EXPOSE 4000
CMD ["node", "dist/index.js"]
