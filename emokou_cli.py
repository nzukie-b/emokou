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


# db.remote_connect()
db.local_connect()
parser = argparse.ArgumentParser()
parser.add_argument("-dl", "--download", dest='dl', action="store", choices=['y', 'n'], default='n',
                    help="Whether to try downloading images from pixiv into the db.")
parser.add_argument("-u", "--username", dest='username', action="store",
                    help="Pixiv account username. Used to authenticate for download.")
parser.add_argument("-p", "--password", dest='password', action="store",
                    help="Pixiv account password. Used to authenticate for download.")
parser.add_argument("text", action="store", help="The text used to search by.")
parser.add_argument('-n', '--number', dest='number', action='store', type=int, default=5,
                    help='The max number of result images to open. Default = 5')
parser.add_argument('-d', '--debug', action='store_true',
                    default=False, help='To log debug info into a file.')

async def _main(*args, aapi):
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


def main(*args):
    args = parser.parse_args()
    if (args.number <= 0):
        print("Please increase the number of results to display. Must be greater than 1. Entered: ", args.number)
        return False
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_main(args, aapi=AppPixivAPI()))

main()
