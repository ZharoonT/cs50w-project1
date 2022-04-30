from ast import And
import os

from flask import Flask, render_template,request, session ,url_for,redirect
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from helper import validadte_sesion_state
#import requests
app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
dataBase="postgresql://cukvooypnhbtvc:f31776da87ce9a826779209bcd37c7714dd0e70565d3cee4297e94a8ef975ef1@ec2-34-231-63-30.compute-1.amazonaws.com:5432/d6qnp2n60ih49i"
engine = create_engine(os.getenv("DATABASE_URL"))
#engine = create_engine(os.getenv(dataBase))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/",methods=["GET","POST"])
#@validadte_sesion_state
def index():
    lista_libros=[]
    #validar el tipo de metodo que recibo desde la interfaz
    if request.method=="POST":
        #parametro de busqequeda
        parametro_busqeda=request.form.get("txt_buscar")
        #indicamos como buscar
        filtrar_por=request.form.get("radio")
        print(parametro_busqeda)
            #Validamos si en el campo de busqyeda existe un valor
        if (parametro_busqeda is None):
            #Mostramos todos los libros
            lista_libros=get_all_books()
        else:
            #validamos el tipo de filtro que vamos a aplicar
            #Y realizamos el filtro
            if(filtrar_por=="title"):
                lista_libros=buscar_libros_por_titulo(parametro_busqeda)
            elif(filtrar_por=="author"):
                lista_libros=buscar_libros_por_author(parametro_busqeda)
            elif(filtrar_por=="isbn"):
                lista_libros=buscar_libros_por_isbn(parametro_busqeda)
    else:
        lista_libros=get_all_books()
    return render_template('index.html', libros=lista_libros)

#ruta para login
@app.route("/login",methods=["GET","POST"])
def login():
    session.clear()
    if request.method=="POST":
        user_name=request.form.get("txt_user_name")
        password=request.form.get("txt_password")
        user_id=get_user_id_from_user_name_password(user_name,password)
        if len(user_id)>0:
            #iniciamos sesion
            session["user_id_sesion"]=user_id
            return redirect(url_for('index'))
        else:
            return("El usuario NO EXISTE, debes de agregarlo")
    else:
            return render_template('login.html')

#ruta para crear un usuario
@app.route("/register",methods=["GET","POST"])
def register():
    if request.method=="POST":
        username=request.form.get("txt_user_name")
        password=request.form.get("txt_password")
        confirm_password=request.form.get("txt_confirm_password")
        country=request.form.get("txt_country")
        #validamos campos nulos
        if(username=="" or password=="" or confirm_password==""):
            return ("no se admiten campos nulos")
        else:
            #validamos las contraseñas
            if(password==confirm_password):
                print("Las contraseñas son iguales")
                #dentro de add_user_se valida si el usuario existe o no    NO PUEDE HABER UN USUARIO REPETIDO   
                state=add_user(username,password)
                if(state==True):
                    return ("Usuario agregado con exito")
                else:
                    return ("Error el usuario no fue agregado")
            else:
                return("Las contraseñas no son iguales inténtalo de nuevo..... :-(")
    else:
        return render_template('register.html')

#ruta para detalles del libro
@app.route("/detalles/<book_isbn>", methods=["GET","POST"])
def detalles(book_isbn):
    #validamos el tipo de metodo de entrada desde el serividor
    if request.method=="POST":
            pass
            #accedems a las variables
            reseña=request.form.get("txt_reseña")
            puntaje=request.form.get("txt_puntaje")
            if reseña is None and puntaje is None:
                return 'No se admiten campos nulos'
            else:
                pass
                #implementar la funcion agregar resenia
    else:
        libro_detalle=detalle_libro_por_isbn(book_isbn)
        #implementar listar todas las resenias de un libro
    return render_template('detalles.html',libro_detalle=libro_detalle)
#funcion para agregar un usuario
def add_user(username,password):
    #procedemos a insertar los datos en la base de datos
    try:
        #validamos si existe un registro con ese nombre de usuario
        user_validate=get_user_name_from_user_name(username)
        if(user_validate==""):
            return False
        else:
            #si no hay un usuario registrado con ese username se agreda
            query="INSERT INTO usuarios (usuario, contraseña) VALUES('"+username+"','"+password+"')"
            db.execute(query)
            db.commit()
            return True
    except ValueError:
        return False

def get_user_name_from_user_name(user_name_parametro):
    #obtenemos el user code con el id del usuario
    try:
        query="SELECT usuario FROM usuarios WHERE usuario ='"+user_name_parametro+"'"
        user_name=db.execute(query).fetchall()
        return user_name
    except ValueError:
        print(ValueError)

def get_user_id_from_user_name_password(user_name,password):
    #obtenemos el user code con el id del usuario
    try:
        query="SELECT id_usuario FROM usuarios WHERE  usuario ='"+user_name+"' AND contraseña='"+password+"'"
        id_usuario=db.execute(query).fetchall()
        return id_usuario
    except ValueError:
        print(ValueError)

@app.route("/salir")
def logout():
    # Forget any user_id
    session.clear()
    # Redirect user to login
    return redirect("/login")

def get_all_books():
    try:
        query="SELECT * from libros "#fetchall: agarre todos los datos de golpe
        lista_libros=db.execute(query).fetchall()
        return lista_libros
    except ValueError:
        print(ValueError)

def buscar_libros_por_titulo(title):
    try:
        query="SELECT * from libros WHERE title LIKE '%"+title+"%'"
        buscarLibros_porNombre=db.execute(query).fetchall()
        return buscarLibros_porNombre
    except ValueError:
        print(ValueError)

def buscar_libros_por_author(author):
    try:
        query="SELECT * from libros WHERE author LIKE '%"+author+"%'"
        buscarLibros_porAuthor=db.execute(query).fetchall()
        return buscarLibros_porAuthor
    except ValueError:
        print(ValueError)
        
def buscar_libros_por_isbn(isnb):
    try:
        query="SELECT * from libros WHERE isbn LIKE '%"+isnb+"%'"
        buscarLibros_porisbn=db.execute(query).fetchall()
        return buscarLibros_porisbn
    except ValueError:
        print(ValueError)

#crear tabla reseñas dentro de adminer, campos: id reseña, id_usuario,id_libro, contenido
def agregar_reseña():
    id_usuario=session["user_id_sesion"][0]

    pass

def detalle_libro_por_isbn(isbn_libro):
    try:
        query="SELECT * from libros WHERE  isbn = '"+isbn_libro+"'"
        detalle=db.execute(query).fetchone()
        return detalle
    except ValueError:
        print(ValueError)