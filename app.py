import re
import sys
import time
import json
import sqlite3 as sql
from spotipy.exceptions import SpotifyException
from modulos.spotify import AdministradorSpotify, UsuarioSpotify
from modulos.yt_music import AdministradorYTMusic, UsuarioYoutubeMusic

# ---------------------------------------------------------------------------- #
#                             funciones auxiliares                             #
# ---------------------------------------------------------------------------- #
def __tagNameFormat__(track: list) -> str:
    """creador de keys para el diccionario de las excepciones"""
    return track[1][0].split(" ")[0].lower() + str(len(track[1])) + __limpiarTexto__(track[0].lower())

def __limpiarTexto__(texto: str):
    """
    funcion encargada de recibir un texto, limpiar caracteres, separar, quitar parentesis, corchetes, etc.
    formatea el texto en otras palabras.
    
    Arg: 'texto' : str = texto de entrada a formatear
    Returs: 'texto' : str = texto formateado
    """
    if re.search(r"[Ll][Ii][Vv][Ee]", texto) or re.match(r"^[\u3000-\u4DB5\u4E00-\u9FE6]+\b\s?(?!\([Cc]|（[Cc]).*(\s-\s)?\w*", texto):
        pass
            
    elif re.search(r"[Rr][Ee][Mm][Ii][Xx]", texto):
        texto = re.sub(r"\((?![Rr][Ee][Mm][Ii][Xx]).*\)", "", texto)

    else:
        texto = re.split(r"\s[-]\s", texto)[0].strip()
        texto = re.sub(r"\s?\(.*\)\s?|\s?（.*）?\s?", "", texto)
        
    texto = re.sub(r"[^\u0020-\u007E\u00A0-\u036F\u0370-\u052F\u0600-\u077F\u2E80-\u2FD5\u3000-\u4DB5\u4E00-\u9FE6\uA640-\uA69F\u10330-\u1034A\uFF21-\uFF3A\uFF08\uFF09]", "", texto)
    texto = re.sub(r"(\s)+", " ", texto)
    
    return texto.strip()

def __formatearNombrePlaylist__(nombre: str):
    """
    funcion encargada de recibir el nombre de una playlist, lo formatea quitando caracteres, espacios, iconos, etc.
    en otras palabras formatea el texto dejandolo en una version simple para usar en una Base de Datos.
    
    Arg: 'nombre' : str = texto de entrada a formatear
    Returs: 'nombre' : str = texto formateado
    """
    nombre = nombre.lower()
    BLOQUEOS = """@"#$%&/()=?¡¨*[]{}+´:;-.,'"""
    listaNombre = []
    espacios = 0
    letras = 0
    if len(nombre) > 2:
        for caracter in nombre:
            if ord(caracter) >= 33 and ord(caracter) <= 165:
                if caracter not in BLOQUEOS:
                    listaNombre.append(caracter)
                    letras += 1
            elif ord(caracter) == 32:
                listaNombre.append("_")
                espacios += 1
            elif ord(caracter) == 120392:
                #Excepcion para playlist "Mood: Perreo" debido a que tiene caracteres especiales en su nombre
                return "mood_perreo"
        if listaNombre[-1] == "_":
            listaNombre.pop()
            espacios -= 1
        listaNombre = "".join(listaNombre)
        if letras == espacios+1:
            listaNombre = listaNombre.replace("_", "")
        return listaNombre
    else:
        return nombre

# ---------------------------------------------------------------------------- #
#                             funciones principales                            #
# ---------------------------------------------------------------------------- #
def SqlOpcion(argument: str):
    """Conectar con la base de datos y ejecutar secuencias SQL

        Argument : (Secuencia SQL a ejecutar)

        Nt: la variable {servicio_predeterminado} diferencia si conectar con la DB de Spotify y Youtube, el servicio predeterminado es Spotify
    """
    try:
        if servicio_predeterminado:
            con = sql.connect(spotify_path)
        else:
            con = sql.connect(youtube_path)
        m = con.cursor()
        m.execute(argument)
        values = m.fetchall()
        con.commit()
        con.close()
        return values
    except KeyboardInterrupt:
        con.close()

def CompararPlaylists(AllPlaylist: bool, IDplaylist: str, Debug: bool):
    def __comparador__(playlistMain:list, playlistSecond:list, id:int):
        #id: 0 for spotify
        #id: 1 for youtube
        
        exit_playlist = []
        for track in playlistMain:
            add = True
            track_name = track[0]
            track_name = __limpiarTexto__(track_name)
            track_artist = track[1][0]
            track_artist = __limpiarTexto__(track_artist)
            
            try:
                if id == 0:
                    exclusion_sp[ __tagNameFormat__(track) ]
                else:
                    exclusion_yt[ __tagNameFormat__(track) ]
                    
                continue
            except KeyError:
                for song in playlistSecond:
                    try:
                        song_name = exclusion_main[ __tagNameFormat__(song) ][0]
                        artist_song = exclusion_main[ __tagNameFormat__(song) ][1][0]
                    except KeyError:
                        song_name = song[0]
                        artist_song = song[1][0]
                        
                    song_name = __limpiarTexto__(song_name)
                    artist_song = __limpiarTexto__(artist_song)
                    
                    if id == 0:
                        compador = track_name.lower()
                    else:
                        compador = song_name.lower()
                    
                    """if track[2] == "2:30":
                        print("SP: "+track_name)
                        print("YT: "+song_name)
                        print(re.search(track_name.lower(), song_name.lower()))
                        print(re.search(song_name.lower(), track_name.lower()))
                        print(track_name.lower() == song_name.lower())
                        print(track_artist.lower() == artist_song.lower())
                        print("SP: "+track_artist.lower())
                        print("YT: "+artist_song.lower())
                        print("\n\n")"""
                    
                    #r"[\u3000-\u4DB5\u4E00-\u9FE6]+.*(\s-\s)?[A-Za-z0-9\(\)]+.*" -- NO BORRAR HASTA QUE FUNCIONE, HAZLE CASO A TU PASADO, EL SIEMPRE TE ENSEÑA ALGO...
                    if re.match(r"^[\u3000-\u4DB5\u4E00-\u9FE6]+.*(\s-\s)?\w+.*", compador):
                        if re.search(track_name.lower(), song_name.lower()) != None and track_artist.lower() == artist_song.lower():
                            #print("one enter")
                            add = False
                            break
                            
                        if re.search(song_name.lower(), track_name.lower()) != None and track_artist.lower() == artist_song.lower():
                            #print("two enter")
                            add = False
                            break
                        
                    else:
                        if song_name.lower() == track_name.lower() and track_artist.lower() == artist_song.lower():
                            add = False
                            break
                            
                if add:
                    try:
                        exit_playlist.append(exclusion_main[ __tagNameFormat__(track) ])
                    except KeyError:
                        exit_playlist.append(track)
            #input("continue?")
                        
        return exit_playlist  
    
    sp = UsuarioSpotify(Debug = Debug).PLAYLIST_USUARIO
    yt = UsuarioYoutubeMusic(Debug = Debug).PLAYLIST_USUARIO
    
    if AllPlaylist:
        print("no deberias estar aqui")
        exit()
        """por desarrollar"""
        for sp_playlist in sp:
            for yt_playlist in yt:
                if sp_playlist["name"] == yt_playlist["title"]:
                    sp_engine = AdministradorSpotify(sp_playlist["id"]).ImportarCanciones()
                    yt_engine = AdministradorYTMusic(yt_playlist["playlistId"]).ImportarCanciones()
                    no_on_yt = [] #youtube comparador
                    for track in sp_engine:
                        add = True
                        for song in yt_engine:
                            if track[0].lower() == song[0].lower() and track[1][0].lower() == song[1][0].lower():
                                add = False
                                break
                        if add: no_on_yt.append(track)
                    no_on_sp = [] #spotify comparador
                    for song in yt_engine:
                        add = True
                        for track in sp_engine:
                            if song[0].lower() == track[0].lower() and song[1][0].lower() == track[1][0].lower():
                                add = False
                                break
                        if add: no_on_sp.append(song)
                    with open("add_to_Youtube.txt", "w") as f:
                        for reader in no_on_yt:
                            f.write(str(reader)+"\n")
                    with open("add_to_Spotify.txt", "w") as f:
                        for reader in no_on_sp:
                            f.write(str(reader)+"\n")
    else:
        if len(IDplaylist) == 22:
            playlist = {"spotifyID": IDplaylist}
            for search in sp:
                if search["id"] == IDplaylist:
                    nombre_playlist = search["name"]
                    break
            for search in yt:
                if search["title"].lower() == nombre_playlist.lower():
                    playlist["youtubeID"] = search["playlistId"]
                    break
        else:
            playlist = {"youtubeID": IDplaylist}
            for search in yt:
                if search["playlistId"] == IDplaylist:
                    nombre_playlist = search["title"]
                    break
            for search in sp:
                if search["name"].lower() == nombre_playlist.lower():
                    playlist["spotifyID"] = search["id"]
                    break
                
        sp_engine = AdministradorSpotify(playlist["spotifyID"])
        sp_playlist = sp_engine.ImportarCanciones()
        
        yt_engine = AdministradorYTMusic(playlist["youtubeID"])
        yt_playlist = yt_engine.ImportarCanciones()
        
        with open(excepciones_path, "r") as f:
            data = json.load(f)
            
            exclusion_yt = data["yt"]
            exclusion_sp = data["sp"]
            exclusion_main = data["main"]
            del data
        
        #youtube comparador
        no_on_yt = __comparador__(sp_playlist, yt_playlist, 1)
        
        #spotify comparador
        no_on_sp = __comparador__(yt_playlist, sp_playlist, 0)
        
        print("\n-----")
        if len(no_on_yt) != 0:
            for i in no_on_yt: print(i)
        else:
            print("YT - NULL")
            
        print("\n-----")
        
        if len(no_on_sp) != 0:
            for x in no_on_sp: print(x)
        else:
            print("SP - NULL")
            
        print("\n-----\n")
        
        if len(no_on_yt) != 0:
            yt_engine.InsertarCancionesPlaylist(datos_cancion=no_on_yt)
        if len(no_on_sp) != 0:
            sp_engine.InsertarCancionesPlaylist(datos_cancion=no_on_sp)

    # ---------------------------------------------------------------------------- #
    #                               funciones spotify                              #
    # ---------------------------------------------------------------------------- #
def ActualizarDBSpotify(AllPlaylist: bool = True, IDplaylist: str = None, Debug: bool = False):
    """Conecta con la BD para verificar si los datos existen, actualizarlos o eliminarlos y volverlos a añadir.

    Args:
        AllPlaylist (bool, optional): establecer si se ejecutara la accion en todas las playlist del usuario o individualmente en una playlist. Defaults to True.
        IDplaylist (str, optional): Indicar el ID de la playlist donde se ejecutara la accion. Defaults to None.
        Debug (bool, optional): establecer si el modo desarrollador esta activado para ver los avisos de ejecucion. Defaults to False.

    Raises:
        UserWarning: Error generado por no especificar una playlist al interactuar con una sola playlist (AllPlaylist = False)
    """
    def __actualizarDB__(id_playlist: str = IDplaylist):
        """Conectar con la funcion [SqlOpcion] para añadir un conjunto de valores

        Args:
            id_playlist (str, optional): ID de la playlist a iterar. Defaults to IDplaylist.
        """
        def __addSongs__():
            """Conectar con la funcion [SqlOpcion] para añadir un conjunto de valores"""
            for cancion in canciones_playlist:
                if Debug:
                    print(cancion[0], cancion[1], cancion[2])
                artista = str(cancion[1]).replace('"', "'")
                SqlOpcion('INSERT INTO "{}" VALUES ("{}", "{}", "{}")'.format(playlist_nombre, cancion[0].replace('"', '""'), artista, cancion[2]))
            if Debug:
                print("Canciones added.\n")

        engine = AdministradorSpotify(id_playlist, Debug=Debug)
        playlist_nombre = __formatearNombrePlaylist__(engine.NOMBRE_PLAYLIST)
        if not "test" in playlist_nombre.lower():
            if Debug:
                print(f"Nombre Playlist: {playlist_nombre}\n")
            Existe = SqlOpcion(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{playlist_nombre}'")
            canciones_playlist = engine.ImportarCanciones()
            if len(Existe) != 0:
                songs = SqlOpcion(f'SELECT "name song" FROM "{playlist_nombre}"')
                if len(canciones_playlist) == len(songs):
                    for index, item in enumerate(canciones_playlist):
                        if item[0] == songs[index][0]:
                            pass
                        else:
                            print("[!] Orden no coincidente con DB")
                            SqlOpcion(f"DELETE FROM '{playlist_nombre}'")
                            __addSongs__()
                            break
                else:
                    if Debug:
                        print("Escalas Desiguales, limpiando y actualizando...\n")
                    SqlOpcion(f"DELETE FROM '{playlist_nombre}'")
                    __addSongs__()
            else:
                if Debug:
                    print("Tabla inexistente\n")
                SqlOpcion( f"CREATE TABLE '{playlist_nombre}' ('name song' TEXT, 'artist' TEXT, 'length' INT)")           
                if Debug:
                    print("Tabla Creada, adding canciones...\n")
                __addSongs__()

    if AllPlaylist:
        print("Actualizando playlists...")
        usuarioPlaylists = UsuarioSpotify().PLAYLIST_USUARIO
        for playlist in usuarioPlaylists:
            __actualizarDB__(playlist["id"])
        return "Playlists actualizadas."
    else:
        print("Actualizando playlist...")
        __actualizarDB__()
        return "Playlist actualizada."


def ActualizarOrdenPlaylistSpotify(AllPlaylist: bool = True, IDplaylist: str = None, Debug: bool = False, Algoritmo: bool = False):
    if AllPlaylist:
        print("Ordenando playlists...")
        usuarioPlaylists = UsuarioSpotify().PLAYLIST_USUARIO
        for playlist in usuarioPlaylists:
            if not "test" in playlist["name"].lower():
                engine = AdministradorSpotify(playlist_Identificador=playlist["id"], Debug=Debug)
                engine.ComprobarPlaylist()
                if playlist["id"] == sp_excepcion_playlist_uno or playlist["id"] == sp_excepcion_playlist_dos:
                    engine.OrdenarPlaylistAlgoritmo(Algoritmo=True)
                else:
                    engine.OrdenarPlaylistAlgoritmo(Algoritmo=False)
        return "Playlists ordenadas."
    else:
        print("Ordenando playlist...")
        engine = AdministradorSpotify(playlist_Identificador=IDplaylist, Debug=Debug)
        return engine.OrdenarPlaylistAlgoritmo(Algoritmo=Algoritmo)
        
def ComprobarPlaylistSpotify(AllPlaylist: bool = True, IDplaylist: str = None, Debug: bool = False) -> str:
    if AllPlaylist:
        print("Inspeccionando playlists...")
        usuarioPlaylists = UsuarioSpotify().PLAYLIST_USUARIO
        for playlist in usuarioPlaylists:
            if not "test" in playlist["name"].lower():
                engine = AdministradorSpotify(playlist_Identificador=playlist["id"], Debug=Debug)
                print(engine.ComprobarPlaylist())
        return "Playlists revisadas."
    else:
        print("Inspeccionando playlist...")
        engine = AdministradorSpotify(playlist_Identificador=IDplaylist, Debug=Debug)
        return engine.ComprobarPlaylist()






    # ---------------------------------------------------------------------------- #
    #                            funciones youtube music                           #
    # ---------------------------------------------------------------------------- #
def ActualizarDBYoutubeMusic(AllPlaylist: bool = True, IDplaylist: str = None, Debug: bool = False):
    """Conecta con la BD para verificar si los datos existen, actualizarlos o eliminarlos y volverlos a añadir.

    Args:
        AllPlaylist (bool, optional): establecer si se ejecutara la accion en todas las playlist del usuario o individualmente en una playlist. Defaults to True.
        IDplaylist (str, optional): Indicar el ID de la playlist donde se ejecutara la accion. Defaults to None.
        Debug (bool, optional): establecer si el modo desarrollador esta activado para ver los avisos de ejecucion. Defaults to False.

    Raises:
        UserWarning: Error generado por no especificar una playlist al interactuar con una sola playlist (AllPlaylist = False)
    """
    def __actualizarDB__(id_playlist: str = IDplaylist):
        """Conectar con la funcion [SqlOpcion] para añadir un conjunto de valores

        Args:
            id_playlist (str, optional): ID de la playlist a iterar. Defaults to IDplaylist.
        """
        def __addSongs__():
            """Conectar con la funcion [SqlOpcion] para añadir un conjunto de valores"""
            for cancion in canciones_playlist:
                if Debug:
                    print(cancion[0], cancion[1], cancion[2])
                artista = str(cancion[1]).replace('"', "'")
                SqlOpcion('INSERT INTO "{}" VALUES ("{}", "{}", "{}")'.format(playlist_nombre, cancion[0].replace('"', '""'), artista, cancion[2]))
            if Debug:
                print("Canciones added.\n")

        engine = AdministradorYTMusic(id_playlist, modo_debug=Debug)
        playlist_nombre = __formatearNombrePlaylist__(engine.NOMBRE_PLAYLIST)
        if not "test" in playlist_nombre.lower():
            if Debug:
                print(f"Nombre Playlist: {playlist_nombre}\n")
            Existe = SqlOpcion(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{playlist_nombre}'")
            canciones_playlist = engine.ImportarCanciones()
            if len(Existe) != 0:
                songs = SqlOpcion(f'SELECT "name song", "artist", "length"  FROM "{playlist_nombre}"')
                if len(canciones_playlist) == len(songs):
                    for index, item in enumerate(canciones_playlist):
                        if item[0] == songs[index][0] and str(item[1]).replace('"', "'") == songs[index][1] and item[2] == songs[index][2]:
                            pass
                        else:
                            if Debug:
                                print("[!] Orden no coincidente con DB")
                            SqlOpcion(f"DELETE FROM '{playlist_nombre}'")
                            __addSongs__()
                            break
                else:
                    if Debug:
                        print("Escalas Desiguales, limpiando y actualizando...\n")
                    SqlOpcion(f"DELETE FROM '{playlist_nombre}'")
                    __addSongs__()
            else:
                if Debug:
                    print("Tabla inexistente\n")
                SqlOpcion( f"CREATE TABLE '{playlist_nombre}' ('name song' TEXT, 'artist' TEXT, 'length' INT)")
                if Debug:
                    print("Tabla Creada, adding canciones...\n")
                __addSongs__()

    if AllPlaylist:
        print("Actualizando playlists...")
        usuarioPlaylists = UsuarioYoutubeMusic().PLAYLIST_USUARIO
        for playlist in usuarioPlaylists:
            __actualizarDB__(playlist["playlistId"])
        return "Playlists actualizadas."
    else:
        print("Actualizando playlist...")
        __actualizarDB__()
        return "Playlist actualizada."
        
def ActualizarOrdenPlaylistYTMusic(AllPlaylist: bool = True, IDplaylist: str = None, Debug: bool = False, Algoritmo: bool = False):
    if AllPlaylist:
        print("Ordenando playlists...")
        usuarioPlaylists = UsuarioYoutubeMusic().PLAYLIST_USUARIO
        for playlist in usuarioPlaylists:
            if not "test" in playlist["title"].lower():
                engine = AdministradorYTMusic(playlist_Identificador=playlist["playlistId"], Debug=Debug)
                engine.ComprobarPlaylist()
                if playlist["playlistId"] == yt_excepcion_playlist_uno or playlist["playlistId"] == yt_excepcion_playlist_dos:
                    engine.OrdenarPlaylistAlgoritmo(Algoritmo=True)
                else:
                    engine.OrdenarPlaylistAlgoritmo(Algoritmo=False)
        return "Playlists ordenadas."
    else:
        print("Ordenando playlist...")
        engine = AdministradorYTMusic(playlist_Identificador=IDplaylist, Debug=Debug)
        return engine.OrdenarPlaylistAlgoritmo(Algoritmo=Algoritmo)
        
def ComprobarPlaylistYTMusic(AllPlaylist: bool = True, IDplaylist: str = None, Debug: bool = False) -> str:
    if AllPlaylist:
        print("Inspeccionando playlists...")
        usuarioPlaylists = UsuarioYoutubeMusic().PLAYLIST_USUARIO
        for playlist in usuarioPlaylists:
            if not "test" in playlist["name"].lower():
                engine = AdministradorYTMusic(playlist_Identificador=playlist["playlistId"], Debug=Debug)
                print(engine.ComprobarPlaylist())
        return "Playlists revisadas."
    else:
        print("Inspeccionando playlist...")
        engine = AdministradorYTMusic(playlist_Identificador=IDplaylist, Debug=Debug)
        return engine.ComprobarPlaylist()

if __name__ == "__main__":
    TimeIn = time.time()  # tomar tiempo al momento de inicio
    argvs = sys.argv[1:] #tomar argumentos
    
    # ------------------------------ Debug Opciones ------------------------------ #
    with open("modulos/excepciones.json", "r") as f:
        excepcion = json.loads(f.read())

        if argvs[0] == "--d" or argvs[0] == "--debug":
            if excepcion["modo_debug"]: excepcion["modo_debug"] = False
            else: excepcion["modo_debug"] = True
            with open("modulos/excepciones.json", "w") as f:
                json.dump(excepcion, f, indent=2)
            print("Ajuste actualizado.")
            exit()

    # ---------------------------- parametros glabales --------------------------- #
    modo_debug = excepcion["modo_debug"] #cambiar el parametro 'debug'
    sp_excepcion_playlist_uno = excepcion["spotify"]["excepcion_playlist_uno"]
    sp_excepcion_playlist_dos = excepcion["spotify"]["excepcion_playlist_dos"]
    yt_excepcion_playlist_uno = excepcion["youtube"]["excepcion_playlist_uno"]
    yt_excepcion_playlist_dos = excepcion["youtube"]["excepcion_playlist_dos"]
    spotify_path = excepcion["spotify_path"]
    youtube_path = excepcion["youtube_path"]
    excepciones_path = excepcion["excepciones_main_path"]
    canales_guardados = excepcion["saved_channels"]
    
    try:
        if argvs[0] == "-h" or argvs[0] == "-help":
            print("""App ([-sp|-spotify] | [-yt|-youtube] | [-cs|-cross] | [-adexc|-addExcept]) ([-u|-update] | [-s|-sort] | [-r|-review]) *Url_playlist* {sort: --A1 | --A2}
    
    Administrador de Playlist para Youtube Music y Spotify
    
    Uso:
        -sp | -spotify : indica que se usara el servicio de spotify.
        -yt | -youtube : indica que se usara el servicio de youtube music.
        -cs | -cross : comparar la/s playlist/s de Spotify y Youtube Music
        
    Funciones:
        -u | -update : actualiza o crea la tabla para la playlist/s correspondiente.
        -s | -sort : ordena la playlist mediante dos algoritmos personalizados {--A1:'Algoritmo de secciones simples',
                                                                                --A2: 'Algoritmo de secciones dobles'}
        -r | -review : comprueba o revisa la playlist para eliminar canciones duplicadas.
        
    Desarrollador:
        --d | --debug : activar el modo debug (ejecutar el comando SOLO [sin más parametros] para cambiar 
                        la variable del programa, ejecutar nuevamente para desactivar el modo debug)
            """)
           
            
        elif argvs[0] == "-yt" or argvs[0] == "-youtube": #Seccion Youtube
            servicio_predeterminado = False
            if argvs[1] == "-u" or argvs[1] == "-update":
                try:
                    if len(argvs) > 3:
                        raise ValueError("Error en Youtube (update) if")
                    else:
                        print(ActualizarDBYoutubeMusic(AllPlaylist=False, IDplaylist=argvs[2], Debug=modo_debug))
                except IndexError:
                    print(ActualizarDBYoutubeMusic(AllPlaylist=True, Debug=modo_debug))
            
            elif argvs[1] == "-s" or argvs[1] == "-sort":
                try:
                    try:
                        if len(argvs) > 4:
                            raise ValueError("Error en Youtube (sort) if")
                        elif argvs[3] == "--A2":
                            print(ActualizarOrdenPlaylistYTMusic(AllPlaylist=False, IDplaylist=argvs[2], Algoritmo=True, Debug=modo_debug))
                        elif argvs[3] == "--A1":
                            print(ActualizarOrdenPlaylistYTMusic(AllPlaylist=False, IDplaylist=argvs[2], Algoritmo=False, Debug=modo_debug))
                        else:
                            print("Error: Algoritmo de orden invalidado.")
                    except IndexError:
                        print(ActualizarOrdenPlaylistYTMusic(AllPlaylist=False, IDplaylist=argvs[2], Debug=modo_debug))
                except IndexError:
                    print(ActualizarOrdenPlaylistYTMusic(AllPlaylist=True, Debug=modo_debug))
            
            elif argvs[1] == "-r" or argvs[1] == "-review":
                try:
                    if len(argvs) > 3:
                            raise ValueError("Error en Youtube (review) if")
                    else:
                        print(ComprobarPlaylistYTMusic(AllPlaylist=False, IDplaylist=argvs[2], Debug=modo_debug))
                except IndexError:
                    print(ComprobarPlaylistYTMusic(AllPlaylist=True, IDplaylist=None, Debug=modo_debug))
            else:
                raise UserWarning("Error en Youtube (main) If")    


        elif argvs[0] == "-sp" or argvs[0] == "-spotify": #Seccion Spotify
            servicio_predeterminado = True
            if argvs[1] == "-u" or argvs[1] == "-update":
                try:
                    if len(argvs) > 3:
                        raise ValueError("Error en Spotify (update) if")
                    else:
                        print(ActualizarDBSpotify(AllPlaylist=False, IDplaylist=argvs[2], Debug=modo_debug))
                except IndexError:
                    print(ActualizarDBSpotify(AllPlaylist=True, Debug=modo_debug))
            
            elif argvs[1] == "-s" or argvs[1] == "-sort":
                try:
                    try:
                        if len(argvs) > 4:
                            raise ValueError("Error en Spotify (sort) if")
                        elif argvs[3] == "--A2":
                            print(ActualizarOrdenPlaylistSpotify(AllPlaylist=False, IDplaylist=argvs[2], Algoritmo=True, Debug=modo_debug))
                        elif argvs[3] == "--A1":
                            print(ActualizarOrdenPlaylistSpotify(AllPlaylist=False, IDplaylist=argvs[2], Algoritmo=False, Debug=modo_debug))
                        else:
                            print("Error: Algoritmo de orden invalidado.")
                    except IndexError:
                        print(ActualizarOrdenPlaylistSpotify(AllPlaylist=False, IDplaylist=argvs[2], Debug=modo_debug))
                except IndexError:
                    print(ActualizarOrdenPlaylistSpotify(AllPlaylist=True, Debug=modo_debug))
            
            elif argvs[1] == "-r" or argvs[1] == "-review":
                try:
                    if len(argvs) > 3:
                            raise ValueError("Error en Spotify (review) if")
                    else:
                        print(ComprobarPlaylistSpotify(AllPlaylist=False, IDplaylist=argvs[2], Debug=modo_debug))
                except IndexError:
                    print(ComprobarPlaylistSpotify(AllPlaylist=True, Debug=modo_debug))
            
            else:
                raise UserWarning("Error en Spotify (main) If")    
        
        
        elif argvs[0] == "-cs" or argvs[0] == "-cross": #Seccion comparador
            try:
                CompararPlaylists(AllPlaylist = False, IDplaylist = sys.argv[2], Debug = modo_debug)
            except KeyboardInterrupt:
                CompararPlaylists(AllPlaylist = True, IDplaylist = None, Debug = modo_debug)
                
                
        elif argvs[0] == "--addexc" or argvs[0] == "--addExcept":
            with open(excepciones_path, "r") as a:
                datos:dict = json.load(a)
            
            with open(excepciones_path, "w") as f:
                if re.search(r"\s=\s", argvs[1]):
                    elementos = re.split(r"\s=\s", argvs[1])
                    
                    try:
                        loop = 0 
                        filtro = None
                        while True:
                            if len(elementos[0]) == 11:
                                track_sp = UsuarioSpotify(Debug=modo_debug).InfoTrack(elementos[1])
                                track_yt = UsuarioYoutubeMusic(Debug=modo_debug).InfoTrack(elementos[0], filtro)
                                
                            elif len(elementos[0]) == 22:
                                track_sp = UsuarioSpotify(Debug=modo_debug).InfoTrack(elementos[0])
                                track_yt = UsuarioYoutubeMusic(Debug=modo_debug).InfoTrack(elementos[1], filtro)
                            
                            else:
                                raise SpotifyException("404", "error", "Url Invalida")
                            
                            track_yt = AdministradorYTMusic.__ExcepcionTracks__(track = track_yt)
                            
                            track_sp = [ __limpiarTexto__(track_sp["name"]), [ artist["name"] for artist in track_sp["artists"] ] ]
                            
                            elementos = [ str(track_sp), str(track_yt) ]
                            
                            print(elementos, end="\n")
                            
                            user = input("yes / no [Y|n]: ").lower()
                            if user == "yes" or user == "y" or user == "":
                                break
                            else:
                                if loop == 0:
                                    filtro = "songs"
                                elif loop == 1:
                                    filtro == "videos"
                            
                            loop += 1
     
                    except SpotifyException:
                        pass
                    
                    try:
                        elementos = list(map(lambda x: eval(x), elementos)) 
                    except NameError:
                        print("\nCanciones estilo 'list' invalidos.\n")
                        exit()
                    
                    tagNameOne = __tagNameFormat__(elementos[0])
                    tagNameTwo = __tagNameFormat__(elementos[1])
                    
                    print(tagNameOne)
                    print(tagNameTwo)
               
                    datos["main"][tagNameOne] = elementos[1]
                    datos["main"][tagNameTwo] = elementos[0]
                    
                elif re.search(r"yt:\s?", argvs[1]) or re.search(r"sp:\s?", argvs[1]):
                    elementos = re.sub(r"yt:\s|sp:\s", "", argvs[1])
                    elementos = eval(elementos)
                    tagName = __tagNameFormat__(elementos)
                    
                    print(tagName)
                    
                    if re.search(r"yt:\s?", argvs[1]):
                        print("1")
                        datos["yt"][tagName] = elementos
                    else:
                        print("2")
                        datos["sp"][tagName] = elementos
                else:
                    raise UserWarning("Error en (--Excepciones) If")
                
                json.dump(datos, f, indent=2)
        
        
        elif argvs[0] == "--exp" or argvs[0] == "--export":
            if re.search(r"yt:\s?", argvs[1]) or re.search(r"sp:\s?", argvs[1]):
                data = re.sub(r"yt:\s?|sp:\s?", "", sys.argv[2])

                if re.search(r"yt:\s?", argvs[1]):
                    try:
                        track = UsuarioYoutubeMusic(Debug=modo_debug).InfoTrack(data, "songs")
                    except IndexError:
                        try:
                            track = UsuarioYoutubeMusic(Debug=modo_debug).InfoTrack(data, "videos")
                        except IndexError:
                            raise SpotifyException("404", "error", "Url Invalida")
                                        
                    if track["artists"][0]["id"] in canales_guardados:
                        track["artists"] = None
                    
                    name_song, artist_song = AdministradorYTMusic.__ExcepcionTracks__(track = track)
                    
                else:
                    track = UsuarioSpotify(Debug=modo_debug).InfoTrack(data)

                    name_song = __limpiarTexto__(track["name"])
                    artist_song = track["artists"]
                    artist_song = [ artist["name"] for artist in artist_song ]
                    
                print( [name_song, artist_song] ) #salida (return) con la info
            else:
                raise UserWarning("Error en (--Export) If")
        
        
        else:
            raise UserWarning("Error en main If")
    #(UserWarning, ValueError, SpotifyException)
    except KeyboardInterrupt as e:
        if type(e) == ValueError:
            print("Error: demasiados argumentos.")
        elif type(e) == SpotifyException:
            print("\nError: Url invalida.")
        else:
            print("Error: argumentos incorrectos.")
        if modo_debug:
            print("\nERROR:")
            print(e, end="\n")
    finally:
        TimeOu = time.time()  # tomar tiempo al momento de finalizar
        print(f"\nPrograma Finalizado en {(TimeOu-TimeIn):.2f} segundos.") # mostrar tiempo de ejecuccion del codigo.