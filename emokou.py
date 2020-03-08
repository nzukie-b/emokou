#!/usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio
import os
import random
from pixivpy_async import AppPixivAPI
from PIL import Image
from download import dl
from search import srch
from models import ImageData
from mongoengine import connect
connect('emokou')


async def _main(aapi):
    redownload = input("Do you want to redownload the MEMES? (y/n) \n")
    if (redownload.lower() == 'y'): 
        _USERNAME = input('Enter your pixiv username.\n')
        _PASSWORD = input('Enter your pixiv password.\n')
        try:
            await dl(aapi = aapi, username=_USERNAME, password=_PASSWORD)
            print('All good.')
        except TypeError as te:
            print("Invalid login credentials. Please try again.")
    search_text = input("Enter text to search for.\n")
    found_images = list(srch(search_text))
    limit = min(5, len(found_images))
    print("SHOWING : ", limit)
    for i in range(0, limit):
        # filename = found_images[i].url
        res = random.choice(found_images)
        print("FOUND IMAGE: ", res)
        found_images.remove(res)
        picture = Image.open(res.img)
        picture.show()
        
def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_main(AppPixivAPI()))

main()

