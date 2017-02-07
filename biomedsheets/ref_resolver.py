# -*- coding: utf-8 -*-
"""Code for resolving references in JSON code"""

import os
from urllib.parse import urlparse
import sys

import jsonpath_rw
import requests
from requests.exceptions import HTTPError
import requests_file

try:
    import ruamel.yaml as yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

from . import requests_resource

__author__ = 'Manuel Holtgrewe <manuel.holtgrewe@bihealth.de>'


class RefResolutionException(Exception):
    """Raised on problems with resolving JSON pointers"""


class RefResolver:
    """Helper class for resolving JSON pointers in "$ref" properties

    The resolver will perform on inline updates but rather create new
    dicts and lists with copies.
    """

    def __init__(self, lookup_paths=None, dict_class=dict, verbose=False):
        self.cache = {}
        self.dict_class = dict_class
        self.lookup_paths = list(lookup_paths or [])
        self.session = requests.Session()
        self.session.mount('file://', requests_file.FileAdapter())
        self.session.mount('resource://', requests_resource.ResourceAdapter())
        #: whether or not to resolve relative paths using cwd
        self.rel_cwd_paths = True
        self.verbose = verbose  # TODO: use logging instead

    def resolve(self, doc_uri, obj):
        """Entry point for resolving JSON pointers

        doc_uri is the URI of the JSON document in obj.

        obj can either be a dict or list object (possibly of a sub class)

        raises RefResolutionError on problems with the resolution
        """
        self.cache = {doc_uri: obj}
        return self._resolve(doc_uri, obj, obj)

    def _resolve(self, doc_uri, main_doc, obj):
        if isinstance(obj, (int, bool, float, str)):  # JSON atomic
            return obj
        elif isinstance(obj, dict):  # JSON object
            return self._resolve_dict_entry(doc_uri, main_doc, obj)
        elif isinstance(obj, list):  # JSON list
            return [self._resolve(doc_uri, main_doc, elem) for elem in obj]
        else:
            raise RefResolutionException(
                'Can only resolve in dict and list container objects and '
                'the atomic types int, bool, foat, and str.')

    def _resolve_dict_entry(self, doc_uri, main_doc, obj):
        """Implementation of a dict objects"""
        # Interpret '$ref' key if present in obj
        if '$ref' in obj:
            result = self._load_ref(doc_uri, main_doc, obj['$ref'])
        else:
            result = self.dict_class()
        # Merge values from obj with result
        for k, v in obj.items():
            if k != '$ref':
                result[k] = self._resolve(doc_uri, main_doc, v)
        return result

    def _load_ref(self, doc_uri, doc, ref_uri):
        """Resolve "$ref" URI ``uri``"""
        if self.verbose:
            print('Resolving $ref URI {}'.format(ref_uri), file=sys.stderr)
        parsed_ref_uri = self._parse_ref_uri(ref_uri)
        ref_file = parsed_ref_uri.netloc + parsed_ref_uri.path
        if not ref_file:  # must be relative to current doc
            pass  # is already in cache
        elif ref_file not in self.cache:
            self.cache[ref_uri] = self._load_for_cache(
                doc_uri, doc, parsed_ref_uri)
        ref_json = self.cache[ref_uri]
        expr = jsonpath_rw.parse(
            '$' + '.'.join(parsed_ref_uri.fragment.split('/')))
        for match in expr.find(ref_json):
            return match.value  # return first match only
        # If we reach here, resolution failed
        raise RefResolutionException(
            'Could not resolve reference URI "{}"'.format(ref_uri))

    def _parse_ref_uri(self, ref_uri):
        parsed_ref_uri = urlparse(ref_uri)
        if (self.rel_cwd_paths and parsed_ref_uri.scheme == 'file' and
                parsed_ref_uri.netloc):
            for path in self.lookup_paths:
                tmp = ref_uri[:(len('file://'))]
                abspath = os.path.join(
                    os.path.abspath(path), parsed_ref_uri.netloc)
                if os.path.exists(abspath):
                    tmp += abspath
                    tmp += ref_uri[len('file://' + parsed_ref_uri.netloc):]
                    return urlparse(tmp)
            else:
                raise RefResolutionException(
                    'Could not find local file {}'.format(
                        parsed_ref_uri.netloc))
        else:
            return parsed_ref_uri

    def _load_for_cache(self, doc_uri, doc, parsed_uri):
        """Load fragment from file URI without cache"""
        remote_uri = '{}://{}/{}'.format(
            parsed_uri.scheme, parsed_uri.netloc, parsed_uri.path)
        if self.verbose:
            print('Loading URI {}'.format(remote_uri), file=sys.stderr)
        response = self.session.get(remote_uri)
        try:
            response.raise_for_status()
        except HTTPError as e:
            raise RefResolutionException(
                'Could not load file {}'.format(parsed_uri.geturl()))
        remote_json = self._load_json(response)
        return remote_json

    def _load_json(self, response):
        if YAML_AVAILABLE:
            return yaml.round_trip_load(response.text)
        else:
            return response.json(object_pairs_hook=self.dict_class)
