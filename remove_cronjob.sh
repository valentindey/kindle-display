#!/bin/sh

echo "$(date) removing display update cronjob" >> /var/log/kindle-display.log
sed -i '/display.sh/d' /etc/crontab/root
/etc/init.d/cron restart
