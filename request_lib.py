from datetime import datetime, timedelta
from time import sleep
import time
from typing import Dict, List
import requests
import os
from ratelimiter import RateLimiter

headers = {
    'content-type': 'application/json',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0',
    'Cookie': 'POESESSID=ae11a4dd8cde44395e1af0fe47bad8f5; cf_clearance=OoYUPCFnHFzscJz3hVgzcHH8R8Kt_HZj1BpukWU8w5A-1723622586-1.0.1.1-mL2cJOHAzhfeE0g36a3GMK39OFeZpXzc6r9DixsYOk658oNUtTpJ.ZV7XseA9PvJGVJmqPGAmvOo24LInPOMCQ'
}

# mode = "Ip"
mode = "Account"


class Queue:
    queue = List[datetime.date]

    def __init__(self):
        self.queue = []

    def add(self):
        self.queue = [datetime.utcnow(), *self.queue]

    def get_sleep_time(self, time_interval: int, max_requests: int) -> timedelta:
        if len(self.queue) < max_requests + 1:
            return timedelta(seconds=0)
        return max(timedelta(seconds=0), self.queue[max_requests] - datetime.utcnow() + timedelta(seconds=time_interval))

    def __str__(self):
        now = datetime.utcnow()
        return "\n".join(str(i) for i in self.queue)


class RequestHandler:

    def __init__(self):
        self.headers = headers
        self.cookies = {}
        self.get_is_initialized = False
        self.make_limited_get_request = None
        self.post_is_initialized = False
        self.make_limited_post_request = None
        self.queue: dict[str, Queue] = {"GET": Queue(), "POST": Queue()}
        self.current_league = self.set_league()

    def set_league(self):
        # response = requests.get(
        #     'https://api.pathofexile.com/leagues', headers=self.headers, cookies=self.cookies)
        # for league in response.json():
        #     if league['rules'] == [] and league["category"].get("current", False):
        #         return league['id']
        return "Hardcore Settlers"  # if league cant be found

    def trade_fetch(self, post_response):
        url_hash = post_response.json()['id']
        results = post_response.json()['result']
        for items in [','.join(results[n: n + 10]) for n in range(0, len(results), 10)]:
            url = f"""https://www.pathofexile.com/api/trade/fetch/{
                items}?query={url_hash}"""
            response = self.make_request(url, 'GET')
            for result in response.json()['result']:
                yield result

    def make_request(self, url, method, data=None, retry=False):
        if method == 'GET':
            response = self.make_get_request(url, self.headers, self.cookies)
        elif method == 'POST':
            response = self.make_post_request(
                url, self.headers, self.cookies, data)
        else:
            return None
        if response.status_code > 399:
            if retry:
                raise ConnectionError(response.text)
            for state in response.headers[f'X-Rate-Limit-Ip-State'].split(','):
                _, _, timeout = state.split(':')
                if timeout != '0':
                    print(f"Sleeping for {timeout} seconds")
                    sleep(int(timeout) + 10)
            for state in response.headers[f'X-Rate-Limit-Account-State'].split(','):
                _, _, timeout = state.split(':')
                if timeout != '0':
                    print(f"Sleeping for {timeout} seconds")
                    sleep(int(timeout) + 10)
            response = self.make_request(url, method, data, retry=True)
        return response

    def initialize_limited_request(self, response_headers, method):
        policies = response_headers[f'X-Rate-Limit-{mode}']
        current_states = response_headers[f'X-Rate-Limit-{mode}-State']
        limiters = [RateLimiter(period=1, max_calls=10000) for _ in range(3)]
        for idx, policy, state in zip(range(3), policies.split(','), current_states.split(',')):
            request_limit, period, _ = policy.split(':')
            current_state, _, _ = state.split(':')
            limiter = RateLimiter(period=int(
                int(period) * 1.2), max_calls=int(request_limit))
            limiter.calls.extend(time.time() for _ in range(
                int(current_state)))  # add previous requests to queue
            limiters[idx] = limiter

        @limiters[0]
        @limiters[1]
        @limiters[2]
        def limit_request_function(url, headers, cookies, data=None):
            if data:
                return getattr(requests, method)(url, headers=headers, cookies=cookies, json=data)
            return getattr(requests, method)(url, headers=headers, cookies=cookies)
        return limit_request_function

    def make_get_request(self, url, headers, cookies):
        if self.get_is_initialized:
            return self.make_limited_get_request(url, headers, cookies)
        else:
            response = requests.get(url, headers=headers, cookies=cookies)
            self.make_limited_get_request = self.initialize_limited_request(
                response.headers, "get")
            self.get_is_initialized = True
            return response

    def make_post_request(self, url, headers, cookies, data):
        if self.post_is_initialized:
            return self.make_limited_post_request(url, headers, cookies, data)
        else:
            response = requests.post(
                url, headers=headers, cookies=cookies, json=data)
            self.make_limited_post_request = self.initialize_limited_request(
                response.headers, "post")
            self.post_is_initialized = True
            return response

    def iterate_trade(self, data):
        url = f"""https://www.pathofexile.com/api/trade/search/{
            self.current_league}"""
        response = self.make_request(url, 'POST', data)
        for result in self.trade_fetch(response):
            yield result
