FROM python:3.6.6-alpine3.8 

WORKDIR /data
RUN pip3 install  -i https://pypi.douban.com/simple flask_socketio flask requests 
COPY websocket_chat.py /data/websocket_chat.py
CMD ["python3", "websocket_chat.py"]
