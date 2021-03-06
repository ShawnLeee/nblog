# encoding: utf-8
from threading import Thread
import threading
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from Common import QBSpider
from app import config
from sqlalchemy.exc import IntegrityError, OperationalError
app = Flask(__name__)
app.config.from_object(config['development'])
db = SQLAlchemy(app)
spider = QBSpider()
max_page = 5


def main():
    threads = []
    for i in range(1, max_page):
        thread_t = Thread(target=append_author_for_page, args=(i,))
        threads.append(thread_t)

    for i in range(1, max_page):
        threads[i-1].start()

    for i in range(1, max_page):
        threads[i-1].join()


def append_author_for_page(page=1):
    authors = spider.get_authors(page=page)
    print("Get %d authors" % len(authors))
    print('Adding to datatbase...')
    for author in authors:
        db.session.add(author)
        try:
            db.session.commit()
            print(u'user:%s 插入成功' % author.user_name)
        except IntegrityError, reason:
            db.session.rollback()
            print('user:%s 插入失败:%s' % (author.user_name, reason))
            continue

    print('插入用户的糗事')
    for author in authors:
        posts = spider.get_articles_for_author(author.author_url)
        print('用户%s共有糗事%d条' % (author.user_name, len(posts)))
        for post_comment in posts:

            post = post_comment.get('post')
            comments = post_comment.get('comments')

            db.session.add(post)
            try:
                db.session.commit()
                print('Post:%s insert success' % post.post_id)
            except IntegrityError, reason:
                db.session.rollback()
                print('Post:%s insert failed,%s' % (post.post_id, reason))
                continue

            for comment in comments:
                db.session.add(comment)
                try:
                    db.session.commit()
                    print(u'糗事%s评论%s插入成功' % (post.post_id, comment.comment_id))
                except IntegrityError, reason:
                    db.session.rollback()
                    print(u'糗事%s评论%s插入失败:%s' % (post.post_id, comment.comment_id, reason))
                    continue
if __name__ == '__main__':
    main()