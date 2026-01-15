FROM node:current-alpine

ARG APP_PATH=.

WORKDIR /app

COPY ${APP_PATH}/package*.json ./

RUN npm install
RUN apk --no-cache add curl

COPY . .

EXPOSE ${REACT_APP_PORT}

CMD ["npm", "start", "--port=${REACT_APP_PORT:-3000}"]