#!/usr/bin/python3.5

import datetime
import io
import flask
import flask_cache
import PyRSS2Gen
import requests

__version__ = '0.1'

HEADERS = requests.utils.default_headers()
HEADERS.update({
    'User-Agent': 'reddit-rss:v{} (by /u/1337turtle)'.format(__version__)
})

# Max sure we don't waste bandwidth getting the largest image.
MAX_HEIGHT = 700
MAX_WIDTH = 1000

app = flask.Flask(__name__)
# Cache resulting rss feed so we don't spam reddit with too many requests.
cache = flask_cache.Cache(app, config={'CACHE_TYPE': 'simple'})


def get_preview_url(item):
    """Gets image url for displaying as preview.
    Returns None if not available."""
    if 'preview' not in item:
        return None
    # TODO: Is it possible to have more than one image?
    images = item['preview']['images'][0]

    # Pull gifs if we can.
    if 'variants' in images and 'gif' in images['variants']:
        images = images['variants']['gif']['resolutions']
    else:
        images = images['resolutions']

    # Reversed so we go from highest resolution to lowest.
    # for index in range(len(images)-1, 0, -1):
    for image in reversed(images):
        # image = images[index]
        if image['width'] <= MAX_WIDTH or image['height'] <= MAX_HEIGHT:
            return image['url']


@app.route('/r/<subreddit>')
@cache.memoize(timeout=60)
def produce_feed(subreddit):
    json_url = 'http://reddit.com/r/{}/.json?raw_json=1'.format(subreddit)
    response = requests.get(json_url, headers=HEADERS)
    if response.status_code != 200:
        flask.abort(response.status_code)

    feed = response.json()

    cached_feed = PyRSS2Gen.RSS2(
        generator='reddit-rss.com',
        docs='github.com/jpsnyder/reddit-rss',
        title=subreddit,
        link='TODO: {}'.format(subreddit),
        description=None,
        lastBuildDate=None,
    )

    for item in feed['data']['children']:
        item = item['data']

        # Extract preview url.
        try:
            item['preview_url'] = get_preview_url(item)
        except KeyError:
            item['preview_url'] = None

        cached_item = PyRSS2Gen.RSSItem(
            guid=u'https://www.reddit.com/{}'.format(item['permalink']),
            title=item['title'],
            link=item['permalink'],
            description=flask.render_template('rss_item.html', item=item),
            author=item['author'],
            pubDate=datetime.datetime.utcfromtimestamp(item['created_utc']))
        cached_feed.items.append(cached_item)

    output = io.StringIO()
    cached_feed.write_xml(output)
    output.seek(0)
    return output.read()


@app.route('/')
def index():
    return flask.render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
