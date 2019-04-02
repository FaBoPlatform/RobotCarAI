import glob
import os
import sys
import re

def get_download_link(url, title):
    html = '<a href="'+url+'" download>' + title + '</a>\n'
    return html

def declare_variables(variables, macro):
    @macro
    def download_link(url, title):
      return get_download_link(url, title)

if __name__ == '__main__':
    url = sys.argv[1]
    title = sys.argv[2]
    element = get_download_link(url, title)

    print(element)
