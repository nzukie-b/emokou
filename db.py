from mongoengine import connect

def remote_connect():
    db_uri = 'mongodb+srv://meihong:tengyuan@emokou1-9co8z.mongodb.net/test?retryWrites=true&w=majority'
    db = connect(host=db_uri)
    return db

def local_connect():
    db = connect('emokou')
    return db


    