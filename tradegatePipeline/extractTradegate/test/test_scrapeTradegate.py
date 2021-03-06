from unittest import TestCase
from unittest.mock import Mock, MagicMock, patch

import sys
sys.modules['google.cloud.storage'] = MagicMock()
sys.modules['requests'] = MagicMock()

from scrapeTradegate import pubsubEntryPoint

class Stock:
    def __init__(self, isin):
        self.isin = isin

class Page:
    def __init__(self):
        self.text = "Html content"


@patch('builtins.print', Mock())
class testScrape(TestCase):
    def testMockRun(self):
        source = Mock()
        source.query.return_value = [Stock('US3434'), Stock('DE78322')]
        sqlSourcePatch = patch('scrapeTradegate.StdSource', return_value=source)
        rqPatch = patch('scrapeTradegate.rq.get', return_value=Page())
        #source.query().limit().return_value = ['US3434', 'DE78322']
        strIO = patch('gcp.Storage.StringIO', Mock)
        with sqlSourcePatch, strIO, rqPatch:
            pubsubEntryPoint(None, None)

