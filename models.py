#!/usr/bin/env python
# -*- coding: utf-8 -*-
from mongoengine import *
from mongoengine.fields import ImageField, ListField, StringField, URLField


class ImageData(Document):
    url = URLField(max_length=255, required=True)
    eng_cap = ListField(StringField())
    eng_tr = ListField(StringField())
    chi_cap = ListField(StringField())
    img = ImageField()
