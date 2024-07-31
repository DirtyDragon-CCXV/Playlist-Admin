import json
import spotipy
from spotipy import util
from spotipy.oauth2 import SpotifyClientCredentials

with open("modulos/tokens/credenciales_API.json", "r") as f:
    credenciales = json.loads(f.read())

user_ID = credenciales["user_ID"]
client_id = credenciales["client_id"]
secret_key = credenciales["secret_key"]
TOKEN = util.prompt_for_user_token(
    username = credenciales["username"],
    scope = credenciales["scope"],
    client_id = credenciales["client_id"],
    client_secret = credenciales["secret_key"],
    redirect_uri = credenciales["redirect_uri"]
)

class AdministradorSpotify():
    def __init__(self, playlist_Identificador: str, Debug: bool = False) -> None:
        # Valores Modificables
        self.__playlist_ID__ = playlist_Identificador  # ID de Playlist a interactuar
        self.__modo_debug__ = Debug

        # iniciar Api
        if self.__modo_debug__:
            print("1. Autorizando Cliente...")

        CREDENCIALES_CLIENTE = SpotifyClientCredentials(client_id, secret_key)  # establecer crendenciales del cliente
        # iniciar la API con las credenciales y token
        self.__sp__ = spotipy.Spotify(client_credentials_manager=CREDENCIALES_CLIENTE, auth=TOKEN)
        # establecer el nombre de la playlist en una variable
        self.NOMBRE_PLAYLIST = self.__sp__.playlist(self.__playlist_ID__)["name"]

        if self.__modo_debug__:
            print("1. Cliente Autorizado", end="\n\n")

    def __ObtenerPlaylist__(self) -> spotipy.Spotify.playlist_tracks:
        """
        Funcion que obtiene la lista completa de canciones de una playlist.

        Spotipy funciona por paginas, es decir toma las primeras 100 canciones, pero con la opcion ['next'], la API te permite continuar y tomar 100 más, si se repite el proceso en una bucle 'While' se pueden tomar todas las canciones

        @Usuario de StackOverflow - No la hice yo, encontre la parte del codigo.
        """
        resultados = self.__sp__.user_playlist_tracks(None, self.__playlist_ID__)
        canciones = resultados['items']
        while resultados['next']:
            resultados = self.__sp__.next(resultados)
            canciones.extend(resultados['items'])
        return canciones

    def OrdenarPlaylistAlgoritmo(self, Algoritmo: bool = False) -> str:
        """
        Ordernar la playlist segun algoritmo personalizado.

        Algoritmo 1: ordena dos veces, primero toma los artistas y los ordena alfabeticamente, luego ordena las canciones del artista donde canta solo y canta acompañado, es decir la playlist se ordena por artista y a su vez se ordena por cantidad de cantantes por canciones, dejando las canciones que tiene más de un cantante al final de la seccion del artista.

        Algoritmo 2: La variante de este algoritmo es que se separan las canciones por secciones, es decir si el artista solo tiene una cancion en toda la playlist aparece en la segunda seccion, pero si tiene varias canciones en la playlist aparece en la seccion 1, al igual que la otra se ordena de la A-Z posicionando de primero las canciones donde canta solo, luego donde canta acompañado y luego donde aparece pero no es el principal (para que esta condicion se cumpla el principal no debe tener más de 1 cancion en la playlist), una vez terminada de ordenadas los artistas que tienen más de una cancion, se colocan los artistas que solo tiene una cancion ordenados de la A-Z.

        Notas:
        1. El diccionario crea la "Key" del elemento en base al nombre de la cancion y la primera letra del artista, para identicar canciones que tengan nombres iguales

        2. Al ejecutar el reordenamiento los elemento que esten abajo se posicioran arriba y desplazaran una posicion los elementos anteriores a el elemento que se reordeno, es decir cada que un elemento se reposicion primero,mueve todos los que estan detras de el una posicion para colocarse donde deberia ir una vez ordenada la playlist y para no confundir los index, hay que sumarle un valor cada vez que esto pase.
        """
        def __ActualizarListaYIndexs__(add_Elemnt):
            LISTATERMINADA.append(add_Elemnt)
            nombre_llave = add_Elemnt[1][0].split(
                " ")[0]+str(len(add_Elemnt[1]))+add_Elemnt[0]  # [NT: 1]
            index_docs[nombre_llave] = {"index": canciones.index(add_Elemnt)}
            index_docs[nombre_llave]["endIndex"] = LISTATERMINADA.index(
                add_Elemnt)

        def __EjecutarOrdenamiento__(LISTATERMINADA, index_docs):
            # reposicionar elementos en la playlist de Spotify
            while len(LISTATERMINADA) != 0:
                # definir el "key" del diccionario a usar
                NOMBRE_TAG = LISTATERMINADA[0][1][0].split(" ")[0]+str(len(LISTATERMINADA[0][1]))+LISTATERMINADA[0][0]
                # Guardar el index que se usa
                index_guardado = index_docs[NOMBRE_TAG]["index"]
                if self.__modo_debug__:
                    print(f'!{NOMBRE_TAG} : PoIn {index_guardado}  /  PoFi {index_docs[NOMBRE_TAG]["endIndex"]}')

                # Enviar las modificaciones la API
                if index_docs[NOMBRE_TAG]["index"] != index_docs[NOMBRE_TAG]["endIndex"]:
                    self.__sp__.user_playlist_reorder_tracks(user=user_ID, playlist_id=self.__playlist_ID__, range_start=index_guardado, insert_before=index_docs[NOMBRE_TAG]["endIndex"])
                    # Ajustar los demas index al modificar la playlist [NT: 2]
                    for track in LISTATERMINADA:
                        index_tag = track[1][0].split(" ")[0]+str(len(track[1]))+track[0]
                        if index_docs[index_tag]["index"] < index_guardado:
                            index_docs[index_tag]["index"] += 1
                else:
                    if self.__modo_debug__:
                        print("[/]Elemento ya ordenado.")

                # Remover el elemento añadido de la lista original y el diccionario
                LISTATERMINADA.remove(LISTATERMINADA[0])
                del index_docs[NOMBRE_TAG]

        if self.__modo_debug__:
            print("2. Obteniendo Playlist...")
        
        # Obtener las canciones de la playlist
        canciones = self.ImportarCanciones()

        # Ordernar Lista y modificar el orden en spotify 
        artistas = []

        # filtrar los repetidos
        for track in canciones:
            nombre_artista = track[1][0]
            if nombre_artista not in artistas:  # añadir el nombre del artista a la lista
                artistas.append(nombre_artista)

        del nombre_artista

        artistas.sort(key=lambda item: item.lower())

        # definir las listas donde se almacenaran los resultados del algoritmo
        LISTATERMINADA = []
        index_docs = {}

        if Algoritmo == False:  # Algoritmo 1
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
                    __ActualizarListaYIndexs__(add_Elemnt)

            del artista_solista
            del multiples_artistas

            __EjecutarOrdenamiento__(LISTATERMINADA, index_docs)

        else:  # Algoritmo 2
            def __CoincidenciasArtista__(Lista_canciones: list, artista_buscar: str):
                coincidencias = filter(lambda cancion: artista_buscar in cancion[1][0], Lista_canciones)
                return len(list(coincidencias))

            TEMP = []
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

                # Ordenada las lista
                artista_solista.sort()
                multiples_artistas.sort()
                extra_artista.sort()
                segunda_seccion.sort()
                if len(segunda_seccion) != 0:
                    TEMP.append(segunda_seccion[0])
                else:
                    for add_Elemnt in artista_solista + multiples_artistas + extra_artista:
                        __ActualizarListaYIndexs__(add_Elemnt)

                artistas.remove(nombre_artista)

            for track in TEMP:
                if track not in LISTATERMINADA:
                    __ActualizarListaYIndexs__(track)

            del TEMP
            del artista_solista
            del multiples_artistas
            del extra_artista
            del segunda_seccion
            del coincidencias

            __EjecutarOrdenamiento__(LISTATERMINADA, index_docs)

        if self.__modo_debug__:
            print("3. Playlist Ordenada.", end="\n\n")
            
        return "Playlist ordenada."

    def ImportarCanciones(self) -> list:
        if self.__modo_debug__:
            print("2. Obteniendo Playlist.")
        # se obtienen todas las canciones de la playlist, en una lista.
        canciones_playlist = self.__ObtenerPlaylist__()

        canciones = []
        # se itera sobre la lista de las canciones para extraer: nombre de la cancion, nombre del artista y la duracion.
        for track in canciones_playlist:
            artistas = []
            name_song = track['track']['name']  # nombre de la cancion
            name_artist = track['track']['artists']  # artistas de la cancion
            for artist in name_artist:
                artistas.append(artist["name"])
            length_song = self.__ConvertirTiempo__(track['track']['duration_ms'])
            canciones.append([name_song, artistas, length_song])
        if self.__modo_debug__:
            print("2. Playlist Obtenida.", end="\n\n")
        return canciones

    def __ConvertirTiempo__(self, milisegundos: int) -> str:
        """
        convierte los milisegundos a minutos para mostrar la duracion de la cancion, con su separador ':'

        @Google Gemini, le pedi la porcion de codigo, me senti muy tonto al recordar que podia haberla hecho con el operardor de residuo '%'. me pase de pendejo :(.
        """
        minutos = int(milisegundos / 60000)
        segundos = int((milisegundos % 60000) / 1000)

        if segundos < 10:
            segundos_str = f"0{segundos}"
        else:
            segundos_str = str(segundos)

        return f"{minutos}:{segundos_str}"

    def ComprobarPlaylist(self) -> str:
        """
        Revisa las canciones en la playlist para eliminar duplicadas.
        """
        canciones_playlist = self.__ObtenerPlaylist__()
        canciones = []
        # se itera sobre la lista de las canciones para extraer: nombre de la cancion, nombre del artista y el ID.
        for track in canciones_playlist:
            name_song = track['track']['name']  # nombre de la cancion
            name_artist = track['track']['artists']  # artistas de la cancion
            artistas = []
            for artist in name_artist:
                artistas.append(artist["name"])
            id_cancion = track['track']['id']  # se coloca el id de la cancion
            canciones.append([name_song, artistas, id_cancion])

        del canciones_playlist

        if self.__modo_debug__:
            print("3. Comprobando Playlist...")
        repetidas = []
        for index, cancion in enumerate(canciones):
            coincidencias = 0
            for track in canciones:
                if cancion[0] == track[0] and cancion[1] == track[1]:
                    coincidencias += 1
            if coincidencias > 1:
                existe = False
                valor = [cancion[0:2], cancion[2], index, existe]
                if len(repetidas) == 0:
                    repetidas.append(valor)
                else:
                    for i, elemento in enumerate(repetidas):
                        if cancion[0] == elemento[0][0] and cancion[1] == elemento[0][1]:
                            if cancion[2] == elemento[1]:
                                repetidas[i][3] = True
                            existe = True
                    if not existe:
                        repetidas.append(valor)
        try:
            del existe
            if self.__modo_debug__:
                print("\n[!]Canciones duplicadas encontradas: ")

            indexs = []
            for indx, eliminar_cancion in enumerate(repetidas):
                if self.__modo_debug__:
                    print("+ ", eliminar_cancion[0])
                repetidas[indx] = eliminar_cancion[1]
                indexs.append(eliminar_cancion[2:4])

            self.__sp__.playlist_remove_all_occurrences_of_items(self.__playlist_ID__, repetidas)
            for iterador, add_cancion in enumerate(indexs):
                if add_cancion[1]:
                    if iterador < 1:
                        self.__sp__.playlist_add_items(self.__playlist_ID__, [repetidas[iterador]], [add_cancion[0]])
                    else:
                        self.__sp__.playlist_add_items(self.__playlist_ID__, [repetidas[iterador]], [add_cancion[0]-1])

            del repetidas
            del indexs

        except UnboundLocalError:
            if self.__modo_debug__:
                print("[!] No se encontraron canciones duplicadas")
            return "No se encontraron duplicados"
            
        del canciones

        if self.__modo_debug__:
            print("3. Playlist Comprobada.")
            
        return "Duplicados eliminados."

class UsuarioSpotify():
    def __init__(self, user_id: str = user_ID, Debug: bool = False) -> list:
        """_summary_

        Args:
            user_id (str, optional): _description_. Defaults to user_ID.
            Debug (bool, optional): _description_. Defaults to False.

        Returns:
            list: _description_
        """
        # Valores modificables
        self.__modo_debug__ = Debug

        # iniciar la API con las credenciales
        self.__sp__ = spotipy.Spotify(auth=TOKEN)
        listaplaylist = self.__sp__.user_playlists(user=user_id)
        self.PLAYLIST_USUARIO = []
        for playlist in listaplaylist["items"]:
            if playlist["owner"]["id"] == user_id:self.PLAYLIST_USUARIO.append(playlist)