from unittest import TestCase
from unittest.mock import patch, Mock, PropertyMock

from pytrackcontrol.event import EventController


class TestEventController(TestCase):

    @patch.multiple(EventController,
                    __abstractmethods__=set(),
                    _context=PropertyMock(return_value='testing...'))
    def test_context_property_mock(self):
        self.assertTrue(EventController('root')._context == 'testing...')

    @patch.multiple(EventController,
                    __abstractmethods__=set(),
                    _context=PropertyMock(return_value=[1, 2, 3]))
    @patch.object(EventController, '_dispatch', autospec=True)
    def test_start_dispatches_3_times(self, mock):
        EventController('root').start()
        self.assertEqual(mock.call_count, 3)

    @patch.multiple(EventController,
                    __abstractmethods__=set(),
                    _context=PropertyMock(return_value=[1, 2, 3]))
    def test_event_handler(self):
        outputs = []
        e = EventController('root')

        @e.on('root')
        def root_handler(num):
            outputs.append(num)

        e.start()
        self.assertEqual(outputs, [1, 2, 3])

    @patch.multiple(EventController,
                    __abstractmethods__=set(),
                    _context=PropertyMock(return_value=[1, 2, 3]))
    def test_multiple_event_handler_on(self):
        outputs = []
        e = EventController('root')

        @e.on('root')
        def root_double(num):
            outputs.append(num * 2)

        @e.on('root')
        def root_triple(num):
            outputs.append(num * 3)

        e.start()
        self.assertEqual(outputs, [2, 3, 4, 6, 6, 9])

    @patch.multiple(EventController,
                    __abstractmethods__=set(),
                    _context=PropertyMock(return_value=[1, 2, 3]))
    def test_multiple_event_handler_off(self):
        outputs = []
        e = EventController('root')

        @e.on('root')
        def root_double(num):
            outputs.append(num * 2)

        @e.on('root')
        def root_triple(num):
            outputs.append(num * 3)

        e.off('root', root_triple)

        e.start()
        self.assertEqual(outputs, [2, 4, 6])

    @patch.multiple(EventController,
                    __abstractmethods__=set(),
                    _context=PropertyMock(return_value=[1, 2, 3]))
    def test_register_with_handler(self):
        inputs = []
        e = EventController('numbers')

        @e.register('squared')
        def squared(resolve, num):
            result = num ** 2
            resolve(result)

        @e.on('squared')
        def squared_handler(num):
            inputs.append(num)

        e.start()
        self.assertEqual(inputs, [1, 4, 9])

    @patch.multiple(EventController,
                    __abstractmethods__=set(),
                    _context=PropertyMock(return_value=[1, 2, 3]))
    def test_register_with_dependencies_with_handler(self):
        inputs = []
        e = EventController('numbers')

        @e.register('squared', dep='numbers')
        def squared(resolve, num):
            result = num ** 2
            resolve(result)

        @e.on('squared')
        def squared_handler(num):
            inputs.append(num)

        e.start()
        self.assertEqual(inputs, [1, 4, 9])

    @patch.multiple(EventController,
                    __abstractmethods__=set(),
                    _context=PropertyMock(return_value=[1, 2, 3]))
    def test_register_multiple_with_handler(self):
        squared_inputs = []
        cubed_inputs = []
        e = EventController('numbers')

        @e.register('squared', dep='numbers')
        def squared(resolve, num):
            result = num ** 2
            resolve(result)

        @e.on('squared')
        def squared_handler(num):
            squared_inputs.append(num)

        @e.register('cubed', dep='numbers')
        def cubed(resolve, num):
            result = num ** 3
            resolve(result)

        @e.on('cubed')
        def cubed_handler(num):
            cubed_inputs.append(num)

        e.start()
        self.assertEqual(squared_inputs, [1, 4, 9])
        self.assertEqual(cubed_inputs, [1, 8, 27])

    @patch.multiple(EventController,
                    __abstractmethods__=set(),
                    _context=PropertyMock(return_value=[1, 2, 3]))
    def test_register_multiple_with_dependencies_with_handler(self):
        inputs = []
        e = EventController('numbers')

        @e.register('squared', dep='numbers')
        def squared(resolve, num):
            result = num ** 2
            resolve(result)

        @e.register('fourth_power', dep=['numbers', 'squared'])
        def fourth_power(resolve, num, sqrd):
            result = sqrd * num ** 2
            resolve(result)

        @e.on('fourth_power')
        def fourth_power_handler(num):
            inputs.append(num)

        e.start()
        self.assertEqual(inputs, [1, 16, 81])

    @patch.multiple(EventController,
                    __abstractmethods__=set(),
                    _context=PropertyMock(return_value=[1, 2, 3]))
    def test_register_multiple_with_dependencies_without_handlers(self):
        from collections import defaultdict
        called = defaultdict(lambda: 0)
        e = EventController('img')

        @e.register('cats')
        def cat_finder(resolve, img):
            called['cats'] += 1
            resolve(img)

        @e.register('grumpycats', dep='cats')
        def grumpy_cat_finder(resolve, cat_img):
            called['grumpycats'] += 1
            resolve(cat_img)

        @e.register('browngrumpycats', dep='grumpycats')
        def brown_grumpy_cat_finder(resolve, cat_img):
            called['browngrumpycats'] += 1
            resolve(cat_img)

        e.start()
        self.assertEqual(sum(called.values()), 0)

    @patch.multiple(EventController,
                    __abstractmethods__=set(),
                    _context=PropertyMock(return_value=[1, 2, 3]))
    def test_register_multiple_with_dependencies_with_one_handlers(self):
        from collections import defaultdict
        called = defaultdict(lambda: 0)
        e = EventController('img')

        @e.register('cats')
        def cat_finder(resolve, img):
            called['cats'] += 1
            resolve(img)

        @e.register('tigercats', dep='cats')
        def tiger_cat_finder(resolve, cat_img):
            called['tigercats'] += 1
            resolve(cat_img)

        @e.on('tigercats')
        def tiger_cat_handler(cat_img):
            pass

        @e.register('grumpycats', dep='cats')
        def grumpy_cat_finder(resolve, cat_img):
            called['grumpycats'] += 1
            resolve(cat_img)

        @e.register('browngrumpycats', dep='grumpycats')
        def brown_grumpy_cat_finder(resolve, cat_img):
            called['browngrumpycats'] += 1
            resolve(cat_img)

        e.start()
        self.assertEqual(called['cats'], 3)
        self.assertEqual(called['tigercats'], 3)
        self.assertEqual(called['grumpycats'], 0)
        self.assertEqual(called['browngrumpycats'], 0)

    @patch.multiple(EventController,
                    __abstractmethods__=set(),
                    _context=PropertyMock(return_value=[1, 2, 3]))
    def test_register_without_handler(self):
        outputs = []
        e = EventController('numbers')

        @e.register('squared')
        def squared(resolve, num):
            outputs.append(num ** 2)

        e.start()
        self.assertEqual(outputs, [])

    @patch.multiple(EventController,
                    __abstractmethods__=set(),
                    _context=PropertyMock(return_value=[1, 2, 3]))
    def test_register_with_dependencies_without_handler(self):
        outputs = []
        e = EventController('numbers')

        @e.register('squared', dep='numbers')
        def squared(resolve, num):
            outputs.append(num ** 2)

        e.start()
        self.assertEqual(outputs, [])

    @patch.multiple(EventController,
                    __abstractmethods__=set(),
                    _context=PropertyMock(return_value=[1, 2, 3]))
    def test_register_with_missing_dependencies(self):
        e = EventController('root')

        with self.assertRaises(ValueError):
            @e.register('a', dep=['root', 'b'])
            def a(resolve, num):
                pass
