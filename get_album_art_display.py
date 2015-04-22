from __future__ import print_function

import pygame as pg
import sys, os, time, random, math
from useful import load_image, colors
from textFuncs import *
from urllib import urlretrieve
from PIL import Image

import threading

from functools import partial

import google_imgs as gi

DEFAULTS = {
    "save_path": os.path.join(os.curdir, "resource")
    }

print_r = partial(print, end="\r")

##SET-UP##

if not __name__=="__main__":
    #this is a "final" .py
    sys.exit(0)

def get_imgs(search_term, callback=print_r):
    load_str = "Loading images for {}".format(search_term)
    
    img_urls = gi.get_first_google_imgs_page(search_term)    #4 image urls

    tmp_files = []
    for i, url in enumerate(img_urls):
        callback(load_str+"\n{} of {}".format(i+1, len(img_urls)))

        tmp_files.append(urlretrieve(url)[0])

    callback("Finished loading")

    return tmp_files

def disp_cb(*s):
    #a callback with the same model as our modified print function,
    #but the strings given in *s are put onto the pygame screen
    screen.fill(colors.black)

    msg = filter(None, ' '.join(s).split('\n'))
    
    texts = [textOutline(fontL, m, white, black) for m in msg]
    n = len(texts)
    h = texts[0].get_rect().height
    
    for i, text in enumerate(texts):
        screen.blit(text, text.get_rect(center=(width/2,
                            height/2-h*n/2+h*i)))
    
    pg.display.flip()

if len(sys.argv) == 1:
    #we've been called with no arguments, so get every album cover we need to

    #check_artwork is a script which does what it says on the tin, saving
    #the results into _missing_albums.txt
    os.system("check_artwork.py")
    print('\n')

    #it's worth noting that if there's nothing found, this file
    #will still exist
    f = open(os.path.join(save_path, "_missing_albums.txt"))
    missing_albums = filter(None, f.read().split('\n'))
    
    tmp_files = ((s, get_imgs(s, disp_cb)) for s in missing_albums)

    save_path = DEFAULTS["save_path"]
else:
    search_term = ' '.join(sys.argv[1:-1])
    save_path = sys.argv[-1]

    #TODO: make os-independant
    #use argparse for fuck's sake
    if not save_path.startswith("C:"):      #vom
        #we haven't been given a save_path, so the last arg is part of
        #the search term!
        search_term += (' ' if search_term else '') + save_path

        save_path = DEFAULTS["save_path"]

    #single-element generator
    tmp_files = ((search_term, get_imgs(search_term)) for _ in '.')

##END SET-UP##

#this could do with generalising (TODO)
size = width, height = 1800, 1010
os.environ["SDL_VIDEO_WINDOW_POS"] = "{},{}".format(
    (1920-width)/2, (1080-height)/2)

pg.init()

##size = width, height = 1800, 1010
fps_tgt = 30
clock = pg.time.Clock()

font = pg.font.SysFont("calibri", 16)

def load_imgs(img_files):
    imgs = []
    for i, tmp in enumerate(img_files):
        try:
            img = load_image(tmp)
        except SystemExit, msg:
            print("Can't load {}".format(tmp))
            continue

        imgs.append(img)

    #resize
    for i, img in enumerate(imgs):
        size = img.get_size()
        tgt = (2*width/3, 4*height/5)       #target dimensions

        scalar = max(size[j]/float(tgt[j]) for j in [0, 1])

        resized = pg.transform.scale(img,
                                     map(int, (size[0]/scalar, size[1]/scalar)))

        imgs[i] = (resized,
                   resized.get_rect(center=(width/2, height/2)),
    ##               font.render("Resolution: {}".format(img.get_size()),
    ##                           0, colors.black),
                   img.get_size(), img    #original resolution
                   )

    return imgs

try:
    search_term, next_files = next(tmp_files)

    #we don't set mode until here because then we don't get a black screen
    #flash up in the case where we just exit immediately - i.e. when all the
    #artwork is present
    screen = pg.display.set_mode(size)
    
    imgs = load_imgs(next_files)
    selected_img = 0
except StopIteration:
    #All artwork present
    pg.quit()
    
    os.system("pause")
    
    sys.exit()

def fix_caption(search_term, img_no, resolution):
    s = "{} - Image#: {}, Original resolution: ({}x{})"
    pg.display.set_caption(s.format(
                                search_term,
                                img_no + 1,
                                resolution[0],
                                resolution[1]
                                )
                           )

fix_caption(search_term, 0, imgs[0][2])

while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

        if event.type == pg.MOUSEBUTTONDOWN:
            m1, m3, m2 = pg.mouse.get_pressed()
            mX, mY = pg.mouse.get_pos()

            if m1:
                #we've picked the artwork we want

                #hardcoding .jpg seems dodgy (TODO)
                file_save_path = os.path.join(save_path, search_term) + ".jpg"
                pg.image.save(imgs[selected_img][3],    #original resolution
                              file_save_path)

                print("Saved selection to {}".format(file_save_path))

                try:
                    search_term, next_files = next(tmp_files)
                    imgs = load_imgs(next_files)
                    selected_img = 0

                    fix_caption(search_term, 0, imgs[0][2])
                except StopIteration:
                    pg.quit()
                    sys.exit()

        if event.type == pg.KEYDOWN:
            keys = pg.key.get_pressed()

            if keys[pg.K_ESCAPE]:
                pg.quit()
                sys.exit()

            if keys[pg.K_LEFT] or keys[pg.K_RIGHT]:
                selected_img = (selected_img + 2*keys[pg.K_RIGHT]-1) % len(imgs)
                fix_caption(search_term, selected_img, imgs[selected_img][2])

    screen.fill(colors.white)

    img = imgs[selected_img]

    screen.blit(img[0], img[1])
    #screen.blit(img[2], (10, 10))

##    imgs[selected_img].draw(screen)
    
    pg.display.flip()

    clock.tick(fps_tgt)
