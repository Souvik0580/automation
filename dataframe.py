#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug  7 10:45:12 2020

@author: souvik
"""
from flask import Flask
from flask import redirect, url_for
from flask import render_template
import pandas as pd
from random import random
import json
import urllib.parse
from datetime import datetime
from dateutil.parser import parse

app = Flask(__name__)

df = pd.read_csv('data/incident.csv')
df = df[['Number','Priority','Short Description','Configuration Item','Resolved','Closure Details','Root Cause','Component Views','Contributing Factor']]
df['Resolved'] = pd.to_datetime(df['Resolved'])

df_rootcause = df.groupby(['Component Views', 'Root Cause'])


@app.route("/")
def index_page():
    data_load()
    return render_template("index.html", title="Title Page of Hello App")

@app.route("/components")
def get_comps():
    df_comp = df.groupby('Component Views')['Number'].count().sort_values(ascending=False).to_frame().to_dict()
    return json.dumps(df_comp["Number"])

@app.route("/rootcause_by_apps")
def rootcause_by_apps():
    df_app = df.groupby('Configuration Item')['Number'].count().sort_values(ascending=False).to_frame().head().to_dict()
    return json.dumps(df_app["Number"])

@app.route("/root/<comp>/<root1>")
def rc_by_root(comp,root1):
    df_rc = df[(df["Component Views"] == urllib.parse.unquote(comp)) & (df["Root Cause"] == urllib.parse.unquote(root1))]
    df_rc_gr = df_rc.groupby('Contributing Factor').Number.count().to_frame().to_dict()
    return json.dumps(df_rc_gr["Number"])

@app.route("/component/<comp>")
def rc_by_comp(comp):
    df_rc = df[df['Component Views'] == urllib.parse.unquote(comp)]
    df_rc_gr = df_rc.groupby('Root Cause').Number.count().to_frame().to_dict()
    return json.dumps(df_rc_gr["Number"])

@app.route("/incidents/<start>/<end>")
def rc_by_date(start,end):
    global df
    data_load()
    df = df[(df['Resolved'] > parse(start)) & (df['Resolved'] < parse(end))];
    #df = df_dt;
    return df.to_html()

def data_load():
    global df
    df = pd.read_csv('data/incident.csv')
    df = df[['Number','Priority','Short Description','Configuration Item','Resolved','Closure Details','Root Cause','Component Views','Contributing Factor']]
    df['Resolved'] = pd.to_datetime(df['Resolved'])

@app.route("/root/<comp>/<root1>/<root2>")
def rc_by_detail(comp,root1,root2):
    pd.set_option('display.max_colwidth', -1)
    df_data = df[(df["Component Views"] == urllib.parse.unquote(comp)) & (df["Root Cause"] == urllib.parse.unquote(root1)) & (df["Contributing Factor"] == urllib.parse.unquote(root2))]
    print(df_data['Closure Details'])
    return df_data.to_html()

@app.route("/inc/<comp>/<root>")
def inc_by_rc(comp,root):
    pd.set_option('display.max_colwidth', -1)
    df_data = df[(df["Component Views"] == urllib.parse.unquote(comp)) & (df["Root Cause"] == urllib.parse.unquote(root))]
    print(df_data['Closure Details'])
    return df_data.to_html()

@app.route("/incident_by_mon/<comp>")
def inc_by_mon(comp):
    df_by_mon = df[(df["Component Views"] == urllib.parse.unquote(comp))]
    df_by_mon.index = df_by_mon['Resolved'] 
    df_by_mon = df_by_mon[['Number']].resample('M').count()
    df_by_mon['Resolved Date'] = df_by_mon.index.strftime('%b-%Y')
    return str(df_by_mon.to_dict(orient="records")).replace("'","\"")
    
@app.route("/data/")
def data():
    return df_rootcause.to_html()

@app.route("/user/<username>/")
def hello_user(username):
    return "Hello " + username + "!!!"

@app.route("/user/<username>/<int:age>/")
def display_age(username, age):
    age = age + 1
    return "Hello " + username +"!!!<br>You are " + str(age) + " years old."

@app.route("/home/")
def demo_redirect():
    return redirect("http://localhost:5000/")

@app.route("/greet/user/<uname>")
def greet_user(uname):
   return redirect(url_for('hello_user', username=uname))


if __name__ == '__main__':
    app.run(debug=True)
