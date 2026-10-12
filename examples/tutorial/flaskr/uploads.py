import os
import uuid

from flask import current_app
from PIL import Image
from werkzeug.utils import secure_filename

EXTENSOES = {"png", "jpg", "jpeg", "gif", "webp"}


def salvar_imagem(arquivo):
    """Valida e salva a imagem. Retorna o nome salvo, ou None se não houve envio."""
    if arquivo is None or arquivo.filename == "":
        return None

    nome = secure_filename(arquivo.filename)
    extensao = nome.rsplit(".", 1)[-1].lower() if "." in nome else ""
    if extensao not in EXTENSOES:
        raise ValueError("Formato não permitido. Use png, jpg, jpeg, gif ou webp.")

    try:
        Image.open(arquivo.stream).verify()  # confere se é imagem de verdade
    except Exception:
        raise ValueError("O arquivo enviado não é uma imagem válida.")
    arquivo.stream.seek(0)

    nome_final = f"{uuid.uuid4().hex}_{nome}"  # evita sobrescrever arquivos
    arquivo.save(os.path.join(current_app.config["UPLOAD_FOLDER"], nome_final))
    return nome_final


def remover_imagem(nome):
    if nome:
        caminho = os.path.join(current_app.config["UPLOAD_FOLDER"], nome)
        if os.path.exists(caminho):
            os.remove(caminho)