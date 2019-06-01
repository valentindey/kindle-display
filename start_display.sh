#!/bin/sh

echo "$(date) stopping framework and power daemons" >> /var/log/kindle-display.log
/etc/init.d/framework stop
/etc/init.d/powerd stop

echo "$(date) adding cronjob to update the display every minute" >> /var/log/kindle-display.log
echo "* * * * * /mnt/us/extensions/kindle-display/display.sh" >> /etc/crontab/root

/etc/init.d/cron restart
