from ytmusicapi import YTMusic

class AdministradorYTMusic():
    def __init__(self, playlist_ID: str, modo_debug: bool = False) -> None:
        self.__yt__ = YTMusic(auth="modulos/tokens/oauth_yt.json")
        self.PLAYLIST_ID = playlist_ID
        self.__modo_debug__ = modo_debug

    def __ObtenerPlaylist__(self) -> dict:
        return self.__yt__.get_playlist(playlistId=self.PLAYLIST_ID, limit=None)

    def ImportarCanciones(self) -> list:
        """Obtiene las canciones, extrae el titulo, artistas, duracion y VideoID

        Returns:
            list: lista con los datos necesarios de las canciones
        """
        PLAYLIST = []
        canciones = self.__ObtenerPlaylist__()
        for track in canciones["tracks"]:
            name_song = track["title"] #titulo de la cancion
            artists_song = [artist["name"] for artist in track["artists"]] 
            length_song = track["duration"]
            song_ID = track["setVideoId"]
            PLAYLIST.append([name_song, artists_song, length_song, song_ID])
        return PLAYLIST

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
            index_docs[nombre_llave] = {
                "beforeAt": canciones[LISTATERMINADA.index(add_Elemnt)][3]}

        def __EjecutarOrdenamiento__(LISTATERMINADA, index_docs):
            # reposicionar elementos en la playlist de Youtube Music
            while len(LISTATERMINADA) != 0:
                # definir el "key" del diccionario a usar
                NOMBRE_TAG = LISTATERMINADA[0][1][0].split(
                    " ")[0]+str(len(LISTATERMINADA[0][1]))+LISTATERMINADA[0][0]
                # Guardar el VideoID que se usara
                index_ID = index_docs[NOMBRE_TAG]["beforeAt"]

                if self.__modo_debug__:
                    print(
                        f'!{NOMBRE_TAG} : PoFi {index_docs[NOMBRE_TAG]["beforeAt"]}')

                self.__yt__.edit_playlist(playlistId=self.PLAYLIST_ID, moveItem=(
                    LISTATERMINADA[0][3], index_docs[NOMBRE_TAG]["beforeAt"]))

                for i, item in enumerate(LISTATERMINADA):
                    idx = item[1][0].split(" ")[0]+str(len(item[1]))+item[0]
                    if i == 0:
                        i = 1
                    index_docs[idx]["beforeAt"] = index_docs[LISTATERMINADA[i-1][1][0].split(
                        " ")[0]+str(len(LISTATERMINADA[i-1][1]))+LISTATERMINADA[i-1][0]]["beforeAt"]

                # Remover el elemento añadido de la lista original y el diccionario
                LISTATERMINADA.remove(LISTATERMINADA[0])
                del index_docs[NOMBRE_TAG]

            print("\n\n\n------ Simulacion ------")
            for m in simulacion:
                print(m)

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
            # del canciones

            # for f in canciones:
            #    print(f)
            print("---\n\n")
            for f in LISTATERMINADA:
                print(f)
            print("---\n\n")
            for i, v in index_docs.items():
                print(f"{i}: {v}")
            print("---\n\n ------ Original -------")
            for x in canciones:
                print(x)

            __EjecutarOrdenamiento__(LISTATERMINADA, index_docs)

        else:  # Algoritmo 2
            def __CoincidenciasArtista__(Lista_canciones: list, artista_buscar: str):
                coincidencias = filter(
                    lambda cancion: artista_buscar in cancion[1][0], Lista_canciones)
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
                    print(
                        f"Artista {nombre_artista} aparece: {coincidencias}\n")

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


youtube = AdministradorYTMusic(
    "PLMl1Y5tQ5mHl5RNgU8NxVw20Xpr7J-Pj9", modo_debug=False).OrdenarPlaylistAlgoritmo()
