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
        generator=u'reddit-rss.com',
        docs=u'github.com/jpsnyder/reddit-rss',
        title=feed['feed'].get('title'),
        link=feed['feed'].get('link'),
        description=feed['feed'].get('description'),
        lastBuildDate=feed['feed'].get('updated'))

    for entry in feed['entries']:
        # TODO: Add extra info: 'author_detail',
        cached_entry = PyRSS2Gen.RSSItem(
            guid=entry['id'],
            title=entry['title'],
            link=entry['link'],
            description=entry['description'],
            author=entry['author'],
            # summary=entry['summary'],
            pubDate=entry['updated'],
            comments=None,
        )
        cached_feed.items.append(cached_entry)


    # TODO: Is there a way to avoid the StringIO nonsense?
    output = io.StringIO()
    cached_feed.write_xml(output)
    output.seek(0)
    return output.read()


if __name__ == '__main__':
    app.run(debug=True)
