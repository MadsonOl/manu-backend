"""Validadores reutilizaveis para os schemas de entrada (defesa em profundidade).

Aplicados apenas aos modelos *Create* — nunca trust o cliente, ainda que o
frontend ja valide. Documentos e telefone sao normalizados para somente
digitos, alinhados ao que o frontend envia. Os modelos *Response* permanecem
permissivos para nao quebrar a leitura de dados legados ja gravados.
"""
import re

_EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def so_digitos(valor: str) -> str:
    """Remove tudo que nao for digito."""
    return re.sub(r"\D", "", valor or "")


def texto(valor, *, campo: str = "campo", minimo: int = 1, maximo: int = 500) -> str:
    """Exige texto nao-vazio (apos strip) e dentro de um limite de tamanho."""
    if not isinstance(valor, str):
        raise ValueError(f"{campo} deve ser um texto")
    limpo = valor.strip()
    if len(limpo) < minimo:
        raise ValueError(f"{campo} e obrigatorio")
    if len(limpo) > maximo:
        raise ValueError(f"{campo} excede {maximo} caracteres")
    return limpo


def texto_opcional(valor, *, campo: str = "campo", maximo: int = 2000):
    """Como `texto`, mas aceita None/vazio (campos opcionais)."""
    if valor is None:
        return valor
    return texto(valor, campo=campo, minimo=0, maximo=maximo)


def _dv(digitos: str, pesos) -> int:
    soma = sum(int(d) * p for d, p in zip(digitos, pesos))
    resto = soma % 11
    return 0 if resto < 2 else 11 - resto


def cpf(valor: str) -> str:
    """Valida o CPF pelos digitos verificadores; retorna so digitos."""
    c = so_digitos(valor)
    if len(c) != 11 or c == c[0] * 11:
        raise ValueError("CPF invalido")
    if int(c[9]) != _dv(c[:9], range(10, 1, -1)) or int(c[10]) != _dv(c[:10], range(11, 1, -1)):
        raise ValueError("CPF invalido")
    return c


def cnpj(valor: str) -> str:
    """Valida o CNPJ pelos digitos verificadores; retorna so digitos."""
    c = so_digitos(valor)
    if len(c) != 14 or c == c[0] * 14:
        raise ValueError("CNPJ invalido")
    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    if int(c[12]) != _dv(c[:12], pesos1) or int(c[13]) != _dv(c[:13], pesos2):
        raise ValueError("CNPJ invalido")
    return c


def telefone(valor: str) -> str:
    """Telefone fixo (10) ou celular (11 digitos); retorna so digitos."""
    d = so_digitos(valor)
    if len(d) not in (10, 11):
        raise ValueError("telefone invalido")
    return d


def email(valor: str) -> str:
    """Valida o formato do e-mail e normaliza (strip)."""
    limpo = (valor or "").strip()
    if not _EMAIL_RE.match(limpo):
        raise ValueError("e-mail invalido")
    return limpo
