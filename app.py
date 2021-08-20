from static.modules.costant_var import *
from flask import Flask , render_template, request, redirect
from flask_pymongo import PyMongo
from bson.json_util import loads, dumps
from flask_login import login_required, login_user, LoginManager, logout_user, current_user, UserMixin,AnonymousUserMixin
from flask_sqlalchemy import SQLAlchemy
import time

app = Flask(__name__)
app.config["SECRET_KEY"] = SECRET_VAR["SECRET"]
#app.config["MONGO_URI"] = "mongodb://localhost:27017/workcalender"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database/login.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["MONGO_URI"] = f"mongodb+srv://{SECRET_VAR['SERVER_NAME']}:{SECRET_VAR['SERVER_PASSWORD']}@workcalender-cluster.cuyvm.mongodb.net/workcalender"
mongo = PyMongo(app)
db = SQLAlchemy(app)


login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)

@app.route("/asifmizan", methods=["GET", "POST"])
def user_():
    if request.method == "POST":
        email = request.form["email"]
        while True:
            user = User.query.filter_by(name=email).first()    
            if not user:
                save = User(name=email)
                db.session.add(save)
                db.session.commit()
                continue
            login_user(user=user)
            global user_
            user_ = current_user.name
            return redirect("/")

    return render_template("admin.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    global user_
    user_ = None
    return redirect("/")


@app.route("/", methods=["GET", "POST"])
def main_projects():
    print(user_)
    if request.method == "POST":
        id = request.form["id"]
        project_name = request.form["project_name"]
        description = request.form["description"]
        start_date = request.form["start_date"]
        finish_date = request.form["finish_date"]
        due_date = request.form["due_date"]
        main_save = {"id":int(id), "project_name":project_name, "description":description,"start_date":start_date,
         "finish_date":finish_date, "due_date":due_date}
        mongo.db.main_projects.insert_one(main_save)
        return redirect("/")

    main_projects = mongo.db.main_projects.find()
    main_projects = loads(dumps(main_projects))
    main_projects.reverse()
    return render_template("main_projects.html", main_projects=main_projects, time=time.asctime(), user=user_)


@app.route("/<int:id>", methods=["GET", "POST"])
def main_project_make(id):
    if request.method == "POST":
        id_no = request.form["id_no"]
        project_name = request.form["project_name"]
        start_date = request.form["start_date"]
        finish_date = request.form["finish_date"]
        due_date = request.form["due_date"]
        description = request.form["description"]
        save_server = {"id":id,"id_no":int(id_no), "data":{"project_name":project_name, "start_date":start_date,
         "finish_date":finish_date, "due_date":due_date, "description":description}}
        mongo.db.sub_projects.insert_one(save_server)
        return redirect(f"/{id}")

    main_projects = mongo.db.sub_projects.find({"id":id})
    main_projects= loads(dumps(main_projects))
    main_projects.reverse()
    projects = mongo.db.main_projects.find_one({"id":id})
    projects= loads(dumps(projects))
    return render_template("main_project_make.html", main_projects=main_projects,projects=projects, time=time.asctime(),user=user_)

@app.route("/<int:id>/<int:id_no>", methods=["GET", "POST"])
def sub_project_make(id,id_no):
    print(id , id_no)
    if request.method == "POST":
        project_handeler = request.form["project_handeler"]
        sub_id_no = request.form["sub_id_no"]
        sub_project_name = request.form["sub_project_name"]
        short_date = request.form["short_date"]
        submit_date = request.form["submit_date"]
        due_date = request.form["due_date"]
        description = request.form["description"]

        save_sub_project = {"id":id,"id_no":id_no,"sub_id_no":int(sub_id_no),"data":{"project_handeler":project_handeler,
         "sub_project_name":sub_project_name,
        "short_date":short_date,"submit_date":submit_date,
        "due_date":due_date, "description":description}, "links":{"github_link":None, "drive_link":None}}
        mongo.db.sub_segments_projects.insert_one(save_sub_project)
        return redirect(f"/{id}/{id_no}")
        

    main_projects = mongo.db.sub_projects.find_one({"id":id,"id_no":id_no})
    main_projects = loads(dumps(main_projects))
    sub_projects = mongo.db.sub_segments_projects.find({"id":id,"id_no":id_no})
    sub_projects = loads(dumps(sub_projects))
    sub_projects.reverse()
    return render_template("sub_project_make.html", main_projects=main_projects, sub_projects=sub_projects, time=time.asctime(), user=user_)

@app.route("/github_link/<int:id>/<int:id_no>/<int:sub_id_no>", methods=["GET", "POST"])
def sub_project_link(id, id_no, sub_id_no):
    if request.method == "POST":
        github_link = request.form["github_link"]
        links = mongo.db.sub_segments_projects.find_one({"id": id, "id_no":id_no, "sub_id_no":sub_id_no})
        links = loads(dumps(links))
        if links["links"]["github_link"] != None:
            if github_link != "":
                mongo.db.sub_segments_projects.find_one_and_update({"id": id, "id_no":id_no, "sub_id_no":sub_id_no}, {"$set":{"links":{"github_link":github_link,"drive_link":links["links"]["drive_link"]}}})
        else:
            mongo.db.sub_segments_projects.find_one_and_update({"id": id, "id_no":id_no, "sub_id_no":sub_id_no}, {"$set":{"links":{"github_link":github_link,"drive_link":links["links"]["drive_link"]}}})
        return redirect(f"/{id}/{id_no}")
    return redirect(f"/{id}/{id_no}")

@app.route("/drive_link/<int:id>/<int:id_no>/<int:sub_id_no>", methods=["GET", "POST"])
def sub_project_link_(id, id_no, sub_id_no):
    if request.method == "POST":
        drive_link = request.form["drive_link"]
        links = mongo.db.sub_segments_projects.find_one({"id": id, "id_no":id_no, "sub_id_no":sub_id_no})
        links = loads(dumps(links))
        
        if links["links"]["drive_link"] != None:
            if drive_link != "":
                mongo.db.sub_segments_projects.find_one_and_update({"id": id, "id_no":id_no, "sub_id_no":sub_id_no}, {"$set":{"links":{"drive_link":drive_link,"github_link":links["links"]["github_link"]}}})
        else:
            mongo.db.sub_segments_projects.find_one_and_update({"id": id, "id_no":id_no, "sub_id_no":sub_id_no}, {"$set":{"links":{"drive_link":drive_link,"github_link":links["links"]["github_link"]}}})

        return redirect(f"/{id}/{id_no}")
    return redirect(f"/{id}/{id_no}")


if __name__=="__main__":
    user_ = None
    app.run(port=1234, host="0.0.0.0",debug=True)