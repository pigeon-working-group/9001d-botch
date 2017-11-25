## Setup

```bash
sudo apt-get install git python3 python3-pip
sudo pip3 install pipenv
git clone https://github.com/pigeon-working-group/9001d-botch.git
cd 9001d-botch
# Pi Zero W is really slow
export PIPENV_TIMEOUT=1200
# Disable piwheels cache
sudo rm /etc/pip.conf
pipenv install
```

## Running
```bash
pipenv shell
python3 app.py
```