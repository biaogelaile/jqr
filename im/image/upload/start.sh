docker build -t mychat/chatupload . -f Dockerfile
#docker stop chatupload
#docker rm chatupload
#docker run -d -p 6000:6000 -v /root/mychat/upload/upload:/data/upload   --name=chatupload mychat/chatupload

