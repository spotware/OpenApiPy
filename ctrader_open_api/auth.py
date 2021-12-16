from ctrader_open_api.endpoints import EndPoints
import requests

class Auth:
    def __init__(self, appClientId, appClientSecret, redirectUri):
        self.appClientId = appClientId
        self.appClientSecret = appClientSecret
        self.redirectUri = redirectUri
    def getAuthUri(self, scope = "trading", baseUri = EndPoints.AUTH_URI):
        return f"{baseUri}?client_id={self.appClientId}&redirect_uri={self.redirectUri}&scope={scope}"
    def getToken(self, authCode, baseUri = EndPoints.TOKEN_URI):
        request = requests.get(baseUri, params=
                               {"grant_type": "authorization_code",
                               "code": authCode,
                              "redirect_uri": self.redirectUri,
                             "client_id": self.appClientId,
                            "client_secret": self.appClientSecret})
        return request.json()
    def refreshToken(self, refreshToken, baseUri = EndPoints.TOKEN_URI):
        request = requests.get(baseUri, params=
                               {"grant_type": "refresh_token",
                               "refresh_token": refreshToken,
                             "client_id": self.appClientId,
                            "client_secret": self.appClientSecret})
        return request.json()
