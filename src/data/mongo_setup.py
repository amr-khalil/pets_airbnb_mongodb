import mongoengine
from mongoengine import connect

mongodb_url = "mongodb+srv://amrmaro:1POXTfbHRswb85IL@cluster0.raket.mongodb.net/?retryWrites=true&w=majority"
def global_init():
    connect(host=mongodb_url, alias="core", db="pets-bnb")
    
 