# Desarrollo: Next.js con Node
FROM node:22-alpine

WORKDIR /app

# Solo package.json para imagen base; ./frontend (incl. src/) se monta en /app por el volumen
COPY package.json package-lock.json* ./
RUN npm install

EXPOSE 3000

# docker-compose sobreescribe con: npm install && npm run dev
CMD ["npm", "run", "dev"]