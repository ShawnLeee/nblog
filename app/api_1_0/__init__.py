# encoding: utf-8
from flask import Blueprint
api = Blueprint('api', '__name__')

from . import authentication, comments, decorators, errors, posts, users
