from flask import redirect, render_template, request, url_for, session, abort, flash
from app.helpers.user_helper import has_permit
from app.models.punto import Punto
from app.helpers.auth import authenticated
from app.helpers import configurator

from app.helpers.forms import PuntoForm, PuntoEditForm
from sqlalchemy import exc

# Public resources
def index():
    """
        El metodo mostrara todos los puntos en una tabla
    """

    if not authenticated(session):
        abort(401)
    
    if not has_permit("punto_index"):
        flash("No cuenta con los permisos necesarios","danger")
        return redirect(request.referrer)

    page = request.args.get('page',1, type=int)
    page_config = configurator.settings().get_rows_per_page()
    puntos = Punto.query.paginate(page=page,per_page=page_config)

    return render_template("punto/index.html", puntos=puntos)

def show(id):
    """
        muestra la info del punto    
    """
    punto = Punto.query.filter_by(id=int(id)).first()
    return render_template("punto/show.html",punto=punto)

def show_map(id):
    """
        muestra el mapa dibujando el punto del id    
    """
    punto = Punto.query.filter_by(id=int(id)).first()
    return render_template("punto/map.html",punto=punto)

def new():
    if not authenticated(session):
        abort(401)

    if not has_permit("punto_new"):
        flash("No cuenta con los permisos necesarios","danger")
        return redirect(request.referrer)
    
    form = PuntoForm()

    return render_template("punto/new.html",form=form)

def create():
    if not authenticated(session):
        abort(401)

    if not has_permit("punto_new"):
        flash("No cuenta con los permisos necesarios","danger")
        return redirect(request.referrer)
    
    form = PuntoForm()
    data= dict(form.data)
    del data["csrf_token"]
    new_punto = Punto(**data)
    
    if not form.validate_on_submit():
        flash(form.errors)
        return render_template("recorrido/new.html", form=form)

    try:
        Punto.save(new_punto)
        flash("Se creo con exito", "success")
        return redirect(url_for("punto_index"))
    except exc.IntegrityError:
        flash("Punto con ese nombre ya existe", "danger")
        return redirect(request.referrer)

def delete(id):
    if not authenticated(session):
        abort(401)

    if not has_permit("punto_delete"):
        flash("No cuenta con los permisos necesarios","danger")
        return redirect(request.referrer)

    puntoEliminar = Punto.query.filter_by(id=int(id)).first()
    Punto.delete(puntoEliminar)
    flash("Se elimino con exito", "success") 
    return redirect(url_for('punto_index'))

def edit(id):
    if not authenticated(session):
        abort(401)

    if not has_permit("punto_edit"):
        flash("No cuenta con los permisos necesarios","danger")
        return redirect(request.referrer)
    
    form = PuntoEditForm()
    punto = Punto.query.filter_by(id=int(id)).first()
    form.nombre(id=punto)

    return render_template("punto/edit.html", punto=punto, form=form)

def update():
    
    if not authenticated(session):
        abort(401)

    if not has_permit("punto_edit"):
        flash("No cuenta con los permisos necesarios","danger")
        return redirect(request.referrer)
    
    data = request.form
    punto = Punto.search_id(data["id"])
    
    form = PuntoEditForm()
    data= dict(form.data)
    del data["csrf_token"]
    
    punto = Punto.search_id(data["id"])
    if not form.validate_on_submit():
        flash(form.errors)
        return render_template("recorrido/edit.html", punto=punto, form=form)
    
    try:
        punto.update(data)
        flash("Se edito con exito", "success")
        return redirect(url_for("punto_index"))
    except exc.IntegrityError:
        flash("Punto con ese nombre ya existe", "danger")
        return redirect(request.referrer)

def filtro():
    """
        El metodo hara un filtro de los puntos dependiendo de los datos ingresados 
    """
    page_config = configurator.settings().get_rows_per_page()
    page = request.args.get('page',1, type=int)
    data = request.form
    estado = data["estado"]
    nombre = data["nombre"]
    busqueda = "%{}%".format(nombre)
    if (estado != "" and nombre!= ""):
      puntos=Punto.query.filter(Punto.nombre.like(busqueda),Punto.estado.like(estado)).paginate(page=page,per_page=page_config)
    else:
        if (estado == "" and nombre != ""):
            puntos=Punto.query.filter_by(Punto.nombre.like(busqueda)).paginate(page=page,per_page=page_config)
        else:
            if(estado !="" and nombre==""):
                puntos=Punto.query.filter_by(estado=estado).paginate(page=page,per_page=page_config)
            else:
                puntos=Punto.query.paginate(page=page,per_page=page_config)
    return render_template("punto/index.html", puntos=puntos, estado=estado, nombre=nombre )
