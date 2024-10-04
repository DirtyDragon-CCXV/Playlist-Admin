import re
import json
from ytmusicapi import YTMusic
from extensiones import ConvertirTextos

with open("modulos/excepciones.json", "r") as f:
    excepciones = json.loads(f.read())

# valores predeterminados tomados de JSON
user_ID = excepciones["youtube"]["yt_user_ID"]
gods = excepciones["gods"]
del excepciones

class AdministradorYTMusic():
    def __init__(self, playlist_Identificador: str, Debug: bool = False) -> None:
        self.__playlist_ID__ = playlist_Identificador
        self.__modo_debug__ = Debug

        # iniciar Api
        if self.__modo_debug__:
            print("1. Autorizando Cliente...")

        self.__yt__ = YTMusic(auth="modulos/tokens/oauth_yt.json", language="es")
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


    @staticmethod
    def __ExcepcionTracks__(track:dict) -> list[str, str]: #-dev1
        #Excepcion para playlist que no cuenta con los titulos y clasificacion de artistas estandar
        
        caracteres = r"[^\u0020-\u007E\u00A0-\u036F\u0370-\u052F\u0600-\u077F\u2E80-\u2FD5\u3000-\u4DB5\u4E00-\u9FE6\uA640-\uA69F\u10330-\u1034A\uFF21-\uFF3A\uFF08\uFF09]"
        invertir_tituto_artista = False
        
        if re.match( r"[\u3000-\u4DB5\u4E00-\u9FE6]+.*?\s-\s[A-Za-z0-9\(\)]+", track["title"] ): #Filtro Canciones Japonesas -D1
            name_song = track['title']
            artists_song = [ artist["name"] for artist in track["artists"] ]
            
        elif re.match( r".*\s-\s.*", track["title"] ): # -D2
            separador_guion = re.split( r"\s-\s", track['title'] )
            
            name_song = separador_guion[1]
            artists_song = [ artist["name"] for artist in track["artists"] ]
            artists_song.append(separador_guion[0])
            
            invertir_tituto_artista = True
            
        elif re.match( r".*\sby\s.*", track['title'] ): # -D3
            separador_by = re.split( r"\sby\s", track['title'] )
            
            name_song = separador_by[0]
            artists_song = [ artist["name"] for artist in track["artists"] ]
            artists_song.append(separador_by[0])

        else:
            name_song = track['title']
            artists_song = [ artist["name"] for artist in track["artists"] ]
            
        
        # Limpieza de texto en titulo y artistas
        if invertir_tituto_artista:
            if name_song.lower() == "remix":
                for x, iterador in enumerate(artists_song):
                    if re.match( r".*[\(\[（\s]([Ff][Ee][Aa][Tt]|[Ff][Tt]|[Cc][Oo][Nn])\.?.*", iterador ):
                        separador = re.split( r"[\(\[（\s](?:[Ff][Ee][Aa][Tt]|[Ff][Tt]|[Cc][Oo][Nn])\.?", iterador )
                        
                        name_song = separador[0]
                        
                        if artists_song == None:
                            artists_song = separador[1]
                        else:
                            artists_song[x] = separador[1]

        else:
            pass
                        
        if re.search( r"[\(\[（\s][Rr][Ee][Mm][Ii][Xx][\)）\]\s]", track["title"] ) and not re.search( r"[\(\[（\s][Rr][Ee][Mm][Ii][Xx][\)）\]\s]", name_song ):
            name_song += " remix"
                
        if re.search( r"lyrics|prod|produced", name_song.lower() ):
            name_song = re.sub( r"[\[\(（\s]([Ll]yrics|[Pp]rod|[Pp]roduced).*[\)）\]\s]", "", name_song )
            
        if not re.search( r"[\[\(（\s]from", name_song.lower() ):
            name_song = re.sub( r"\(.*\)|（.*）\)|\[.*\]", "", name_song )
            
        name_song = re.sub(caracteres, "", name_song)
        name_song = name_song.strip()
        
        temp_lista = []
        for i, artista in enumerate(artists_song):
            artists_song[i] = re.split( r"\s[xX&yY]\s|[,、]\s?|\s?And\s?", artista ) # help - \s[Ff][Tt].\s
            
            for elemento in artists_song[i]:
                #excepciones unicas
                elemento = elemento.lstrip("\u200b")
                elemento = elemento.strip(")")
                elemento = re.split( r"\s[/\(\[]", elemento)[0]
                
                elemento = re.sub(caracteres, "", elemento).strip().capitalize()
                temp_lista.append(elemento)
                
        artists_song = temp_lista

        return [name_song, artists_song]


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
        
        for track in playlist_tracks["tracks"]:
            name_song, artists_song = self.__ExcepcionTracks__(track)
            CANCIONES.append( [name_song, artists_song, track["videoId"], track["setVideoId"]] )
                
        if self.__modo_debug__:
            print("2-1. Playlist Obtenida.", end="\n")
        
        return CANCIONES



    def ImportarCanciones(self) -> list: #-dev0
        """Obtiene las canciones, extrae el titulo, artistas, duracion.

        Returns:
            list: lista con los datos necesarios de las canciones
        """
        if self.__modo_debug__:
            print("2. Obteniendo Playlist.")
        
        canciones = self.__obtenerPlaylist__()
        PLAYLIST = []
        
        for track in canciones["tracks"]:
            name_song, artists_song = self.__ExcepcionTracks__(track)
                    
            PLAYLIST.append([name_song, artists_song, track["duration"]])

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



    def InsertarCancionesPlaylist(self, datos_cancion: list):
        dev = True # --------- Cdev -------------
        
        add_tracks = []
        for datos in datos_cancion:
            print(datos)
            added = False
            nombre_cancion = ConvertirTextos(datos[0]).lower()
            search_query = nombre_cancion
            try:
                artistas = datos[1]
                search_query += " " + artistas[0]
            except IndexError:
                pass
            
            loop = 0
            filtro = ["songs", "videos", None] #<- añadir lista con los filtros y usar el bucle como indice de iteraccion
            while loop < 2 and added == False:
                try:
                    consulta = self.__yt__.search(search_query, filtro[loop])[:3]
                    
                    for track in consulta:
                        if len(track["artists"]) == 0: # verifica si tiene los artistas
                            author = self.__yt__.get_song(track["videoId"])["videoDetails"]["author"].split(", ")
                            for enu, i in enumerate(author, 1):
                                if enu == len(author):
                                    track["artists"].append({"name" : i.lstrip("& ")})
                                else:
                                    track["artists"].append({"name" : i})
                                                            
                        print("\n\n", track, "\n\n")
                        # formatea el titulo del resultado de busqueda
                        nombre_song, artistas_song = AdministradorYTMusic.__ExcepcionTracks__(track)
                        nombre_song = ConvertirTextos(nombre_song).lower()
                        
                        if dev:
                            print("TrK: "+ nombre_song)
                            print("NS: "+ nombre_cancion)
                            print(re.search(nombre_cancion, nombre_song))
                            print(nombre_song == nombre_cancion)
                            print(artistas_song)
                            print(artistas)
                            print("\n\n")
                        
                        if re.search(r"remix", nombre_cancion):
                            remixBool = True
                        else:
                            remixBool = False
                        
                        if re.search(r"instrumental", nombre_cancion):
                            skip_extras = True
                        else:
                            skip_extras = False                
                        
                        # variables de verificacion
                        coincidencias_artista = False
                        if re.search(nombre_cancion, nombre_song) or nombre_song == nombre_cancion:
                            for artista in artistas:
                                artista = ConvertirTextos(artista).lower()
                                for cantante in artistas_song:
                                    cantante = ConvertirTextos(cantante).lower()
                                  
                                    if cantante == artista:
                                        coincidencias_artista = True
                                        break
                                
                                if coincidencias_artista:
                                    if dev: print("yes on point")
                                    
                                    if skip_extras:
                                        if remixBool:
                                            if re.search(r"remix",  nombre_song):
                                                added = True
                                                add_tracks.append(track["videoId"])
                                        else:
                                            added = True
                                            add_tracks.append(track["videoId"])
                                    if not re.search(r"live|instrumental", nombre_song):
                                        if remixBool:
                                            if re.search(r"remix",  nombre_song):
                                                added = True
                                                add_tracks.append(track["videoId"])
                                        else:
                                            added = True
                                            add_tracks.append(track["videoId"])
                                    break
                                    
                        if added:
                            break
                        
                except (IndexError, KeyError):
                    if loop > 1: break
                
                loop += 1
                
            if dev:
                input("continue?")
            
            if not added:
                print("Youtube Music : No encontro la cancion: ", datos, end="\n")

        if len(add_tracks) != 0:
            self.__yt__.add_playlist_items(self.__playlist_ID__, add_tracks, duplicates=True)



class UsuarioYoutubeMusic():
    def __init__(self, Debug: bool) -> None:
        self.__modo_debug__ = Debug

        if self.__modo_debug__:
            print("1. Autorizando Cliente...")
        
        self.__yt__ = YTMusic(auth="modulos/tokens/oauth_yt.json", language="es")

        listaplaylist = self.__yt__.get_library_playlists()
        self.PLAYLIST_USUARIO = [ title for title in listaplaylist ]
        del listaplaylist
        
        if self.__modo_debug__:
            print("1. Cliente Autorizado", end="\n")
    
    def InfoTrack(self, track_id: str) -> dict:
        """obtiene los datos basicos de un track y los devuelve.\n
        filter: [Top result, albums, artists, playlists, community_playlists, featured_playlists, songs, videos, profiles, podcasts, episodes]"""
        
        resultado = self.__yt__.search('"'+track_id+'"')
        
        for i in resultado:
            for nombre in i["artists"]: #excepcion por error de API
                if re.search("visualizaciones", nombre["name"].lower()):
                    i["artists"] = []
                    
            if i["videoId"] == track_id:
                if len(i["artists"]) == 0:
                    i["artists"] = [ {"name" : self.__yt__.get_song(i["videoId"])["videoDetails"]["author"]} ]
                return i

x = AdministradorYTMusic("PLMl1Y5tQ5mHleOf9-Tpq4pimsKqt16NcI").ImportarCanciones()

for i in x:
    print(i)
    
    
#print(UsuarioYoutubeMusic(False).InfoTrack("h3t6osnyPWI"))