import sys
import os
import json, requests
from urllib import urlretrieve

class FileSpoof():
    def __init__(self, data):
        self.data = data
        
    def read(self):
        return self.data

def clean_ext(img_url):
    ext = img_url.split('.')[-1]

    ext = ext if not '?' in ext else ext[:ext.index('?')]

    #print ext
    return ext

def clean_url(img_url):
    split = img_url.split('.')
    return '.'.join(split[:-1]) + '.' + clean_ext(img_url)

def get_first_google_imgs_page(search_term):
    search_url = 'http://ajax.googleapis.com/ajax/services/search/images?v=1.0&q={}&start=0'

    response = requests.get(search_url.format(search_term))
    if not response.ok:
        raise LookupError("Trouble getting", search_url.format(search_term))

##    print "Fetching first image for search term {}, saving to {}".format(
##        search_term, filepath)

    result = json.load(FileSpoof(response.text))

    img_urls = [clean_url(result["responseData"]["results"][i]["unescapedUrl"]) \
                for i in range(4)]

    return img_urls

def download_img(img_url, save_name, save_dir):
    #saves the image from img_url to save_dir/save_name.ext, where ext
    #is the extension used in img_url
    #save_dir is made if it doesn't already exist
    ext = img_url.split('.')[-1]

    save_path = '.'.join((os.path.join(save_dir, save_name), ext))

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    return urlretrieve(img_url, save_path)

def get_first_google_img(search_term, save_dir):
    img_url = get_first_google_imgs_page(search_term)[0]

    return download_img(img_url, search_term, save_dir)
