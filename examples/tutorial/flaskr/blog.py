from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort

from .auth import login_required
from .models import Post, db
from .uploads import remover_imagem, salvar_imagem

bp = Blueprint("blog", __name__)


@bp.route("/")
def index():
    posts = db.session.execute(
        db.select(Post).order_by(Post.created.desc())
    ).scalars().all()
    return render_template("blog/index.html", posts=posts)


def get_post(id, check_author=True):
    post = db.session.get(Post, id)
    if post is None:
        abort(404, f"Post id {id} doesn't exist.")
    if check_author and post.author_id != g.user.id:
        abort(403)
    return post


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        imagem = None
        if error is None:
            try:
                imagem = salvar_imagem(request.files.get("imagem"))
            except ValueError as e:
                error = str(e)

        if error is None:
            db.session.add(
                Post(title=title, body=body, author_id=g.user.id, imagem_post=imagem)
            )
            db.session.commit()
            return redirect(url_for("blog.index"))

        flash(error)

    return render_template("blog/create.html")


@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    post = get_post(id)

    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        nova_imagem = None
        if error is None:
            try:
                nova_imagem = salvar_imagem(request.files.get("imagem"))
            except ValueError as e:
                error = str(e)

        if error is None:
            post.title = title
            post.body = body
            if nova_imagem:
                remover_imagem(post.imagem_post)  # apaga a antiga
                post.imagem_post = nova_imagem
            db.session.commit()
            return redirect(url_for("blog.index"))

        flash(error)

    return render_template("blog/update.html", post=post)


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    post = get_post(id)
    remover_imagem(post.imagem_post)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for("blog.index"))