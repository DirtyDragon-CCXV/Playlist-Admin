from re import split, sub, search, match

#!-- modulo de soporte --!
def ConvertirTextos(texto:str) -> str:
    """remplaza acentos y limpio o formatea la cadena para comparaciones simplificadas.

    Args:
        texto (str): texto a formatear

    Returns:
        str: texto formateado para comparar
    """
    # Primera Fase - Acentos
    acentos = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
        'ñ': 'n', 'Ñ': 'N'
    }
    for acento, sin_acento in acentos.items():
        texto = texto.replace(acento, sin_acento)

    # Segunda Fase - Limpieza
    if search(r"[Ll][Ii][Vv][Ee]", texto) or match(r"^[\u3000-\u4DB5\u4E00-\u9FE6]+\b\s?(?!\([Cc]|（[Cc]).*(\s-\s)?\w*", texto):
        pass
    
    elif search(r"[Rr][Ee][Mm][Ii][Xx]", texto):
        texto = sub(r"\(.*?[Rr][Ee][Mm][Ii][Xx].*?\)", "remix", texto)
        texto = sub(r"-\s.*?[Rr][Ee][Mm][Ii][Xx]", "remix", texto)

    else:
        texto = split(r"\s[-]\s|\swith\s", texto)[0].strip()
        
    texto = sub(r"\(.*?\)\s?|（.*）?\s?|\[.*?\]\s?", "", texto)
    texto = sub(r"[^\u0028\u0029\u0030-\u007E\u00A0-\u036F\u0370-\u052F\u0600-\u077F\u2E80-\u2FD5\u3000-\u4DB5\u4E00-\u9FE6\uA640-\uA69F\u10330-\u1034A\uFF21-\uFF3A\uFF08\uFF09]", "", texto)
    texto = sub(r"(\s)+", " ", texto)
    texto = sub(r"([Rr][Ee][Mm][Ii][Xx])+", "remix", texto)
    
    return texto.strip()

def ConvertirTiempo(milisegundos: int) -> str:
    #by: @Google Gemini, le pedi la porcion de codigo, me senti muy tonto al recordar que podia haberla hecho con el operardor de residuo '%'.
    minutos = int(milisegundos / 60000)
    segundos = int((milisegundos % 60000) / 1000)

    if segundos < 10:
        segundos_str = f"0{segundos}"
    else:
        segundos_str = str(segundos)

    return f"{minutos}:{segundos_str}"