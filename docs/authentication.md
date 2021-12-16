### Auth Class

For authentication you can use the package Auth class, first create an instance of it:

```python
from ctrader_open_api import Auth

auth = Auth("Your App ID", "Your App Secret", "Your App redirect URI")
```

### Auth URI

The first step for authentication is sending user to the cTrader Open API authentication web page, there the user will give access to your API application to manage the user trading accounts on behalf of him.

To get the cTrader Open API authentication web page URL you can use the Auth class getAuthUri method:

```python
authUri = auth.getAuthUri()
```
The getAuthUri has two optional parameters:

* scope: Allows you to set the scope of authentication, the default value is trading which means you will have full access to user trading accounts, if you want to just have access to user trading account data then use accounts

* baseUri: The base URI for authentication, the default value is EndPoints.AUTH_URI which is https://connect.spotware.com/apps/auth

### Getting Token

After user authenticated your Application he will be redirected to your provided redirect URI with an authentication code appended at the end of your redirect URI:

```
https://redirect-uri.com/?code={authorization-code-will-be-here}
```

You can use this authentication code to get an access token from API, for that you can use the Auth class getToken method:

```python
# This method uses EndPoints.TOKEN_URI as a base URI to get token
# you can change it by passing another URI via optional baseUri parameter
token = auth.getToken("auth_code")
```

Pass the received auth code to getToken method and it will give you a token JSON object, the object will have these properties:

* accessToken: This is the access token that you will use for authentication

* refreshToken: This is the token that you will use for refreshing the accessToken onces it expired

* expiresIn: The expiry of token in seconds from the time it generated

* tokenType: The type of token, standard OAuth token type parameter (bearer)

* errorCode: This will have the error code if something went wrong

* description: The error description

### Refreshing Token

API access tokens have an expiry time, you can only use it until that time and once it expired you have to refresh it by using the refresh token you received previously.

To refresh an access token you can use the Auth class refreshToken method:

```python
# This method uses EndPoints.TOKEN_URI as a base URI to refresh token
# you can change it by passing another URI via optional baseUri parameter
newToken = auth.refreshToken("refresh_Token")
```

You have to pass the refresh token to "refreshToken" method, and it will return a new token JSON object which will have all the previously mentioned token properties.

You can always refresh a token, even before it expires and the refresh token has no expiry, but you can only use it once.
