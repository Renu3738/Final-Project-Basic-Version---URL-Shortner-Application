import os
from flask import Flask,request,render_template,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
import string
from wtforms import validators
from flask_migrate import Migrate
from random import choice

app=Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite:///' + os.path.join(basedir,'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False

db = SQLAlchemy(app)
Migrate(app, db)

class Url(db.Model):
    __tablename__='urls'
    id= db.Column(db.Integer, primary_key= True)
    url_long= db.Column(db.Text)
    url_short= db.Column(db.Text)

    def __init__(self,url_long,url_short):
        self.url_long= url_long
        self.url_short= url_short

def shortURL(charlen):
    return ''.join(choice(string.ascii_letters+string.digits) for _ in range(charlen))

@app.route('/',methods=["GET","POST"])
def home():
    if request.method=="POST":
        url_long= request.form['url'] 
        currentUrl = Url.query.filter_by(url_long=url_long).first()
        if currentUrl:
            return render_template('home.html', error=0, finalurl=currentUrl.url_short)
        else:
            if validators.url(url_long):
                while True:
                    shortLink = shortURL(3)
                    url_short = Url.query.filter_by(url_short=shortLink).first()
                    if not url_short:
                        lnk=Url(url_long,shortLink)
                        db.session.add(lnk)
                        db.session.commit()
                        return render_template('home.html',error=0,finalurl=shortLink)
            else:
                return render_template('home.html',error=1)
    return render_template("home.html")

@app.route('/history',methods=["GET","POST"])
def history():
    lnks=Url.query.all()
    return render_template("history.html",hist=lnks)

@app.route('/<finalurl>')
def redirection(finalurl):
    fullurl = Url.query.filter_by(url_short=finalurl).first()
    if fullurl:
        return redirect(fullurl.url_long)
    else:
        return f"URL doesn't Exist"

@app.route('/delete/<int:id>')
def delete(id):
    item = Url.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    return redirect('/history')

if __name__=="__main__":
    app.run(debug=True)