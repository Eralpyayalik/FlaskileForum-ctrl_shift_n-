from flask import Flask, render_template,flash,redirect,logging,url_for,request,session
from flask_mysqldb import MySQL
from wtforms import Form,StringField,TextAreaField,PasswordField,validators
from wtforms.validators import DataRequired, Email
from passlib.hash import sha256_crypt
from functools import wraps
from flask_wtf import FlaskForm
from wtforms import TextAreaField, FileField, SubmitField
from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename
import os
from MySQLdb.cursors import DictCursor



def login_required(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else: 
            flash("Bu sayfayı görüntülemek için giriş yapın...","danger")
        return redirect(url_for("login"))
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" in session:
            cursor = mysql.connection.cursor()
            sorgu = "Select is_admin From users where username = %s"
            cursor.execute(sorgu, (session["username"],))
            user_data = cursor.fetchone()
            
            if user_data and user_data["is_admin"] == 1:
                return f(*args, **kwargs)
            else:
                flash("Bu alan için yetkiniz yok!", "danger")
                return redirect(url_for("index"))
        else:
            flash("Lütfen önce giriş yapın.", "danger")
            return redirect(url_for("login"))
    return decorated_function

class RegisterForm(Form):
    name=StringField("İsim Soyisim",validators=[validators.length(min=4, max=25)])
    username=StringField("Kullanıcı Adı",validators=[validators.length(min=4, max=35)])
    email=StringField("Email Adresi",validators=[validators.Email(message="Lütfen Geçerli Bir mail Giriniz...")])

    password=PasswordField("Parola:", validators=[
        validators.DataRequired(message="Lütfen bir parola belirleyin."),
        validators.EqualTo(fieldname="confirm",message="Parolanız Uyuşmuyor...")
    ])
    confirm=PasswordField("parola Doğrula")
class LoginForm(Form):
    username=StringField("Kullanıcı Adı")
    password = PasswordField("Parola")

app = Flask(__name__)

app.config["MYSQL_HOST"] = "mysql-289e9598-eralpyayalikk-4fe5.h.aivencloud.com"
app.config["MYSQL_USER"] = "avnadmin"
app.config["MYSQL_PASSWORD"] = os.getenv("MYSQL_PASSWORD")
app.config["MYSQL_DB"] = "defaultdb"
app.config["MYSQL_PORT"] = 26850
# SSL için şunu ekle (Aiven için en basit hali):
app.config["MYSQL_SSL_MODE"] = "REQUIRED"

mysql=MySQL(app)

@app.route("/")
def index():
    return render_template("index.html",answer= "evet")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/articles")
def articles():
    cursor=mysql.connection.cursor()

    sorgu="Select * From articles"
    result=cursor.execute(sorgu)

    if result > 0:
        articles=cursor.fetchall()
        return render_template("articles.html",articles=articles)
    else:
        return render_template("articles.html")
@app.route("/dashboard")
@login_required
def dashboard():
    cursor= mysql.connection.cursor()

    sorgu="Select *From articles where author= %s"

    result=cursor.execute(sorgu,(session["username"],))
    if result >0:
        articles =cursor.fetchall()
        return render_template("dashboard.html",articles=articles)

    return render_template("dashboard.html")

@app.route("/register",methods =["GET","POST"])
def register():
    form=RegisterForm(request.form)
    if request.method=="POST" and form.validate():
        name=form.name.data
        username=form.username.data
        email=form.email.data
        password=sha256_crypt.encrypt (form.password.data)

        cursor=mysql.connection.cursor()

        sorgu="Insert into users(name,email,username,password) VALUES(%s,%s,%s,%s)"

        cursor.execute(sorgu,(name,email,username,password))
        mysql.connection.commit()

        cursor.close()

        flash("Başarıyla Kayıt Oldunuz...","success")
        return redirect(url_for("login"))
    else:

        return render_template("register.html",form=form)
@app.route("/login",methods=["GET","POST"])
def login():
    form=LoginForm(request.form)
    if request.method=="POST":
        username=form.username.data
        password_entered=form.password.data

        cursor=mysql.connection.cursor()
        sorgu="Select * From users where username= %s"
        result = cursor.execute(sorgu,(username,))

        if result > 0:
            data= cursor.fetchone()
            real_password = data["password"]
            if sha256_crypt.verify(password_entered,real_password):
                flash("Başarıyla giriş yaptınız...","success")
                
                session["logged_in"]=True
                session["username"]= username
                session["id"] = data["id"]
                session["is_admin"] = data["is_admin"]
                return redirect(url_for("index"))

            
            else:
                flash ("Parolanızı Yanlış Girdiniz...","danger")
                return redirect(url_for("login"))
        else:
            flash("Böyle bir kullanıcı bulunmuyor...","danger")
            return redirect(url_for("login"))

    return render_template("login.html",form=form)

@app.route("/article/<string:id>")
def article(id):
    cursor = mysql.connection.cursor()

    sorgu = """
        SELECT articles.*, users.email, users.avatar, users.name 
        FROM articles 
        INNER JOIN users ON articles.author = users.username 
        WHERE articles.id = %s
    """
    cursor.execute(sorgu, (id,))
    article = cursor.fetchone()

    if not article:
        flash("Konu bulunamadı", "danger")
        return redirect(url_for("articles"))

    cursor.execute(
        "SELECT username, comment, created_date, user_id FROM comments WHERE article_id=%s ORDER BY id DESC",
        (id,)
    )
    comments = cursor.fetchall()

    return render_template("article.html", article=article, comments=comments)
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))
@app.route("/addarticle",methods =["GET","POST"])
def addarticle():

    form =ArticleForms(request.form)
    if request.method=="POST" and form.validate():
        title = form.title.data
        content=form.content.data

        cursor=mysql.connection.cursor()

        sorgu ="Insert into articles(title,author,content)VALUES(%s,%s,%s)"
        cursor.execute(sorgu,(title,session["username"],content))

        mysql.connection.commit()

        cursor.close()

        flash("Makale Başarıyla Oluşturuldu...","success") 

        return redirect(url_for("dashboard"))
    

    return render_template("addarticle.html",form=form)

@app.route("/delete/<string:id>")
@login_required
def delete(id):
    cursor=mysql.connection.cursor()
    sorgu="Select *From articles where author=%s and id=%s"

    result=cursor.execute(sorgu,(session["username"],id))

    if result >0:
        sorgu2="Delete from articles where id=%s"
        cursor.execute(sorgu2,(id,))
        mysql.connection.commit()
        return redirect(url_for("dashboard"))
    
    else:
        
        flash("Böyle bir makale yok veya silme yetkiniz yok","danger")
        return redirect/url_for("index")
    
@app.route("/edit/<string:id>",methods=["GET","POST"])
@login_required
def uptade(id):
    if request.method=="GET":
        cursor=mysql.connection.cursor()

        sorgu="Select *from articles where id=%s and author=%s"
        result=cursor.execute(sorgu,(id,session["username"]))

        if result==0:
            flash("Böyle bir makale yok veya bu işlem yetkiniz yok...","danger")
            return redirect(url_for("index"))
        else:
            article=cursor.fetchone()
            form=ArticleForms()

            form.title.data=article["title"]
            form.content.data=article["content"]
            return render_template("update.html",form=form)
    else:
        form=ArticleForms(request.form)

        newTitle=form.title.data
        newContent=form.content.data

        sorgu2="Update articles Set title = %s,content=%s where id =%s"

        cursor=mysql.connection.cursor()

        cursor.execute(sorgu2,(newTitle,newContent,id))
        mysql.connection.commit()
        flash("Makale başarıyla güncellendi","success")

        return redirect(url_for("dashboard"))

@app.route("/profile/<string:username>")
@login_required
def profile(username):
    cursor = mysql.connection.cursor()
    
    sorgu = "SELECT * FROM users WHERE username=%s"
    result = cursor.execute(sorgu, (username,))

    if result == 0:
        flash("Böyle bir kullanıcı yok!", "danger")
        return redirect(url_for("index"))
    
    user = cursor.fetchone()

    sorgu_makale = "SELECT * FROM articles WHERE author = %s"
    article_count = cursor.execute(sorgu_makale, (username,)) 

    cursor.close() 
    
    return render_template("profile.html", user=user, article_count=article_count)

@app.route("/profile/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = ProfileUpdateForm()
    cursor = mysql.connection.cursor()

    cursor.execute("SELECT * FROM users WHERE username=%s", (session["username"],))
    user = cursor.fetchone()

    if request.method == "GET":
        form.bio.data = user["bio"]
        return render_template("edit_profile.html", form=form)

    if request.method == "POST" and form.validate():
        bio = form.bio.data
        avatar_filename = user["avatar"]

        
        upload_folder = os.path.join(app.root_path, "static", "avatars")
        os.makedirs(upload_folder, exist_ok=True)

        
        if form.avatar.data:
            file = form.avatar.data
            filename = secure_filename(file.filename)

            if filename:  
                save_path = os.path.join(upload_folder, filename)
                file.save(save_path)
                avatar_filename = filename

        update_q = "UPDATE users SET bio=%s, avatar=%s WHERE username=%s"
        cursor.execute(update_q, (bio, avatar_filename, session["username"]))
        mysql.connection.commit()

        flash("Profil güncellendi!", "success")
        return redirect(url_for("profile", username=session["username"]))

@app.route("/add_comment/<string:article_id>", methods=["POST"])
def add_comment(article_id):

    if "logged_in" not in session:
        flash("Yorum yapmak için giriş yapmalısınız.", "danger")
        return redirect(url_for("login"))

    comment = request.form.get("comment")

    cursor = mysql.connection.cursor()
    cursor.execute(
    "INSERT INTO comments (article_id, username, comment, user_id) VALUES (%s, %s, %s, %s)",
    (article_id, session["username"], comment, session["id"])
        )
    mysql.connection.commit()

    flash("Yorum başarıyla eklendi!", "success")
    return redirect(url_for("article", id=article_id))


@app.route("/user/<int:user_id>")
def user_profile(user_id):
    cursor = mysql.connection.cursor()

    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()

    return render_template("user_profile.html", user=user)


@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    cursor = mysql.connection.cursor()
    
    cursor.execute("SELECT * FROM articles")
    articles = cursor.fetchall()
    
    
    cursor.execute("SELECT * FROM comments")
    comments = cursor.fetchall()
    
    return render_template("admin_dashboard.html", articles=articles, comments=comments)


@app.route("/admin/delete_article/<string:id>")
@admin_required
def admin_delete_article(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM articles WHERE id = %s", (id,))
    mysql.connection.commit()
    flash("Makale admin tarafından silindi.", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/delete_comment/<string:id>")
@admin_required
def admin_delete_comment(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM comments WHERE id = %s", (id,))
    mysql.connection.commit()
    flash("Yorum admin tarafından silindi.", "success")
    return redirect(url_for("admin_dashboard"))

class ArticleForms(Form):
    title=StringField("Makale Başlığı",validators=[validators.length(min=5)])
    content=TextAreaField("Makale İçeriği", validators=[validators.length(min=10)])

class ProfileUpdateForm(FlaskForm):
    bio = TextAreaField("Biyografi", validators=[DataRequired()])
    avatar = FileField("Avatar")
    submit = SubmitField("Kaydet")



if __name__=="__main__":
    app.run(debug=True)