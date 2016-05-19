

from .. import db


def extract_pic_uid(picture_url):
  prefix = picture_url[:picture_url.index('jpg') - 1]
  return prefix[prefix.rfind('/') + 1:]

