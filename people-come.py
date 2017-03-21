#!/usr/bin/env python3

#
# Copyright (c) Rui-Jie Fang
#
# Random script to get github peoplez
#

import requests
import json
from threading import Thread
from sys import argv
import os

github_api_endpoint = 'https://api.github.com/users'
is_finished = False


def exec_async(user_name, username, user_email):
    for c in ('git config user.name ' + user_name,
              'git config user.email ' + user_email,
              'echo "' + user_name + ' '
                  + 'https://github.com/' + username + ' - '
                  + user_email + '"' + '>> ' + username + '.txt',
              'git add *',
              'git commit -am ' + '"@' + username + '"'):
        os.system(c)


def async_exec_git(user_name, username, user_email):
    Thread(target=exec_async(user_name, username, user_email))


do_push = (lambda: (Thread(target=os.system(), args=['git push'])).start())


def main():
    g_this = None
    g_next = None

    def get_raw():
        nonlocal g_this, g_next
        get = requests.get(github_api_endpoint)
        get_headers = get.headers
        g_this = get.json()
        get_links = requests.utils.parse_header_links(get_headers['link'])
        marked = False
        for link in get_links:
            if link['rel'] == 'next':
                marked = True
                g_next = link['url']
        if not marked:
            g_next = None

    def process_user():
        nonlocal g_this
        profiles = []
        for user in g_this:
            user_url = requests.get(user['url']).json()
            if user_url['email'] is not None or user_url['email'] is not 'null':
                async_exec_git(user_url['name'], user_url['login'], user_url['email'])

    if g_this is None and g_next is None:
        get_raw()
        process_user()
        prev_counter = 0
        counter = 0
        while g_next is not None:
            get_raw()
            process_user()
            counter += prev_counter
            prev_counter = counter
            if counter == prev_counter * 3:
                do_push()


if __name__ == '__main__':
    main()
