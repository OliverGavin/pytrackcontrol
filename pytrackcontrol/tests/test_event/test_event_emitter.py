from unittest import TestCase
from unittest.mock import patch, Mock, PropertyMock

from pytrackcontrol.event import EventEmitter


class TestEventEmitter(TestCase):

    def test_multiple_event_handler_emit(self):
        outputs = []
        e = EventEmitter()

        @e.on('event')
        def double_handler(num):
            outputs.append(num * 2)

        @e.on('event')
        def triple_handler(num):
            outputs.append(num * 3)

        e.emit('event', 1)
        self.assertEqual(outputs, [2, 3])
        e.emit('event', 2)
        self.assertEqual(outputs, [2, 3, 4, 6])
        e.emit('event', 3)
        self.assertEqual(outputs, [2, 3, 4, 6, 6, 9])
