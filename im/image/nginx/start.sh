docker build -t mychat/chatnginx . -f Dockerfile
#docker run -d -p 6001:80 -p 5001:5001 -v /root/mychat/upload/upload:/data/upload   --name=chatnginx mychat/chatnginx
