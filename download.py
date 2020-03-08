#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import pytesseract
import asyncio
import os
import html
import logging

from pixivpy_async import AppPixivAPI
from mongoengine import connect
from models import ImageData
from translate import Translator
from PIL import Image

tl = Translator(to_lang='en', from_lang='zh', email='nzukie.b@husky.neu.edu')
connect('emokou')

async def dl(aapi, username, password):
    """Download Emoting Mokou memes to the db"""
    await aapi.login(username, password)
    count, nonParsedCount, searched_count = 0, 0, 0
    next_offset = 1
    json_result = await aapi.search_illust('mokou', search_target='exact_match_for_tags', req_auth=False, filter=None)
    next_offset = get_next_offset(json_result)
    while next_offset != 0:
        directory = "tmp"
        if not os.path.exists(directory):
            os.makedirs(directory)
        for illust in json_result.illusts:
            searched_count += 1
            # 上官绯樱 | jokanhiyou
            if (illust.user.id != 4325914):
                continue
            count += 1
            image_url = illust.meta_single_page.get('original_image_url', illust.image_urls.large)
            logging.info("%s: %s" % (illust.title, image_url))
            try:
                url_basename = os.path.basename(image_url)
                extension = os.path.splitext(url_basename)[1]
                name = "illust_id_%d_%s%s" % (
                    illust.id, illust.title, extension)
                logging.info(directory + '\\' + name)
                await aapi.download(image_url, path=directory, name=name)
            except TimeoutError as e:
                logging.exception(e)
                continue
            try:
                if ImageData.objects(url=image_url):
                    logging.info('Image with url %s is already in the DB', image_url)
                    continue
                image = ImageData(url=image_url)
                try:
                    # The OCR library occasionally misenterprets I as |  ’ != '
                    parsedText = html.unescape(pytesseract.image_to_string(Image.open(
                        directory + '\\' + name), lang='chi_sim+eng').replace('|', 'I').replace('&#39;', '\''))
                    logging.info("PARSED TEXT: %s", parsedText)
                except TypeError as te:
                    logging.warn("CAN'T PARSE IMAGE WITH URL: %s  %s",image_url, te)
                    nonParsedCount += 1
                    parsedText = None
                    image.chi_cap = None
                    image.eng_cap = None
                    image.eng_tr = None
                    logging.info('NonParsed count = %d total count = %d', nonParsedCount, count)
                if parsedText:
                    parse_Image(parsedText, image)
                    image.img.put(open(directory + '\\' + name, 'rb'))
                image.save()
            except Exception as e:
                logging.warning('Failed on image with url: %s', image_url)
                logging.exception(e)
                continue
        json_result = await aapi.search_illust('mokou', search_target='exact_match_for_tags', offset=next_offset, req_auth=False, filter=None)
        next_offset = get_next_offset(json_result)
    logging.info('All Emoting Mokou images successfully downloaded. count = %d', count)
    logging.debug('TOTAL SEARCHED: %d', searched_count)
    return True


def parse_Image(parsedText, image):
    """Separates text into various images."""
    # Extract parsed 中文字
    image.chi_cap = re.findall(r'[\u4e00-\u9fff]', parsedText)
    # Add the rest of the parsed text to the caption
    image.eng_cap = re.findall(r"\w*[a-zA-Z]?\'?[a-zA-Z]", parsedText.upper())
    if (image.eng_cap):
        logging.info("ENG CHARS: %s", image.eng_cap)
    if (image.chi_cap):
        # Translate 中文 to english
        text = tl.translate(''.join(image.chi_cap)).upper()
        print('TRANSLATED TEXT: ',  text)
        # text = text.encode().decode('unicode-escape')
        image.eng_tr = text.split()
        logging.info('中文字：%s', image.chi_cap)
        logging.info('TRANSLATION: %s', image.eng_tr)
    return image


def get_next_offset(json_result):
    """Reads the current json_result for the offset if present."""
    return int(json_result.next_url[json_result.next_url.index('offset=') + 7:]) if (
        json_result.next_url is not None) else 0
