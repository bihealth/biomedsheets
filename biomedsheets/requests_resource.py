# -*- coding: utf-8 -*-
"""Extensions for requests module"""

import io
import locale

import importlib_resources
from requests import Response, codes
from requests.adapters import BaseAdapter
from requests.compat import urlparse


class ResourceAdapter(BaseAdapter):
    """Adapter to importlib_resources replacement for pkg_resources.resource_stream()"""

    def send(self, request, **kwargs):
        """Wraps a pkg_resource.resource_stream

        The host name is interpreted as the package name
        """
        # Check that the method makes sense. Only support GET
        if request.method not in ("GET", "HEAD"):
            raise ValueError("Invalid request method {}".format(request.method))
        # Parse the URL
        url_parts = urlparse(request.url)

        # Interpret host name as package name
        if not url_parts.netloc:
            raise ValueError("pkg_resource: hostname interpreted as package name")
        pkg_name = url_parts.netloc

        resp = Response()

        # Open the resource stream, translate certain errors into HTTP
        # responses. Use urllib's unquote to translate percent escapes into
        # whatever they actually need to be
        try:
            url_path = url_parts.path
            while url_path.startswith("/"):
                url_path = url_path[1:]
            ref = importlib_resources.files(pkg_name).joinpath(url_path)
            with ref.open("rb") as inputf:
                resp.raw = io.BytesIO(inputf.read())
        except FileNotFoundError as e:
            resp.status_code = codes.not_found

            # Wrap the error message in a file-like object
            # The error message will be localized, try to convert the string
            # representation of the exception into a byte stream
            resp_str = str(e).encode(locale.getpreferredencoding(False))
            resp.raw = io.BytesIO(resp_str)
            resp.headers["Content-Length"] = len(resp_str)

            # Add release_conn to the BytesIO object
            resp.raw.release_conn = resp.raw.close
        else:
            resp.status_code = codes.ok

        return resp

    def close(self):
        pass
