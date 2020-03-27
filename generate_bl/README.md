# Generate black list

It's created by cybersecurity service of ANS ["Agence Numérique Santé" -> "Digital Health Agency"](https://cyberveille-sante.gouv.fr/). 
It's help you to generate a blacklist from different lists (firehol, MISP, cybercrime, ...).

## Require
  - [docker](https://docs.docker.com/install/) & [docker compose](https://docs.docker.com/compose/)
  - Many API key (it's optional)
    - MISP
    - AUTOSHUN
    - XFORCE IBM
    - BLUELIV
    - IP2LOCATION
  - pip3 local require:
    - pymisp
    - requests
    - dnspython
    - ipaddress
    
## Let's Start
  - build docker firehol image: docker-compose build
  - Configure docker-compose.yml: 
    - Put your API keys in docker-compose.yml (ENV VAR)
    - (verify fields "volumes:" and change if need & you can log docker by syslog)
  - Run docker firehol: docker-compose up -d
  - Configure API key and host for misp in keys.py
  - Run first time script misp.py and verify is run ok (check result in misp.ipset)
    - "python3 /data/docker/firehol/misp.py -l 90d -o ./blacklist/misp.ipset"
  - Put misp script in crontab (exemple in crontab-on-host)
  - Run first time script cybercrime.py and verify is run ok (check result in misp.ipset)
    - "python3 /data/docker/firehol/cybercrime.py"
  - Put cybercrime script in crontab (exemple in crontab-on-host)
  - Wait a little after the launch of firhol for all the ipsets to be created, and run first time create_ipbl.py
    - python3 create_ipbl.py
      - Check result in 'results/db-ipbl.json'
  - Put create_ipbl.py script in crontab (exemple in crontab-on-host)
    
## Add a new entry to the blacklist
  - Create a script (python or other langage) for generate a ipset file in firehol directory: ./blacklist
    - respect IPSET FORMAT

