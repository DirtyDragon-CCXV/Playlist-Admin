import re
import json
import spotipy
from spotipy import util
# modulos.extensiones
from extensiones import ConvertirTextos, ConvertirTiempo
from spotipy.oauth2 import SpotifyClientCredentials

with open("modulos/tokens/credenciales_API.json", "r") as f:
    credenciales = json.loads(f.read())

# valores predeterminados tomados de JSON
user_ID = credenciales["user_ID"]
client_id = credenciales["client_id"]
secret_key = credenciales["secret_key"]
TOKEN = util.prompt_for_user_token(
    username=credenciales["username"],
    scope=credenciales["scope"],
    client_id=credenciales["client_id"],
    client_secret=credenciales["secret_key"],
    redirect_uri=credenciales["redirect_uri"]
)

class AdministradorSpotify():
    def __init__(self, playlist_Identificador: str, Debug: bool) -> None:
        # Valores Modificables
        self.__playlist_ID__ = playlist_Identificador  # ID de Playlist a interactuar
        self.__modo_debug__ = Debug

        if self.__modo_debug__:
            print("1. Autorizando Cliente...")

        # iniciar la API con las credenciales y token
        CREDENCIALES_CLIENTE = SpotifyClientCredentials(client_id, secret_key)
        self.__sp__ = spotipy.Spotify(
            client_credentials_manager=CREDENCIALES_CLIENTE, auth=TOKEN)
        self.NOMBRE_PLAYLIST = self.__sp__.playlist(
            self.__playlist_ID__)["name"]

        if self.__modo_debug__:
            print("1. Cliente Autorizado", end="\n")

    def __getPlaylist__(self) -> spotipy.Spotify.playlist_tracks:
        """
        Funcion que obtiene la lista completa de canciones de una playlist.

        @Usuario de StackOverflow - No la hice yo, encontre la parte del codigo.

        Returns:
            Spotify.playlist_tracks: Diccionario con los tracks de la playlist en bruto.
        """
        resultados = self.__sp__.user_playlist_tracks(
            None, self.__playlist_ID__)

        canciones = resultados['items']
        while resultados['next']:
            resultados = self.__sp__.next(resultados)
            canciones.extend(resultados['items'])

        return canciones

    def ImportarCanciones(self) -> list:  # DONE
        """
        Extrae las informacion basica: Titulo, Artista y Duracion de cada cancion de una playlist.

        Returns:
            list: lista que contiene el titulo, artistas y duracion de las canciones.
        """

        if self.__modo_debug__:
            print("2. Obteniendo Playlist.")

        canciones_playlist = self.__getPlaylist__()
        CANCIONES = []

        # se itera sobre la lista de las canciones para extraer: nombre de la cancion, nombre del artista y la duracion.
        for cancion in canciones_playlist:
            # nombre de la cancion
            nombre_cancion = cancion['track']['name']
            nombre_cancion = re.sub(
                r"\s[\(\[](?:[Ww]\/|[Ww][Ii][Tt][Hh].*|.*[&].*?)[\)\]]|\s[\(\[].*\s[Xx]\s.*|\s[\(\[][Ff][Ee][Aa][Tt].*[\)\]]", "", nombre_cancion)

            # artistas de la cancion
            nombre_artista = cancion['track']['artists']

            for x, iterador in enumerate(nombre_artista):
                if re.match(r"\b(?:\s?\w\s\w\s\w)+\b", iterador["name"]):
                    nombre_artista[x] = iterador["name"].replace(" ", "")

                else:
                    nombre_artista[x] = iterador["name"]

            # duracion de la cancion formateada
            duracion_cancion = ConvertirTiempo(cancion['track']['duration_ms'])

            # añadir cancion
            CANCIONES.append(
                [nombre_cancion, nombre_artista, duracion_cancion])

        if self.__modo_debug__:
            print("2. Playlist Obtenida.", end="\n")

        return CANCIONES

    def OrdenarPlaylist(self, Algoritmo: bool) -> str:  # DONE
        """
        Ordernar la playlist segun algoritmo personalizado.

        Algoritmo 0: ordena dos veces, primero toma los artistas y los ordena alfabeticamente, luego ordena las canciones del artista donde canta solo y canta acompañado, es decir la playlist se ordena por artista y a su vez se ordena por cantidad de cantantes por canciones, dejando las canciones que tiene más de un cantante al final de la seccion del artista.

        Algoritmo 1: La variante de este algoritmo es que se separan las canciones por secciones, es decir si el artista solo tiene una cancion en toda la playlist aparece en la segunda seccion, pero si tiene varias canciones en la playlist aparece en la seccion 1, al igual que la otra se ordena de la A-Z posicionando de primero las canciones donde canta solo, luego donde canta acompañado y luego donde aparece pero no es el principal (para que esta condicion se cumpla el principal no debe tener más de 1 cancion en la playlist), una vez terminada de ordenadas los artistas que tienen más de una cancion, se colocan los artistas que solo tiene una cancion ordenados de la A-Z.

        Notas:
            1. El diccionario crea la "Key" del elemento en base al nombre de la cancion y la primera letra del artista, para identicar canciones que tengan nombres iguales

            2. Al ejecutar el reordenamiento los elemento que esten abajo se posicioran arriba y desplazaran una posicion los elementos anteriores a el elemento que se reordeno, es decir cada que un elemento se reposicion primero,mueve todos los que estan detras de el una posicion para colocarse donde deberia ir una vez ordenada la playlist y para no confundir los index, hay que sumarle un valor cada vez que esto pase.

        Args:
            Algoritmo[bool]: algoritmo a usar, 0 para seccion simple y 1 para seccion doble.

        Returns:
            str: mensaje de correcta ejecuccion.
        """
        def __updateListAndIDs__(add_elemento):
            nombre_llave = add_elemento[1][0].split(
                # [NT: 1]
                " ")[0] + str(len(add_elemento[1])) + add_elemento[0]

            LISTATERMINADA.append(add_elemento)
            INDEX_DOCS[nombre_llave] = {"index": canciones.index(add_elemento)}
            INDEX_DOCS[nombre_llave]["endIndex"] = LISTATERMINADA.index(
                add_elemento)

        def __executeSort__(lista_ordenada: list, dics_index: dict):
            # reposicionar elementos en la playlist de Spotify
            while len(lista_ordenada) != 0:
                # definir el "key" del diccionario a usar
                NOMBRE_TAG = lista_ordenada[0][1][0].split(
                    " ")[0] + str(len(lista_ordenada[0][1])) + lista_ordenada[0][0]
                # Guardar el index que se usa
                index_guardado = dics_index[NOMBRE_TAG]["index"]

                if self.__modo_debug__:
                    print(f'!{NOMBRE_TAG} : PoIn {index_guardado}  /  PoFi {dics_index[NOMBRE_TAG]["endIndex"]}')

                # Enviar las modificaciones la API
                if index_guardado != dics_index[NOMBRE_TAG]["endIndex"]:
                    self.__sp__.user_playlist_reorder_tracks(
                        user=user_ID, playlist_id=self.__playlist_ID__, range_start=index_guardado, insert_before=dics_index[NOMBRE_TAG]["endIndex"])
                    # Ajustar los demas index al modificar la playlist [NT: 2]
                    for track in lista_ordenada:
                        index_tag = track[1][0].split(
                            " ")[0] + str(len(track[1])) + track[0]
                        if dics_index[index_tag]["index"] < index_guardado:
                            dics_index[index_tag]["index"] += 1
                else:
                    if self.__modo_debug__:
                        print("[/]Elemento ya ordenado.")

                # Remover el elemento añadido de la lista original y el diccionario
                lista_ordenada.remove(lista_ordenada[0])
                dics_index.pop(NOMBRE_TAG)

        # Obtener las canciones de la playlist
        canciones = self.ImportarCanciones()

        if self.__modo_debug__:
            print("3. Comprobando Playlist...")

        artistas = []
        for track in canciones:
            nombre_artista = track[1][0]
            if nombre_artista not in artistas:  # añadir el nombre del artista a la lista
                artistas.append(nombre_artista)
        del nombre_artista

        artistas.sort(key=lambda item: item.lower())

        # definir las listas donde se almacenaran los resultados del algoritmo
        LISTATERMINADA = []
        INDEX_DOCS = {}

        if not Algoritmo:  # Algoritmo 0
            for nombre in artistas:
                # definir las listas vacias para canciones con un solo artista y varios
                artista_solista = []
                multiples_artistas = []

                # separa las canciones dependiendo de la cantidad de artistas
                for elemento in canciones:
                    if elemento[1][0] == nombre:
                        if len(elemento[1]) != 1:
                            multiples_artistas.append(elemento)
                        else:
                            artista_solista.append(elemento)

                artista_solista.sort()
                multiples_artistas.sort()

                # Combina las lista y las añade a la lista principal ordenadas y extrae el index y endIndex
                for add_Elemnt in artista_solista + multiples_artistas:
                    __updateListAndIDs__(add_Elemnt)
            del canciones
            del artista_solista
            del multiples_artistas

            __executeSort__(LISTATERMINADA, INDEX_DOCS)

        else:  # Algoritmo 1
            def __coincidenciasArtista__(Lista_canciones: list, artista_buscar: str):
                coincidencias = filter(
                    lambda cancion: artista_buscar in cancion[1][0], Lista_canciones)
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
                    elif nombre_artista in track[1][1:] and coincidencias > 1 and __coincidenciasArtista__(canciones, track[1][0]) < 2:
                        # comprueba si el artista aparece como colaborador y el principal o anteriores a el, no tienen más de 2 canciones
                        add = True
                        for artista in track[1][1:track[1].index(nombre_artista)]:
                            if __coincidenciasArtista__(canciones, artista) > 1:
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
                        __updateListAndIDs__(add_Elemnt)

                artistas.remove(nombre_artista)

            for track in temp_segunda_seccion:
                if track not in LISTATERMINADA:
                    __updateListAndIDs__(track)

            __executeSort__(LISTATERMINADA, INDEX_DOCS)

        if self.__modo_debug__:
            print("3. Playlist Ordenada.", end="\n")

        return "Playlist ordenada."

    def ComprobarPlaylist(self) -> str:  # DONE
        """
        Comprueba las canciones de la playlist comparando mediante titulo y artistas, para eliminar las canciones duplicadas, funciona aunque la cancion sea la misma con diferente ID.

        Returns:
            str: mensaje de correcta ejecuccion.
        """
        if self.__modo_debug__:
            print("2. Obteniendo Playlist.")

        canciones_playlist = self.__getPlaylist__()
        CANCIONES = []
        # se itera sobre la lista de las canciones para extraer: nombre de la cancion, nombre del artista y el ID.
        for track in canciones_playlist:
            name_song = ConvertirTextos(
                track['track']['name'])  # nombre de la cancion
            name_artist = [ConvertirTextos(
                # artistas de la cancion
                artist["name"]) for artist in track['track']['artists']]
            id_cancion = track['track']['id']  # se coloca el id de la cancion
            CANCIONES.append([name_song, name_artist, id_cancion])
        del canciones_playlist

        if self.__modo_debug__:
            print("2. Playlist Obtenida.", end="\n")
            print("3. Comprobando Playlist...")

        repetidas = []
        # Revisar las repetidas y añadirlas a la lista
        for index, cancion in enumerate(CANCIONES):
            coincidencias = 0
            for track in CANCIONES:
                if cancion[2] == track[2] or (cancion[0] == track[0] and cancion[1] == track[1]):
                    coincidencias += 1

            if coincidencias > 1:
                existe = False
                valores = [cancion[0:2], cancion[2], index, existe]

                if len(repetidas) == 0:
                    repetidas.append(valores)
                else:
                    for num, track in enumerate(repetidas):
                        if cancion[0] == track[0][0] and cancion[1] == track[0][1]:
                            if cancion[2] == track[1]:
                                repetidas[num][3] = True
                            existe = True
                    if not existe:
                        repetidas.append(valores)
        del CANCIONES
        del coincidencias

        try:
            del index
            del existe

            if self.__modo_debug__:
                print("\n[!]Canciones duplicadas encontradas: ")

            eliminador_cancion = []
            for indx, cancion in enumerate(repetidas):
                if self.__modo_debug__:
                    print("+ ", cancion[0])

                repetidas[indx] = cancion[1]
                eliminador_cancion.append(cancion[2:4])

            self.__sp__.playlist_remove_all_occurrences_of_items(
                self.__playlist_ID__, repetidas)  # punto de eliminacion

            for iterador, add_cancion in enumerate(eliminador_cancion):
                if add_cancion[1]:
                    if iterador < 1:
                        self.__sp__.playlist_add_items(
                            self.__playlist_ID__, [repetidas[iterador]], [add_cancion[0]])
                    else:
                        self.__sp__.playlist_add_items(
                            self.__playlist_ID__, [repetidas[iterador]], [add_cancion[0]-1])
            del eliminador_cancion

        except UnboundLocalError:
            if self.__modo_debug__:
                print("[!] No se encontraron canciones duplicadas\n3. Playlist Comprobada.")

            return "No se encontraron duplicados"

        if self.__modo_debug__:
            print("3. Playlist Comprobada.")

        return "Duplicados eliminados."

    def InsertarCancionesPlaylist(self, datos_canciones: list):  # DONE
        """funcion encargada de buscar una cancion en base al titulo y el artista principal, para añadirla a la playlist.

        Args:
            datos_cancion (list): ['Tiutlo', ['Artistas', ...]]
        """
        if self.__modo_debug__:
            print("2. Buscando canciones...")
            no_disponibles = []

        add_canciones = []
        for track in datos_canciones:
            add = False

            nombre_cancion = ConvertirTextos(track[0]).lower()
            artistas_cancion = track[1]

            search_query = '"' + nombre_cancion + '" ' + artistas_cancion[0]

            consulta = self.__sp__.search(search_query, limit=5)
            del search_query

            for track in consulta["tracks"]["items"]:
                track_nombre = ConvertirTextos(track["name"]).lower()
                track_artistas = [name["name"] for name in track["artists"]]

                if nombre_cancion == track_nombre or re.search(nombre_cancion, track["name"]):
                    for cantante in artistas_cancion:
                        for artist in track_artistas:
                            if ConvertirTextos(cantante).lower() == ConvertirTextos(artist).lower():
                                add = True
                                add_canciones.append(track["id"])
                                break
                        if add:
                            break
                if add:
                    break

            if not add:
                print("Spotify : No encontro la cancion: ", track, end="\n")

                if self.__modo_debug__:
                    no_disponibles.append(track)

        if len(add_canciones) != 0:
            self.__sp__.playlist_add_items(
                self.__playlist_ID__, items=add_canciones)

            if self.__modo_debug__:
                print("2. Canciones añadidas correctamente.\n")

                if len(no_disponibles) != 0:
                    print("[!] No se encontraron...:")
                    for x in no_disponibles:
                        print(": ", x)

            return "Canciones Añadidas."

        else:
            if self.__modo_debug__:
                print("2. No se encontraron canciones a añadir")


class UsuarioSpotify():
    def __init__(self, Debug: bool, user_id: str = user_ID) -> list:
        # Valores Modificables
        self.__modo_debug__ = Debug

        if self.__modo_debug__:
            print("1. Autorizando Cliente...")

        # iniciar la API con las credenciales
        self.__sp__ = spotipy.Spotify(auth=TOKEN)
        __listaplaylist__ = self.__sp__.user_playlists(user=user_id)
        self.PLAYLIST_USUARIO = [playlist for playlist in __listaplaylist__[
            "items"] if playlist["owner"]["id"] == user_id]
        del __listaplaylist__

        if self.__modo_debug__:
            print("1. Cliente Autorizado", end="\n")

    def InfoTrack(self, track_id: str) -> dict:
        """obtiene los datos basicos de un track y los devuelve."""
        return self.__sp__.track(track_id)