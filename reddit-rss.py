#!/usr/bin/python3.5

import io
import feedparser
import flask
import PyRSS2Gen

app = flask.Flask(__name__)


def parse_rss_feed(rss_url):
    feed = feedparser.parse(rss_url)



@app.route('/')
@app.route('/<subreddit>')
@app.route('/r/<subreddit>')
def produce_feed(subreddit='frontpage'):
    rss_url = 'http://reddit.com/r/{}.rss'.format(subreddit)
    feed = feedparser.parse(rss_url)
    cached_feed = PyRSS2Gen.RSS2(
        title=feed['feed'].get('title'),
        link=feed['feed'].get('link'),
        description=feed['feed'].get('description'),
        lastBuildDate=feed['feed'].get('updated'))
    # TODO: Is there a way to avoid the StringIO nonsense?
    output = io.StringIO()
    cached_feed.write_xml(output)
    output.seek(0)
    return output.read()


if __name__ == '__main__':
    app.run(debug=True)
