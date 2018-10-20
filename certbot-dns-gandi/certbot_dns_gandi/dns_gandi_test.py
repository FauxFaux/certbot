"""Tests for certbot_dns_gandi.dns_gandi."""

import os
import unittest

import mock
from requests.exceptions import HTTPError

from certbot.plugins import dns_test_common
from certbot.plugins import dns_test_common_lexicon
from certbot.plugins.dns_test_common import DOMAIN
from certbot.tests import util as test_util

API_PROTOCOL_REST = 'rest'
API_PROTOCOL_RPC = 'rpc'
TOKEN = 'MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAw'


class AuthenticatorTest(test_util.TempDirTestCase,
                        dns_test_common_lexicon.BaseLexiconAuthenticatorTest):

    def setUp(self):
        super(AuthenticatorTest, self).setUp()

        from certbot_dns_gandi.dns_gandi import Authenticator

        path = os.path.join(self.tempdir, 'file.ini')
        credentials = {
            "gandi_api_protocol": API_PROTOCOL_REST,
            "gandi_token": TOKEN,
        }
        dns_test_common.write(credentials, path)

        self.config = mock.MagicMock(gandi_credentials=path,
                                     gandi_propagation_seconds=0)  # don't wait during tests

        self.auth = Authenticator(self.config, "gandi")

        self.mock_client = mock.MagicMock()
        # _get_gandi_client | pylint: disable=protected-access
        self.auth._get_gandi_client = mock.MagicMock(return_value=self.mock_client)


class GandiLexiconClientRpcTest(unittest.TestCase, dns_test_common_lexicon.BaseLexiconClientTest):
    DOMAIN_NOT_FOUND = Exception(
        "Failed to authenticate: '<Fault 510042: \"Error on object : "
        "OBJECT_DOMAIN (CAUSE_NOTFOUND) [Domain '{0}' doesn't exist.]\">'".format(DOMAIN))
    LOGIN_ERROR = Exception(
        "Failed to authenticate: '<Fault 510150: 'Error on object : "
        "OBJECT_ACCOUNT (CAUSE_NORIGHT) [Invalid API key]'>'")

    def setUp(self):
        from certbot_dns_gandi.dns_gandi import _GandiLexiconClient

        self.client = _GandiLexiconClient(API_PROTOCOL_RPC, TOKEN, DOMAIN, 0)

        self.provider_mock = mock.MagicMock()
        self.client.provider = self.provider_mock


class GandiLexiconClientRestTest(unittest.TestCase, dns_test_common_lexicon.BaseLexiconClientTest):
    DOMAIN_NOT_FOUND = HTTPError('404 Client Error: Not Found for url: {0}.'.format(DOMAIN))
    LOGIN_ERROR = HTTPError('401 Client Error: Unauthorized for url: {0}.'.format(DOMAIN))

    def setUp(self):
        from certbot_dns_gandi.dns_gandi import _GandiLexiconClient

        self.client = _GandiLexiconClient(API_PROTOCOL_REST, TOKEN, DOMAIN, 0)

        self.provider_mock = mock.MagicMock()
        self.client.provider = self.provider_mock


if __name__ == "__main__":
    unittest.main()  # pragma: no cover
