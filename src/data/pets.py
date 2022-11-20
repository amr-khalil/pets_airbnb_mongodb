import datetime
import mongoengine

class Pet(mongoengine.Document):
    registered_date = mongoengine.DateTimeField(default=datetime.datetime.now)
    name = mongoengine.StringField(required=True)
    length = mongoengine.FloatField(required=True)
    species = mongoengine.StringField(required=True)
    is_dangerous = mongoengine.BooleanField(required=True)
    
    meta = {
        'db_alias': 'core',
        'collection': 'pets'
    }