FROM debian:buster
MAINTAINER Lionel PRAT <lionel.prat9@gmail.com>

RUN apt-get update && apt-get install --no-install-recommends -y zlib1g-dev gcc make git autoconf autogen automake pkg-config curl ipset firehol firehol-tools nano vim cron ca-certificates
# Add crontab file in the cron directory
ADD crontab_update /etc/cron.d/ipset-update-cron
# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/ipset-update-cron
#add entrypoint
ADD docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod 0755 /docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]

