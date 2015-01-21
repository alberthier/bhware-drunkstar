find . -name "*" -exec touch {} \;
./configure --without-http./configure --without-http_rewrite_module --prefix=/usr/local --sbin-path=/usr/local/bin/nginx --conf-path=/etc/nginx/nginx.conf --error-log-path=/tmp/nginx/error.log --http-log-path=/tmp/nginx/access.log --pid-path=/tmp/nginx/pid --lock-path=/tmp/nginx/lock --user=root --group=root
 make
 make install
