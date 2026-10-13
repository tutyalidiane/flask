from flask import Blueprint, flash, render_template, request
import math

bp = Blueprint("calculos", __name__)

DESCONTO_SIMPLIFICADO = 607.20

# (limite da base, alíquota, parcela a deduzir)
FAIXAS_IRPF = [
    (2428.80, 0.0, 0.0),
    (2826.65, 0.075, 182.16),
    (3751.05, 0.15, 394.16),
    (4664.68, 0.225, 675.49),
    (float("inf"), 0.275, 908.73),
]


def ler_valor(texto):
    """Aceita 5000, 5000.50, 5.000,50 ou R$ 5.000,50."""
    texto = texto.strip().replace("R$", "").replace(" ", "")
    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")
    valor = float(texto)
    if not math.isfinite(valor) or valor < 0:
        raise ValueError("valor inválido")
    return valor


def calcular_irpf(bruto):
    base = max(0.0, bruto - DESCONTO_SIMPLIFICADO)

    for limite, aliquota, parcela in FAIXAS_IRPF:
        if base <= limite:
            break
    imposto_tabela = max(0.0, base * aliquota - parcela)

    # Redutor da Lei 15.270/2025
    if bruto <= 5000:
        redutor = min(312.89, imposto_tabela)
    elif bruto <= 7350:
        redutor = min(imposto_tabela, max(0.0, 978.62 - 0.133145 * bruto))
    else:
        redutor = 0.0

    imposto = max(0.0, imposto_tabela - redutor)
    return {
        "bruto": bruto,
        "base": round(base, 2),
        "aliquota": aliquota * 100,
        "imposto_tabela": round(imposto_tabela, 2),
        "redutor": round(redutor, 2),
        "imposto": round(imposto, 2),
        "liquido": round(bruto - imposto, 2),
    }


def calcular_rescisao(salario, meses):
    if not 1 <= meses <= 12:
        raise ValueError("meses fora do intervalo")
    return {
        "salario": salario,
        "meses": meses,
        "decimo_terceiro": round(salario / 12 * meses, 2),
    }


@bp.route("/painel", methods=("GET", "POST"))
def painel():
    irpf = None
    rescisao = None

    if request.method == "POST":
        acao = request.form.get("acao")
        try:
            if acao == "irpf":
                irpf = calcular_irpf(ler_valor(request.form["salario_bruto"]))
            elif acao == "rescisao":
                rescisao = calcular_rescisao(
                    ler_valor(request.form["salario_base"]),
                    int(request.form["meses"]),
                )
        except (ValueError, KeyError):
            flash("Valores inválidos. Confira os números digitados.")

    return render_template("calculos/index.html", irpf=irpf, rescisao=rescisao)