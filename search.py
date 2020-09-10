#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import random
import logging
import db
from models import ImageData
from translate import Translator
from PIL import Image

found_images = set()
# db.remote_connect()
db.local_connect()

#TODO: Change the way that the seach works to allow usage of map
#NOTE: I probably don't need to have found_images be ts own thing. MINOR CHANGE
#NOTE: I need to break the text into to words/hanzi SOO this might not acutally be ideal..
def srch(text):
    """ Search the database to find containing the words of the entered text. 
        If no text if provided, searches for images without text."""
    logging.info('SEARCH TEXT %s', text)
    eng_text = re.findall(r'\w*[a-zA-Z]?\'?[a-zA-Z]', text.upper())
    chi_text = re.findall(r'[\u4e00-\u9fff]', text)
    logging.info("HANZI: %s", chi_text)
    logging.info("ENG CHARS: %s", eng_text)
    if not text:
        logging.info("SEARCHING FOR IMAGES WITHOUT TEXT")
        empty_srch()
    if len(text) <= 255:
        if chi_text:
            logging.info("SEARCHING BY CHINESE TEXT")
            for char in chi_text:
                chi_srch(char)
        if eng_text:
            logging.info("SEARCHING BY ENG TEXT CAPTIONS AND TRANSLATIONS IF PRESENT")
            for char in eng_text:
                eng_cap_srch(char)
                eng_tr_srch(char)
        logging.info("FOUND %d UNIQUE IMAGES", len(found_images))
        return found_images

def chi_srch(char):
    """Search the  chinese chars"""
    for image in ImageData.objects(chi_cap=char):
        found_images.add(image)

def eng_cap_srch(char):
    """Search the english captions"""
    for image in ImageData.objects(eng_cap=char):
        found_images.add(image)

def eng_tr_srch(char):
    """Search the english translation""" 
    for image in ImageData.objects(eng_tr=char):
        found_images.add(image)

def empty_srch():
    """ Search for Images without text captions """
    for image in ImageData.objects(eng_cap=[]):
        found_images.add(image)

def top_n_images(found_images, limit):
    """Opens up to 'limit' random images from 'found_images'""" 
    for i in range(0, limit):
            res = random.choice(found_images)
            # print("FOUND IMAGE: ", res)
            found_images.remove(res)
            show_img(res.img)

def show_img(img):
    "Displays the selected image."
    picture = Image.open(img)
    picture.show()
