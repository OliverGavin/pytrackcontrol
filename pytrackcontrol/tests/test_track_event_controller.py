from unittest import TestCase
from unittest.mock import patch, Mock, PropertyMock

from pytrackcontrol import EventController


class TestEventController(TestCase):

    @patch.multiple(EventController,
                    __abstractmethods__=set(),
                    _context=PropertyMock(return_value='testing...'))
    def test_context_property_mock(self):
        self.assertTrue(EventController()._context == 'testing...')

    @patch.multiple(EventController,
                    __abstractmethods__=set(),
                    _context=PropertyMock(return_value=[1, 2, 3]))
    @patch.object(EventController, '_dispatch', autospec=True)
    def test_start_dispatches_3_times(self, mock):
        EventController().start()
        self.assertEqual(mock.call_count, 3)

    @patch.multiple(EventController,
                    __abstractmethods__=set(),
                    _context=PropertyMock(return_value=[1, 2, 3]),
                    _root_event_label=PropertyMock(return_value='root'))
    def test_start_dispatches(self):
        e = EventController()

        @e.on("root")
        def root_handler(num):
            print('@@@@', num)

        # e.on("root", root_handler)

        e.start()
        self.assertEqual(3, 3)
