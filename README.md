Shitbucket UNDER DEV
==========

Sorry mom.

## Requirements

* Computer
* Python 3
* sqlite3
* A brain
* Oat meal
* Bathroom (because you should be drinking 8 glasses a day)

## Install for Devopment (or in my case, production)

Make sure you have virtualenv or virtualenvwrapper installed. Not going to
teach you.

Yo, you don't gotta use sqlite, but you can and stuff. I like Postgresql. Cool.

```bash
git clone https://github.com/kyleterry/shitbucket
mkvirtualenv -p /usr/bin/python3 shitbucket
cd /path/to/shitbucket
pip install -r requirements.txt
python shitbucket/main.py --db="sqlite:////tmp/shitbucket.db"
```

This is not a good example of my coding abilities. In fact, this is me at my
worst.
