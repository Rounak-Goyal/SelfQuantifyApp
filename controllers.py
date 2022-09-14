from datetime import datetime
from flask import Flask, redirect, url_for
from flask import render_template
from flask import request
from flask import current_app as app
from app import *

import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
from matplotlib import dates as mpdt

def plot_tracker(tracker_id, logs):
    x_list = []
    y_list = []
    for linker in logs:
        x_list.append(linker.timest)
        y_list.append(linker.t_value)

    plt.xlabel("TIMESTAMP")
    plt.ylabel("VALUE LOGGED")
    plt.title("Summary of your Logs")
    plt.tight_layout()

    plt.plot(x_list, y_list, '-rD')
    plt.gcf().autofmt_xdate()
    filename_path = "static/graphs/num_tracker_" + str(tracker_id) + ".png"
    plt.savefig(filename_path)
    plt.close()

    return filename_path



@app.route("/", methods=["GET", "POST"])
def login():
    if request.method=="GET":
        return render_template("login.html")

    if request.method=="POST":
        users = User.query.all()

        username = request.form["u"]
        password = request.form["p"]

        for user in users:
            if username == user.username and password == user.password:
                #print("Logged in successfully")
                cuser = User.query.filter(User.username == username).one()
                uid = cuser.user_id
                #print(uid)
                return redirect(url_for("index", uid=uid))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method=="GET":
        return render_template("sign-up.html")

    if request.method=="POST":

        uname = request.form["uname"]
        fname = request.form["fname"]
        passw = request.form["pass"]
        cpass = request.form["cpass"]

        users = User.query.all()
        for user in users:
            if user.username == uname:
                return redirect(url_for("signup"))
            
        if passw == cpass:
            new_user = User(username=uname, password=passw, fname=fname)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for("login"))

@app.route("/index/<int:uid>", methods=["GET", "POST"])
def index(uid):
    if request.method=="GET":
        trackers = Tracker.query.filter(Tracker.u_id == uid)
        tlist = []
        tnlist = []
        for tracker in trackers:
            tlist.append(tracker.t_id)
            tnlist.append((tracker.t_id,tracker.t_name))

        llist = []
        linkers = Linker.query.filter(Linker.tl_id.in_(tlist)).order_by(Linker.l_id.desc()).limit(5).all()
        for linker in linkers:
            for t in tnlist:
                if linker.tl_id == t[0]:
                    llist.append((t[1], linker.timedr, linker.t_value, linker.timest, linker.comm, t[0]))
        
        cuser = User.query.filter(User.user_id == uid).one()
        uname = cuser.fname
        return render_template("index.html", trackers=trackers, uid=uid, uname=uname, llist = llist)

@app.route("/tracker/<int:uid>/<int:tracker_id>", methods=["GET", "POST"])
def tracker(tracker_id, uid):
    if request.method=="GET":
        tracker = Tracker.query.filter(Tracker.t_id == tracker_id).one()
        trackers = Tracker.query.filter(Tracker.u_id == uid)
        linkers = Linker.query.filter(Linker.tl_id == tracker_id)
        cuser = User.query.filter(User.user_id == uid).one()
        uname = cuser.fname

        imgloc = plot_tracker(tracker_id, linkers)
        print(imgloc)
        if tracker.t_type == "Mood":
            mood = [(4,"Happy"),(3,"Normal"),(2,"Sad"),(1,"Angry")]
            mlist = []
            for linker in linkers:
                for m in mood:
                    if linker.t_value == m[0]:
                        mlist.append((linker.timest, m[1], linker.comm, linker.tl_id, linker.l_id))
            return render_template("Mood.html", tracker=tracker, trackers=trackers, mlist=mlist, uid=uid, uname=uname, imgloc=imgloc)
        else:
            return render_template("Numerical.html", tracker=tracker, trackers=trackers, linkers=linkers, uid=uid, uname=uname, imgloc=imgloc)
    
    if request.method=="POST":
        dt = request.form["dt"]
        dt = dt.replace('T',' ')
        dt = datetime.strptime(dt, '%Y-%m-%d %H:%M')
        dur = request.form["dur"]
        val = request.form["val"]
        notes = request.form["notes"]

        #print(dt,dur,val,notes)

        new_rec = Linker(tl_id=tracker_id, t_value=val, timest=dt, timedr=dur, comm=notes)
        db.session.add(new_rec)
        db.session.commit()
        return redirect(url_for("tracker", tracker_id=tracker_id, uid=uid))

@app.route("/tracker/mood/<int:uid>/<int:tracker_id>", methods=["GET", "POST"])
def tracker_misc(tracker_id, uid):
    if request.method=="POST":
        dt = request.form["dt"]
        dt = dt.replace('T',' ')
        dt = datetime.strptime(dt, '%Y-%m-%d %H:%M') 
        mood = int(request.form["radio-inline"])
        notes = request.form["notes"]

        #print(dt,mood,notes)

        new_mood = Linker(tl_id=tracker_id, t_value=mood, timest=dt, timedr=0, comm=notes)
        db.session.add(new_mood)
        db.session.commit()
        return redirect(url_for("tracker", tracker_id=tracker_id, uid=uid))

@app.route("/tracker/create/<int:uid>", methods=["GET", "POST"])
def add_tracker(uid):
    if request.method=="GET":
        trackers = Tracker.query.filter(Tracker.u_id == uid)
        cuser = User.query.filter(User.user_id == uid).one()
        uname = cuser.fname
        return render_template("AddTracker.html", trackers=trackers, uid=uid, uname=uname)

    if request.method=="POST":
        tname = request.form["tname"]
        tdesc = request.form["tdesc"]
        ttype = request.form["ttype"]

        #print(tname,tdesc,ttype)
        
        new_tr = Tracker(u_id=uid, t_name=tname, desc=tdesc, t_type=ttype)
        db.session.add(new_tr)
        db.session.commit()
        return redirect(url_for("index", uid=uid))

@app.route("/tracker/deletelinker/<int:uid>/<int:tracker_id>/<int:lid>", methods=["GET", "POST"])
def del_log(tracker_id, uid, lid):
    if request.method=="GET":
        log = Linker.query.filter(Linker.l_id == lid).one()
        db.session.delete(log)
        db.session.commit()
        return redirect(url_for("tracker", tracker_id=tracker_id, uid=uid))

@app.route("/tracker/deletetracker/<int:uid>/<int:tracker_id>", methods=["GET", "POST"])
def delete_tracker(tracker_id, uid):
    if request.method=="GET":
        logs = Linker.query.filter(Linker.tl_id == tracker_id)
        for log in logs:
            db.session.delete(log)
        db.session.commit()

        deltr = Tracker.query.filter(Tracker.t_id == tracker_id).one()
        db.session.delete(deltr)
        db.session.commit()

        return redirect(url_for("index", uid=uid))

@app.route("/tracker/updatelinker/<int:uid>/<int:tracker_id>/<int:lid>", methods=["GET", "POST"])
def updt_log(tracker_id, uid, lid):
    if request.method=="GET":
        log = Linker.query.filter(Linker.l_id == lid).one()
        trackers = Tracker.query.filter(Tracker.u_id == uid)
        cuser = User.query.filter(User.user_id == uid).one()
        uname = cuser.fname
        return render_template("UpdateLog.html", uid=uid, trackers=trackers, uname=uname, lid=lid, tracker_id=tracker_id, log=log)

    if request.method=="POST":
        log = Linker.query.filter(Linker.l_id == lid).one()
        log.timedr = request.form["dur"]
        log.t_value = request.form["val"]
        log.comm = request.form["notes"]
        db.session.commit()

        return redirect(url_for("tracker", tracker_id=tracker_id, uid=uid))