import requests
import json


def make_gist(contents, time_string):
    r = requests.post('https://api.github.com/gists',
                      data=json.dumps({
                          'description': 'Comments for entry on %s' % time_string,
                          'public': False,
                          'files': {
                              'comments_%s.md' % time_string: {
                                  'content': contents
                              }
                          }
                      })
                      )
    response = r.content.decode('utf-8')
    response_json = json.loads(response)
    return response_json['html_url']

