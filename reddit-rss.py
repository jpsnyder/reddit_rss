#!/usr/bin/python3.5

import datetime
import io
import feedparser
import flask
import flask_cache
import PyRSS2Gen
import requests

app = flask.Flask(__name__)
# Cache resulting rss feed so we don't spam reddit with too many requests.
cache = flask_cache.Cache(app, config={'CACHE_TYPE': 'simple'})


def parse_rss_feed(rss_url):
    feed = feedparser.parse(rss_url)



@app.route('/')
@app.route('/r/<subreddit>')
@cache.memoize(timeout=60)
def produce_feed(subreddit='frontpage'):
    json_url = 'http://reddit.com/r/{}.json'.format(subreddit)
    response = requests.get(json_url)
    if response.status_code != 200:
        flask.abort(response.status_code)

    feed = response.json()

    cached_feed = PyRSS2Gen.RSS2(
        generator='reddit-rss.com',
        docs='github.com/jpsnyder/reddit-rss',
        title='TODO: {}'.format(subreddit),
        link='TODO: {}'.format(subreddit),
        description=None,
        lastBuildDate=None,
    )

    for item in feed['data']['children']:
        item = item['data']

        cached_item = PyRSS2Gen.RSSItem(
            guid=u'https://www.reddit.com/{}'.format(item['permalink']),
            title=item['title'],
            link=item['permalink'],
            description=flask.render_template('rss_item.html', item=item),
            author=item['author'],
            pubDate=datetime.datetime.utcfromtimestamp(item['created_utc']))
            # thumbnail=item['thumbnail'])
        cached_feed.items.append(cached_item)


    # rss_url = 'http://reddit.com/r/{}.rss'.format(subreddit)
    # feed = feedparser.parse(rss_url)
    # cached_feed = PyRSS2Gen.RSS2(
    #     generator=u'reddit-rss.com',
    #     docs=u'github.com/jpsnyder/reddit-rss',
    #     title=feed['feed'].get('title'),
    #     link=feed['feed'].get('link'),
    #     description=feed['feed'].get('description'),
    #     lastBuildDate=feed['feed'].get('updated'))
    #
    # for entry in feed['entries']:
    #     # TODO: Add extra info: 'author_detail',
    #     cached_entry = PyRSS2Gen.RSSItem(
    #         guid=entry['id'],
    #         title=entry['title'],
    #         link=entry['link'],
    #         description=entry['description'],
    #         author=entry['author'],
    #         # summary=entry['summary'],
    #         pubDate=entry['updated'],
    #         comments=None,
    #     )
    #     cached_feed.items.append(cached_entry)


    output = io.StringIO()
    cached_feed.write_xml(output)
    output.seek(0)
    return output.read()


if __name__ == '__main__':
    app.run(debug=True)
