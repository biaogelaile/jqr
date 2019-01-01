message_subject_utf8=$1
message_subject_gb2312=`iconv -t GB2312 -f UTF-8 << EOF
$message_subject_utf8
EOF`
[ $? -eq 0 ] && message_subject="$message_subject_gb2312" || message_subject="$message_subject_utf8"

echo $message_subject 

curl   "http://gateway.iems.net.cn/GsmsHttp?username=69828:admin&password=89523028&to=$2&content=$message_subject_gb2312"
