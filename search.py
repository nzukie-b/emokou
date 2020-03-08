#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import random
import logging
from mongoengine import connect
from models import ImageData
from translate import Translator
from PIL import Image

connect('emokou')
found_images = set()

def srch(text):
    logging.info('SEARCH TEXT %s', text)
    eng_text = re.findall(r'\w*[a-zA-Z]?\'?[a-zA-Z]', text.upper())
    chi_text = re.findall(r'[\u4e00-\u9fff]', text)
    print("HANZI: ", chi_text)
    print("ENG CHARS: ", eng_text)
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

def top_n_images(found_images, limit):
    """Opens up to 'limit' randcom images from 'found_images'""" 
    for i in range(0, limit):
            res = random.choice(found_images)
            # print("FOUND IMAGE: ", res)
            found_images.remove(res)
            picture = Image.open(res.img)
            picture.show()
