Shitbucket UNDER DEV
==========

Sorry mom.

## Requirements

* Python 3
* sqlite3
* A brain

## Install for Dev

Make sure you have virtualenv or virtualenvwrapper installed. Not going to
teach you.

```bash
git clone https://github.com/kyleterry/shitbucket
mkvirtualenv -p /usr/bin/python3 shitbucket
cd /path/to/shitbucket
pip install -r requirements.txt
python shitbucket/main.py --db="sqlite:////tmp/shitbucket.db"
```
