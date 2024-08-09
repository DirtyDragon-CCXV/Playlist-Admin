import re
import json
from ytmusicapi import YTMusic

with open("modulos/excepciones.json", "r") as f:
    excepciones = json.loads(f.read())

# valores predeterminados tomados de JSON
excepcion_playlist_uno = excepciones["youtube"]["excepcion_playlist_exclusiva"]

class AdministradorYTMusic():
    def __init__(self, playlist_Identificador: str, Debug: bool = False) -> None:
        self.__playlist_ID__ = playlist_Identificador
        self.__modo_debug__ = Debug

        # iniciar Api
        if self.__modo_debug__:
            print("1. Autorizando Cliente...")

        self.__yt__ = YTMusic(auth="modulos/tokens/oauth_yt.json")
        self.NOMBRE_PLAYLIST = self.__yt__.get_playlist(self.__playlist_ID__, limit=1)["title"]

        if self.__modo_debug__:
            print("1. Cliente Autorizado", end="\n")

    def __obtenerPlaylist__(self) -> dict:
        """
        Funcion que obtiene el JSON de canciones en bruto.
        
        Returns:
            dict: Diccionario con los tracks de la playlist en bruto.
        """
        return self.__yt__.get_playlist(playlistId=self.__playlist_ID__, limit=None)

    def __obtenerPlaylistConIDs__(self) -> list:
        """
        obtiene los tracks de la playlist pero añade el 'VideoID' y 'SetVideoID'
        
        Returns:
            list: Lista que contiene las tracks [Titulo, Artistas, VideoID, SetVideoID]
        """
        if self.__modo_debug__:
            print("2-1. Obteniendo Playlist.")
            
        CANCIONES = []
        playlist_tracks = self.__obtenerPlaylist__()
        if self.__playlist_ID__ == excepcion_playlist_uno:
            #Excepcion para playlist que no cuenta con los titulos y clasificacion de artistas estandar
            for track in playlist_tracks["tracks"]:
                name_song = track["title"]
                
                if track["artists"] == None or re.match(r".*\s-\s.*", name_song):
                    if re.match(r".*([Ff][Ee][Aa][Tt]\.|[Ff][Tt]\.).*", name_song):
                        request = re.split(r"\s-\s", name_song)
                        name_song = re.split(r"[\s\S](?:[Ff][Tt]\.|[Ff][Ee][Aa][Tt]\.)[\s\S]", request[1])[0]
                        artists_song = [request[0]]
                        for adder in re.split(r"[\s\S](?:[Ff][Tt]\.|[Ff][Ee][Aa][Tt]\.)[\s\S]", request[1])[1:]:
                            artists_song.append(adder) 
                    else:
                        request = re.split(r"\s-\s", name_song)
                        name_song = request[1]
                        artists_song = [request[0]]

                elif re.match(r".*([Ff][Ee][Aa][Tt]\.|[Ff][Tt]\.).*", name_song):
                    request = re.split(r"[\s\S](?:\(?[Ff][Ee][Aa][Tt]\.|\(?[Ff][Tt]\.)[\s\S]", name_song)
                    name_song = request[0]
                    artists_song = [ artist["name"] for artist in track["artists"] ]
                    artists_song.append(request[1])

                elif re.match(r".*[^\.]\sby.*", name_song):
                    request = re.split(r"\sby\s", name_song)
                    name_song = request[0]
                    artists_song = [re.split(r"\s\[(?:.*)", request[1])[0]]

                else:
                    if re.match(r".*([Ff][Tt]\.|[Ff][Ee][Aa][Tt]\.).*", name_song):
                        request = re.search(r"^(.*)\s(?:\(?[Ff][Tt]\.|[Ff][Ee][Aa][Tt]\.)\s(.*)\)?", name_song)
                        name_song = request.group(1).split(" (")[0]
                        artists_song = [request.group(2)]
                    else:
                        artists_song = [ artist["name"] for artist in track["artists"] ]

                # Limpieza de texto en titulo y artistas
                name_song = name_song.strip()
                name_song = re.split(r"[\s\S](\(|\[)", name_song)[0]

                temp_lista = []
                for i, artist in enumerate(artists_song):
                    artists_song[i] = re.split(r"\s[&xX\,]\s", artist)
                    for elemento in artists_song[i]:
                        elemento = elemento.lstrip("\u200b")
                        if elemento[1] == " " and elemento[-3] == " ":
                            elemento = elemento[2:-3]
                        elemento = re.split(r"[\s\S](?:\(|\[|\/\/)", elemento)[0]
                        elemento = elemento.strip(")")
                        elemento = re.sub(r"[^\sa-zA-z0-9０-９ａ-ｚＡ-Ｚ$'!#%&\?¡¿！＂＃＄％＆＇＊＋，－．／À-þ]", "", elemento)
                        elemento = elemento.capitalize()
                        temp_lista.append(elemento)
                artists_song = temp_lista
                
                CANCIONES.append( [name_song, artists_song, track["videoId"], track["setVideoId"]] )
        else:
            for track in playlist_tracks["tracks"]:
                name_song = track["title"]  # titulo de la cancion
                try: 
                    artists_song = [ artist["name"] for artist in track["artists"] ] # artistas de la cancion
                except TypeError: 
                    artists_song = ["Desconocido/s"]
                    
                CANCIONES.append( [name_song, artists_song, track["videoId"], track["setVideoId"]] )
                
        if self.__modo_debug__:
            print("2-1. Playlist Obtenida.", end="\n")
        
        return CANCIONES

    def ImportarCanciones(self) -> list:
        """Obtiene las canciones, extrae el titulo, artistas, duracion.

        Returns:
            list: lista con los datos necesarios de las canciones
        """
        if self.__modo_debug__:
            print("2. Obteniendo Playlist.")
        
        canciones = self.__obtenerPlaylist__()
        PLAYLIST = []

        if self.__playlist_ID__ == excepcion_playlist_uno:
            #Excepcion para playlist que no cuenta con los titulos y clasificacion de artistas estandar
            for track in canciones["tracks"]:
                
                name_song = track["title"]
                
                if track["artists"] == None or re.match(r".*\s-\s.*", name_song):
                    if re.match(r".*([Ff][Ee][Aa][Tt]\.|[Ff][Tt]\.).*", name_song):
                        request = re.split(r"\s-\s", name_song)
                        name_song = re.split(r"[\s\S](?:[Ff][Tt]\.|[Ff][Ee][Aa][Tt]\.)[\s\S]", request[1])[0]
                        artists_song = [request[0]]
                        for adder in re.split(r"[\s\S](?:[Ff][Tt]\.|[Ff][Ee][Aa][Tt]\.)[\s\S]", request[1])[1:]:
                            artists_song.append(adder)
                    else:
                        request = re.split(r"\s-\s", name_song)
                        name_song = request[1]
                        artists_song = [request[0]]

                elif re.match(r".*([Ff][Ee][Aa][Tt]\.|[Ff][Tt]\.).*", name_song):
                    request = re.split(r"[\s\S](?:\(?[Ff][Ee][Aa][Tt]\.|\(?[Ff][Tt]\.)[\s\S]", name_song)
                    name_song = request[0]
                    artists_song = [ artist["name"] for artist in track["artists"] ]
                    artists_song.append(request[1])

                elif re.match(r".*[^\.]\sby.*", name_song):
                    request = re.split(r"\sby\s", name_song)
                    name_song = request[0]
                    artists_song = [re.split(r"\s\[(?:.*)", request[1])[0]]

                else:
                    if re.match(r".*([Ff][Tt]\.|[Ff][Ee][Aa][Tt]\.).*", name_song):
                        request = re.search(r"^(.*)\s(?:\(?[Ff][Tt]\.|[Ff][Ee][Aa][Tt]\.)\s(.*)\)?", name_song)
                        name_song = request.group(1).split(" (")[0]
                        artists_song = [request.group(2)]
                    else:
                        artists_song = [ artist["name"] for artist in track["artists"] ]

                # Limpieza de texto en titulo y artistas
                name_song = name_song.strip()
                name_song = re.split(r"[\s\S](\(|\[)", name_song)[0]

                temp_lista = []
                for i, artist in enumerate(artists_song):
                    artists_song[i] = re.split(r"\s[&xX\,]\s", artist)
                    for elemento in artists_song[i]:
                        elemento = elemento.lstrip("\u200b")
                        if elemento[1] == " " and elemento[-3] == " ":
                            elemento = elemento[2:-3]
                        elemento = re.split(r"[\s\S](?:\(|\[|\/\/)", elemento)[0]
                        elemento = elemento.strip(")")
                        elemento = re.sub(r"[^\sa-zA-z0-9０-９ａ-ｚＡ-Ｚ$'!#%&\?¡¿！＂＃＄％＆＇＊＋，－．／À-þ]", "", elemento)
                        elemento = elemento.capitalize()
                        temp_lista.append(elemento)
                artists_song = temp_lista
                
                PLAYLIST.append([name_song, artists_song, track["duration"]])
        else:
            for track in canciones["tracks"]:
                name_song = track["title"]  # titulo de la cancion
                try:
                    artists_song = [ artist["name"] for artist in track["artists"] ] # artistas de la cancion
                except TypeError:
                    artists_song = ["Desconocido/s"]
                length_song = track["duration"]  # duracion de la cancion

                PLAYLIST.append([name_song, artists_song, length_song])

        if self.__modo_debug__:
            print("2. Playlist Obtenida.", end="\n")

        return PLAYLIST

    def OrdenarPlaylistAlgoritmo(self, Algoritmo: bool = False) -> str:
        """
        Ordernar la playlist segun algoritmo personalizado.

        Algoritmo 0: ordena dos veces, primero toma los artistas y los ordena alfabeticamente, luego ordena las canciones del artista donde canta solo y acompañado, es decir la playlist se ordena por artista y a su vez se ordena por cantidad de cantantes por canciones, dejando las canciones que tiene más de un cantante al final de la seccion del artista.

        Algoritmo 1: La variante de este algoritmo es que se separan las canciones por secciones, si el artista solo tiene una cancion en toda la playlist aparece en la segunda seccion, pero si tiene varias canciones en la playlist aparece en la seccion 1, al igual que la otra se ordena de la A-Z posicionando de primero las canciones donde canta solo, luego donde canta acompañado y luego donde aparece pero no es el principal (para que esta condicion se cumpla el principal no debe tener más de 1 cancion en la playlist), una vez terminada de ordenadas los artistas que tienen más de una cancion, se colocan los artistas que solo tiene una cancion ordenados de la A-Z.

        Notas:
        1. El diccionario crea la "Key" del elemento en base al nombre del artista (si este contiene espacios toma lo anterior al mismo), cantidad de artista que participan y el nombre de la cancion

        2. Al ejecutar el reordenamiento los elemento que esten abajo se posicioran arriba y desplazaran una posicion los elementos anteriores a el elemento que se reordeno, es decir cada que un elemento se reposicion primero,mueve todos los que estan detras de el una posicion para colocarse donde deberia ir una vez ordenada la playlist y para no confundir los index, hay que sumarle un valor cada vez que esto pase.

        Args:
            Algoritmo[bool]: algoritmo a usar, 0 para seccion simple y 1 para seccion doble.
        
        Returns:
            str: mensaje de correcta ejecuccion.
        """
        def __ActualizarListaYIndexs__(add_Elemnt):
            # codigo que se reutiliza para añadir las tracks a la lista final y el Index_ID al diccionario
            nombre_llave = add_Elemnt[1][0].split(" ")[0]+str(len(add_Elemnt[1]))+add_Elemnt[0]  # [NT: 1]

            LISTATERMINADA.append(add_Elemnt)
            INDEX_DOCS[nombre_llave] = {"index": canciones.index(add_Elemnt)}
            INDEX_DOCS[nombre_llave]["endIndex"] = LISTATERMINADA.index(add_Elemnt)
            INDEX_DOCS[nombre_llave]["ID"] = add_Elemnt[3]

        def __EjecutarOrdenamiento__(lista_ordenada: list, dics_index: dict):
            # bucle que reposiciona los elementos dentro de la playlist
            while len(lista_ordenada) != 0:
                # definir el "key" del diccionario a usar
                NOMBRE_TAG = lista_ordenada[0][1][0].split(" ")[0] + str(len(lista_ordenada[0][1])) + lista_ordenada[0][0]
                # Guardar el index que se usa
                index_guardado = dics_index[NOMBRE_TAG]["index"]

                if self.__modo_debug__:
                    print(f'!{NOMBRE_TAG} : PoIn {index_guardado}  /  PoFi {dics_index[NOMBRE_TAG]["endIndex"]}')

                #Se mueve de posicion el track con la API
                if index_guardado != dics_index[NOMBRE_TAG]["endIndex"]:
                    for comparador in dics_index.values():
                        if comparador["index"] == dics_index[NOMBRE_TAG]["endIndex"]:
                            self.__yt__.edit_playlist(playlistId=self.__playlist_ID__, moveItem=(lista_ordenada[0][3], comparador["ID"]))

                    # se reajusta los index_ID debido a modificar el orden de la playlist
                    for track in dics_index.values():
                        if track["index"] < index_guardado:
                            track["index"] += 1
                else:
                    if self.__modo_debug__:
                        print("[/]Elemento ya ordenado.")

                # Remover el elemento añadido de la lista original y el diccionario
                lista_ordenada.remove(lista_ordenada[0])
                dics_index.pop(NOMBRE_TAG)

        # Obtener las canciones de la playlist
        canciones = self.__obtenerPlaylistConIDs__()
        
        if self.__modo_debug__:
            print("3. Comprobando Playlist...")

        artistas = []
        for track in canciones:  # filtrar los artistas
            nombre_artista = track[1][0]
            if nombre_artista not in artistas:
                artistas.append(nombre_artista)
        del nombre_artista
        artistas.sort(key=lambda item: item.lower())

        # definir las listas donde se almacenaran los resultados del algoritmo
        LISTATERMINADA = []
        INDEX_DOCS = {}

        if not Algoritmo:  # Algoritmo 0
            for nombre_artista in artistas:
                # definir las listas vacias para canciones con un solo artista y varios
                artista_solista = []
                multiples_artistas = []

                # separa las canciones dependiendo de la cantidad de artistas
                for track in canciones:
                    if track[1][0] == nombre_artista:
                        if len(track[1]) != 1:
                            multiples_artistas.append(track)
                        else:
                            artista_solista.append(track)

                artista_solista.sort()
                multiples_artistas.sort()

                # Combina las lista y las añade a la lista principal ordenadas y extrae el index_ID
                for add_Elemnt in artista_solista + multiples_artistas:
                    __ActualizarListaYIndexs__(add_Elemnt)

            del canciones
            del artista_solista
            del multiples_artistas

            __EjecutarOrdenamiento__(LISTATERMINADA, INDEX_DOCS)

        else:  # Algoritmo 1
            def __CoincidenciasArtista__(Lista_canciones: list, artista_buscar: str) -> int:
                # identifica la veces que aparece un artistas como principal
                coincidencias = filter(lambda cancion: artista_buscar in cancion[1][0], Lista_canciones)
                return len(list(coincidencias))

            temp_segunda_seccion = []
            while len(artistas) != 0:
                nombre_artista = artistas[0]
                artista_solista = []
                multiples_artistas = []
                extra_artista = []
                segunda_seccion = []

                # comprobar cuantas veces aparece el cantante como principal
                coincidencias = 0
                for iterador in canciones:
                    if nombre_artista in iterador[1][0]:
                        coincidencias += 1
                del iterador

                if self.__modo_debug__:
                    print(f"Artista {nombre_artista} aparece: {coincidencias}\n")

                # separa las canciones dependiendo de la cantidad de artistas
                for track in canciones:
                    if track[1][0] == nombre_artista and coincidencias > 1:
                        # añade el elemento a la lista {Varios} si contiene más de un artista
                        if len(track[1]) != 1:
                            multiples_artistas.append(track)
                        else:
                            artista_solista.append(track)
                    elif nombre_artista in track[1][1:] and coincidencias > 1 and __CoincidenciasArtista__(canciones, track[1][0]) < 2:
                        # comprueba si el artista aparece como colaborador y el principal o anteriores a el, no tienen más de 2 canciones
                        add = True
                        for artista in track[1][1:track[1].index(nombre_artista)]:
                            if __CoincidenciasArtista__(canciones, artista) > 1:
                                add = False
                                break
                        if add:
                            extra_artista.append(track)
                        del add
                    elif track[1][0] == nombre_artista:
                        segunda_seccion.append(track)
                del coincidencias

                # Ordenada las lista
                artista_solista.sort()
                multiples_artistas.sort()
                extra_artista.sort()
                segunda_seccion.sort()
                
                if len(segunda_seccion) != 0:
                    temp_segunda_seccion.append(segunda_seccion[0])
                else:
                    for add_Elemnt in artista_solista + multiples_artistas + extra_artista:
                        __ActualizarListaYIndexs__(add_Elemnt)

                artistas.remove(nombre_artista)

            for track in temp_segunda_seccion:
                if track not in LISTATERMINADA:
                    __ActualizarListaYIndexs__(track)

            del canciones
            del nombre_artista
            del artista_solista
            del multiples_artistas
            del extra_artista
            del segunda_seccion
            del temp_segunda_seccion
            del __coincidenciasArtista__
            
            __EjecutarOrdenamiento__(LISTATERMINADA, INDEX_DOCS)

        if self.__modo_debug__:
            print("3. Playlist Ordenada.", end="\n")

        return "Playlist ordenada."

    def ComprobarPlaylist(self):
        """
        Comprueba las canciones de la playlist comparando mediante titulo y artistas, para eliminar las canciones duplicadas, funciona aunque la cancion sea la misma con diferente ID.
        
        Returns:
            str: mensaje de correcta ejecuccion.
        """
        #Obtiene las canciones en bruto
        CANCIONES = self.__obtenerPlaylistConIDs__()

        if self.__modo_debug__:
            print("3. Comprobando Playlist...")

        repetidas = []
        for cancion in CANCIONES: #Revisar las repetidas y añadirlas a la lista
            coincidencias = 0
            for track in CANCIONES:
                if cancion[0] == track[0] and cancion[1] == track[1]:
                    coincidencias += 1
            if coincidencias > 1:
                valores = [cancion[0:2], cancion[2], cancion[3]]
                if len(repetidas) == 0:
                    repetidas.append(valores)
                else:
                    contador = 0
                    for track in repetidas:
                        if cancion[0] == track[0][0] and cancion[1] == track[0][1]:
                            contador += 1
                    if contador < coincidencias-1:
                        repetidas.append(valores)
        del CANCIONES
        del coincidencias

        try:
            del valores
            if self.__modo_debug__:
                print("\n[!]Canciones duplicadas encontradas: ")

            for indx, eliminar_cancion in enumerate(repetidas):
                if self.__modo_debug__:
                    print("+ ", eliminar_cancion[0])
                repetidas[indx] = {"videoId": eliminar_cancion[1], "setVideoId": eliminar_cancion[2]}

            self.__yt__.remove_playlist_items(playlistId=self.__playlist_ID__, videos=repetidas)

        except UnboundLocalError:
            if self.__modo_debug__:
                print("[!] No se encontraron canciones duplicadas")
            return "No se encontraron duplicados"

        if self.__modo_debug__:
            print("3. Playlist Comprobada.")

        return "Duplicados eliminados."


class UsuarioYoutubeMusic():
    def __init__(self) -> None:
        self.__yt__ = YTMusic(auth="modulos/tokens/oauth_yt.json")
        listaplaylist = self.__yt__.get_library_playlists(None)
        self.PLAYLIST_USUARIO = []
        for playlist in listaplaylist:
            if playlist["playlistId"] != 'LM' and playlist["playlistId"] != 'SE':
                self.PLAYLIST_USUARIO.append(playlist)
