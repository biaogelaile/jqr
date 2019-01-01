FROM mychat/chatapi 
RUN rm -rf /data
RUN pip3 install uwsgi -i https://pypi.douban.com/simple
ADD . /data
#CMD ["python3", "http_chat.py"]
CMD ["uwsgi", "--ini", "upload.ini"]
