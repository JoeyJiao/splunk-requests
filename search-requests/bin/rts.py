#!/usr/bin/env python

import sys
import time
import requests
import json

from splunklib.searchcommands import dispatch, GeneratingCommand, Configuration, Option

@Configuration()
class RtsCommand(GeneratingCommand):
    """ Generates events that are the result of a query via requests to rest api

    ##Syntax

    .. code-block::
        | requests method=get url="http://localhost/rest/api"


    ##Description

    The :code:`requests` issue a query to rest api interface, where the method specifies requests method. And get is the default method.


    ##Example

    .. code-block::
        | requests method=get url="http://localhost/rest/api"
    """
    url = Option(doc='', require=True)

    method = Option(doc='', require=False, default='get')

    data = Option(doc='', require=False, default=None)

    kwargs = Option(doc='', require=False, default='{}')

    maxretry = Option(doc='', require=False, default=5)

    def generate(self):
        self.logger.debug('Start query')

        attempt_count = 0

        try:
            func = getattr(requests, self.method)
            while 1:
                resp = func(self.url, self.data, **json.loads(self.kwargs)) if self.data else func(self.url, **json.loads(self.kwargs))
                if resp.status_code < 300:
                    break
                elif resp.status_code in range(400, 500):
                    self.logger.error("Failed to {} {}, resp={} <{}>".format(self.method.upper(), self.url, resp.status_code, resp.text))
                    raise
                else: # Server side issue
                    self.logger.warn("Failed to {} {}, resp={} <{}>, retrying again".format(self.method.upper(), self.url, resp.status_code, resp.text))
                    if attempt_count > self.maxretry:
                        self.logger.error("Failed to {} {}, resp={} <{}> after retrying".format(self.method.upper(), self.url, resp.status_code, resp.text))
                        raise
                    attempt_count += 1
                    sleep(10)

            if self.method in ['get', 'delete']:
                result = json.loads(resp.text)
            else:
                result = resp

            if type(result) == list:
                for hit in result:
                    yield self.getEvent(hit)
            elif type(result) == dict:
                yield self.getEvent(result)
            elif type(result) in [unicode, str]:
                for hit in result.split('\n'):
                    yield self.getEvent(hit)
            else:
                yield self.getEvent(result)
        except AttributeError as e:
            raise e
        except Exception as e:
            raise e

    def getEvent(self, result):
        event = {
            '_time': time.time(),
            '_raw': result
        }

        return event

    def __init__(self):
        super(GeneratingCommand, self).__init__()

dispatch(RtsCommand, sys.argv, sys.stdin, sys.stdout, __name__)
