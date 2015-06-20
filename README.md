# meh
basic, personal 4chan archiver

what
----

You hit 'update' on the homepage. It will then scrape all the OP posts (no replies yet). You can use browse to go page by page or search to look for posts containing a certain term(s).

needs
-----

* redis server
* `pip install -r requirements.txt`
* `python models.py` to make DB

optional: setup a cronjob to run `python func.py` on some interval to update the archive.

todo
----

- [ ] ! search results need to be ranked according to relevance
- [ ] ! need way to add and remove boards from database (and cascade removing of threads related), list info for particular boards here too (such as g has 200 threads)
- [ ] ! way of removing individual threads in list views (search, browse, home, etc)
- [ ] need to get threads AND replies to threads (straightforward, but didn't want to do that yet)
- [ ] images would be nice, but I don't want to handle all that data, I was more interested in the text for whatever reason
