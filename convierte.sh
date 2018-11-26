iconv -f $1 -t utf-8 $2 >/tmp/$2
mv /tmp/$2 $2
