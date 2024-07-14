import sys
import time
import json
import sqlite3 as sql
from spotipy.exceptions import SpotifyException
from spotify import AdministradorSpotify, UsuarioSpotify

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
                            SqlOpcion(F"DELETE FROM '{playlist_nombre}'")
                            __addSongs__()
                            break
                else:
                    if Debug:
                        print("Escalas Desiguales, limpiando y actualizando...\n")
                    SqlOpcion(F"DELETE FROM '{playlist_nombre}'")
                    __addSongs__()
            else:
                if Debug:
                    print("Tabla inexistente\n")
                SqlOpcion(
                    F"CREATE TABLE '{playlist_nombre}' ('name song' TEXT, 'artist' TEXT, 'length' INT)")
                if Debug:
                    print("Tabla Creada, adding canciones...\n")
                __addSongs__()

    def __formatearNombrePlaylist__(nombre: str):
        nombre = nombre.lower()
        BLOQUEOS = """@"#$%&/()=?¡¨*[]{}+´:;-.,'"""
        listaNombre = []
        espacios = 0
        letras = 0
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

    if AllPlaylist:
        print("Actualizando playlists...")
        usuarioPlaylists = UsuarioSpotify().PLAYLIST_USUARIO
        for playlist in usuarioPlaylists:
            __actualizarDB__(playlist["id"])
        return "Playlists actualizadas."
    else:
        if IDplaylist == None:
            raise UserWarning("Url de Spotify.Playlist no definida")
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
                if playlist["id"] == excepcion_playlist_uno or playlist["id"] == excepcion_playlist_dos:
                    engine.OrdenarPlaylistAlgoritmo(Algoritmo=True)
                else:
                    engine.OrdenarPlaylistAlgoritmo(Algoritmo=False)
        return "Playlists ordenadas."
    else:
        print("Ordenando playlist...")
        engine = AdministradorSpotify(IDplaylist, Debug=Debug)
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
        engine = AdministradorSpotify(IDplaylist, Debug)
        return engine.ComprobarPlaylist()


if __name__ == "__main__":
    TimeIn = time.time()  # tomar tiempo al momento de inicio
    argvs = sys.argv[1:]
    
    with open("credenciales_API.json", "r") as f:
        excepcion = json.loads(f.read())
    
    with open("credenciales_API.json", "w") as f:
        modo_debug = excepcion["modo_debug"]
        if argvs[0] == "--debug" or argvs[0] == "--d":
            if excepcion["modo_debug"]: 
                excepcion["modo_debug"] = False
            else:
                excepcion["modo_debug"] = True  
            f.seek(0)
            f.write(json.dumps(excepcion, indent=2))
            print("Ajuste actualizado.")
            exit()

    
    excepcion_playlist_uno = excepcion["excepcion_playlist_uno"]
    excepcion_playlist_dos = excepcion["excepcion_playlist_dos"]
    spotify_path = excepcion["spotify_path"]
    youtube_path = excepcion["youtube_path"]
    
    try:
        if argvs[0] == "-h" or argvs[0] == "-help":
            print("""Documentacion...""")
        elif argvs[0] == "-yt" or argvs[0] == "-youtube":
            servicio_predeterminado = False
            print("[!] En Desarrollo...")

        elif argvs[0] == "-sp" or argvs[0] == "-spotify":
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
                            print(ActualizarOrdenPlaylistSpotify(AllPlaylist=False, IDplaylist=argvs[2], Debug=modo_debug))
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
                    ComprobarPlaylistSpotify(AllPlaylist=True, Debug=modo_debug)
            
            else:
                raise UserWarning("Error en Spotify (main) If")    
        else:
            raise UserWarning("Error en main If")
    except (UserWarning, IndexError, ValueError, SpotifyException) as e:
        if type(e) == ValueError:
            print("Error: demasiados argumentos.")
        elif type(e) == SpotifyException:
            print("\nError: Url invalida.")
        else:
            print("Error: argumentos incorrectos.")
        if modo_debug:
            print(e)
    finally:
        TimeOu = time.time()  # tomar tiempo al momento de finalizar
        print(f"\nPrograma Finalizado en {(TimeOu-TimeIn):.2f} segundos.") # mostrar tiempo de ejecuccion del codigo.