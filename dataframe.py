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
from flask import request

app = Flask(__name__)

df = pd.read_csv('data/incident.csv')
df = df[['Number','Priority','Short Description','Configuration_Item','Resolved','Closure Details','Root_Cause_L1','Category_2','Contributing Factor']]
df['Resolved'] = pd.to_datetime(df['Resolved'])

df_rootcause = df.groupby(['Category_2', 'Root_Cause_L1'])


@app.route("/rca")
def rca_page():
    data_load()
    return render_template("index.html", title="Incident Roott Cause Analysis")

@app.route("/")
def home_page():
    data_load()
    return render_template("home.html", title="Automation of Production")

#Group by components
@app.route("/components")
def get_comps():
    df_comp = df.groupby('Category_2')['Number'].count().sort_values(ascending=False).to_frame().to_dict()
    return json.dumps(df_comp["Number"])

#Group by root cause1
@app.route("/root1")
def get_root1():
    df_comp = df.groupby('Root_Cause_L1')['Number'].count().sort_values(ascending=False).to_frame().to_dict()
    return json.dumps(df_comp["Number"])

#Group by root cause2
@app.route("/root2")
def get_root2():
    df_comp = df.groupby('Contributing Factor')['Number'].count().sort_values(ascending=False).to_frame().to_dict()
    return json.dumps(df_comp["Number"])

#Group by application
@app.route("/rootcause_by_apps")
def rootcause_by_apps():
    df_app = df.groupby('Configuration_Item')['Number'].count().sort_values(ascending=False).to_frame().head().to_dict()
    return json.dumps(df_app["Number"])

#Group by root cause 2 for specific component and root cause1
@app.route("/root/<comp>/<root1>")
def rc_by_root(comp,root1):
    df_rc = df[(df["Category_2"] == urllib.parse.unquote(comp)) & (df["Root_Cause_L1"] == urllib.parse.unquote(root1))]
    df_rc_gr = df_rc.groupby('Contributing Factor').Number.count().to_frame().to_dict()
    return json.dumps(df_rc_gr["Number"])

#Group by root cause 2 for specific app and root cause1
@app.route("/root/app/<app>/<root1>")
def rc_by_root_for_app(app,root1):
    df_rc = df[(df["Configuration_Item"] == urllib.parse.unquote(app)) & (df["Root_Cause_L1"] == urllib.parse.unquote(root1))]
    df_rc_gr = df_rc.groupby('Contributing Factor').Number.count().to_frame().to_dict()
    return json.dumps(df_rc_gr["Number"])

#Group by root cause 2 for specific app and root cause1
@app.route("/root/<root1>")
def rc_by_root_for_root1(root1):
    df_rc = df[(df["Root_Cause_L1"] == urllib.parse.unquote(root1))]
    df_rc_gr = df_rc.groupby('Contributing Factor').Number.count().to_frame().to_dict()
    return json.dumps(df_rc_gr["Number"])

#Group by root cause 1 for specific component
@app.route("/component/<comp>")
def rc_by_comp(comp):
    df_rc = df[df['Category_2'] == urllib.parse.unquote(comp)]
    df_rc_gr = df_rc.groupby('Root_Cause_L1').Number.count().to_frame().to_dict()
    return json.dumps(df_rc_gr["Number"])

#Group by root cause 1 for specific application
@app.route("/application/<app>")
def rc_by_app(app):
    df_rc = df[df['Configuration_Item'] == urllib.parse.unquote(app)]
    df_rc_gr = df_rc.groupby('Root_Cause_L1').Number.count().to_frame().to_dict()
    return json.dumps(df_rc_gr["Number"])

#Group by root cause 2 for specific root cause 1
@app.route("/root1/<r1>")
def rc1_by_rc2(r1):
    df_rc = df[df['Root_Cause_L1'] == urllib.parse.unquote(r1)]
    df_rc_gr = df_rc.groupby('Contributing Factor').Number.count().to_frame().to_dict()
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
    df = df[['Number','Priority','Short Description','Configuration_Item','Resolved','Closure Details','Root_Cause_L1','Category_2','Contributing Factor']]
    df['Resolved'] = pd.to_datetime(df['Resolved'])

@app.route("/root/<comp>/<root1>/<root2>")
def rc_by_detail(comp,root1,root2):
    pd.set_option('display.max_colwidth', -1)
    df_data = df[(df["Category_2"] == urllib.parse.unquote(comp)) & (df["Root_Cause_L1"] == urllib.parse.unquote(root1)) & (df["Contributing Factor"] == urllib.parse.unquote(root2))]
    print(df_data['Closure Details'])
    return df_data.to_html()

@app.route("/inc/<comp>/<root>", methods=["GET","POST"])
def inc_by_rc(comp,root):
    pd.set_option('display.max_colwidth', -1)
    if request.method == "POST":
        value = request.get_json()
        print(value)
        df_data = df[(df["Category_2"] == urllib.parse.unquote(comp)) & (df["Root_Cause_L1"] == urllib.parse.unquote(root)) & (df["Contributing Factor"].isin(value['key']))]
    else:
        df_data = df[(df["Category_2"] == urllib.parse.unquote(comp)) & (df["Root_Cause_L1"] == urllib.parse.unquote(root))]
    
    return df_data.to_html()

@app.route("/app/inc/<app>/<root>", methods=["GET","POST"])
def inc_by_app_rc(app,root):
    pd.set_option('display.max_colwidth', -1)
    if request.method == "POST":
        value = request.get_json()
        print(value)
        df_data = df[(df["Configuration_Item"] == urllib.parse.unquote(app)) & (df["Root_Cause_L1"] == urllib.parse.unquote(root)) & (df["Contributing Factor"].isin(value['key']))]
    else:
        df_data = df[(df["Configuration_Item"] == urllib.parse.unquote(app)) & (df["Root_Cause_L1"] == urllib.parse.unquote(root))]
    
    return df_data.to_html()


@app.route("/root1/inc/<root>", methods=["GET","POST"])
def inc_by_root1_rc(root):
    pd.set_option('display.max_colwidth', -1)
    if request.method == "POST":
        value = request.get_json()
        print(value)
        df_data = df[(df["Root_Cause_L1"] == urllib.parse.unquote(root)) & (df["Contributing Factor"].isin(value['key']))]
    else:
        df_data = df[(df["Root_Cause_L1"] == urllib.parse.unquote(root))]
    
    return df_data.to_html()

@app.route("/root2/inc/<root>", methods=["GET","POST"])
def inc_by_root2_rc(root):
    pd.set_option('display.max_colwidth', -1)
    df_data = df[(df["Contributing Factor"] == urllib.parse.unquote(root))]
    return df_data.to_html()

@app.route("/incident_by_mon/<comp>")
def inc_by_mon(comp):
    df_by_mon = df[(df["Category_2"] == urllib.parse.unquote(comp))]
    df_by_mon.index = df_by_mon['Resolved'] 
    df_by_mon = df_by_mon[['Number']].resample('M').count()
    df_by_mon['Resolved Date'] = df_by_mon.index.strftime('%b-%Y')
    return str(df_by_mon.to_dict(orient="records")).replace("'","\"")

@app.route("/incident_by_mon/app/<app>")
def inc_app_by_mon(app):
    df_by_mon = df[(df["Configuration_Item"] == urllib.parse.unquote(app))]
    df_by_mon.index = df_by_mon['Resolved'] 
    df_by_mon = df_by_mon[['Number']].resample('M').count()
    df_by_mon['Resolved Date'] = df_by_mon.index.strftime('%b-%Y')
    return str(df_by_mon.to_dict(orient="records")).replace("'","\"")

@app.route("/incident_by_mon/root1/<root1>")
def inc_root1_by_mon(root1):
    df_by_mon = df[(df["Root_Cause_L1"] == urllib.parse.unquote(root1))]
    df_by_mon.index = df_by_mon['Resolved'] 
    df_by_mon = df_by_mon[['Number']].resample('M').count()
    df_by_mon['Resolved Date'] = df_by_mon.index.strftime('%b-%Y')
    return str(df_by_mon.to_dict(orient="records")).replace("'","\"")

@app.route("/incident_by_mon/root2/<root2>")
def inc_root2_by_mon(root2):
    df_by_mon = df[(df["Contributing Factor"] == urllib.parse.unquote(root2))]
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
