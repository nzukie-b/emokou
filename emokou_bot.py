#!/usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio
import os
import random
import argparse
import logging
import html
import db
from pixivpy_async import AppPixivAPI
from PIL import Image
from download import dl
from search import srch, top_n_images
from models import ImageData


async def _main():
    handler = [logging.FileHandler(filename="./emoakou_cli.log", encoding='utf-8')]
    logging.basicConfig(handlers=handler, format='%(levelname)s:%(message)s', level=logging.DEBUG)
    logging.info('STARTING')
    args = parser.parse_args()
    if (args.dl == 'y' and args.username and args.password):
        logging.info('DOWNLOADING IMAGES')
        try:
            await dl(aapi=aapi, username=args.username, password=args.password)
        except Exception as e:
            logging.exception(e)
    logging.info('SEARCHING IMAGES FOR ENTERED TEXT')
    found_images = list(srch(html.unescape(args.text)))
    limit = min(args.number, len(found_images))
    top_n_images(found_images, limit)
    logging.info('FINISHED')
    
def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_main(args, aapi=AppPixivAPI()))
