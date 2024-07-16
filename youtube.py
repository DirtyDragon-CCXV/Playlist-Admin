import json
import requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


class AdministradorYoutube():
    def __init__(self, playlist_ID: str = None, modo_debug: bool = False) -> None:
        self.modo_debug = modo_debug
        self.PLAYLIST_ID = playlist_ID

        # comprueba si el archivo con el token existe, si genera el token y lo guarda
        try:
            with open('token.json', 'r') as archivo:
                datos = json.load(archivo)
                self.CREDENCIAL = Credentials(token=datos['token'])
                self.API_KEY = datos["api_key"]
                self.SCOPES = datos["scopes"]

            if not self.CREDENCIAL.valid:
                self.__ObtenerToken__()

        except FileNotFoundError:
            self.__ObtenerToken__()

    def __ObtenerToken__(self) -> str:
        """Generar un nuevo token y guardarlo en un archivo Json"""
        flow = InstalledAppFlow.from_client_secrets_file('youtube_credenciales.json', self.SCOPES)
        credentials = flow.run_local_server()

        token = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
        }

        with open('token.json', 'w') as f:
            f.write(json.dump(token, indent = 2))

        return "token obtenido"

    def __ConsultaAPI__(self) -> requests.Response | json.JSONDecoder:
        """Realiza una consulta a la API con el token de Oauth2.0 y devuelve el contenido en un diccionario

        Returns:
            requests.Response | json.JSONDecoder: Devuelve el contenido de la peticion 'request.Response' y convierte el Json en diccionario.
        """
        response = requests.get(f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId={self.PLAYLIST_ID}&maxResults=50", headers={'Authorization': f'Bearer {self.CREDENCIAL.token}'})
        if self.modo_debug:
            print(f"Status request: {response.status_code}")
        return json.loads(response.text)

yt = AdministradorYoutube(playlist_ID='PLMl1Y5tQ5mHl5RNgU8NxVw20Xpr7J-Pj9').__ConsultaAPI__()

for i in yt["items"]:
    print(i["snippet"]["title"])
