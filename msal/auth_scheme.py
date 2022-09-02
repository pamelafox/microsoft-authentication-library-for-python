try:
    from urllib.parse import urlparse
except ImportError:  # Fall back to Python 2
    from urlparse import urlparse

# We may support more auth schemes in the future
class PopAuthScheme(object):
    # Internal design: https://identitydivision.visualstudio.com/DevEx/_git/AuthLibrariesApiReview?path=/PoPTokensProtocol/PopTokensProtocol.md
    def __init__(self, http_method=None, url=None, nonce=None):
        """Create an auth scheme which is needed to obtain a Proof-of-Possession token.

        :param str http_method:
            Its value is an uppercase http verb, such as "GET" and "POST".
        :param str url:
            The url to be signed.
        :param str nonce:
            The nonce came from resource's challenge.
        """
        if not (http_method and url and nonce):
            # In the future, we may also support accepting an http_response as input
            raise ValueError("All http_method, url and nonce are required parameters")
        if http_method.upper() != http_method:
            raise ValueError("http_method must be uppercase, according to "
                "https://datatracker.ietf.org/doc/html/draft-ietf-oauth-signed-http-request-03#section-3")
        self._http_method = http_method
        self._url = urlparse(url)
        self._nonce = nonce

