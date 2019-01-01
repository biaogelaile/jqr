FROM mychat/httpapi 
RUN apk update && apk add curl
ADD . /data
CMD ["python3", "http_chat.py"]
