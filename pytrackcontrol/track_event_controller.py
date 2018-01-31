from abc import ABC, abstractmethod
from collections import defaultdict
from functools import partial

from pytrackvision.utils.camera_stream import get_camera_stream

from pytrackcontrol.graph import Dag

# Maybe seperate the controller (loop) from the emitter?


class EventController(ABC):

    def __init__(self, lazy_validation=True):
        self._lazy_validation = lazy_validation
        self._dag = Dag(root=self._root_event_label)
        self._event_handlers = defaultdict(list)
        self._event_providers = {}
        self._event_sequence = []

    def start(self):
        """Start iterating.

        Emitted events in the registered functions will trigger the event callbacks.
        """
        if self._lazy_validation:
            self._refresh_event_sequence()

        try:
            with self._context as ctx:
                self._iterate(ctx)
        except AttributeError:
            self._iterate(self._context)

    def _iterate(self, iterable):
        for item in iterable:
            self._dispatch(item)

    def _dispatch(self, value):
        """Dispatch the initial value to the registered handling functions.

        Resolves dependencies on outputs from other handlers and dispatches
        to them when the dependency has been met.
        """
        outputs = {}

        def resolver(event, value):
            outputs[event] = value
            self.emit(event, value)

        resolver(self._root_event_label, value)
        print('##################################here')

        for event in self._event_sequence[1:]:
            print('####', event)
            provider = self._event_providers[event]

            inputs = {dep: outputs[dep] for dep in provider.dependencies}
            provider.function(partial(resolver, event), **inputs)

    def _refresh_event_sequence(self):
        self._event_sequence = self._dag.topological_sort()

    def _get_active_handler_events(self):
        return set([event for event, handlers in self._event_handlers.items() if handlers])

    def _get_required_provider_events(self):
        handler_events = self._get_active_handler_events()

        def get_providers(events):
            providers = {e: p for e, p in self._event_providers.items() if e in events}
            dependency_events = set([d for p in providers.values() for d in p.dependencies])

            if not dependency_events:
                return set()

            return events & get_providers(dependency_events)

        return get_providers(handler_events)

    @property
    @abstractmethod
    def _context(self):
        """Hook which returns an appropriate iterable through an optional context manager
        for use in the main event loop.

        Returns
        ----------
        ContextManager[Iterable] or Iterable
            a context manager which returns and iterable
        """
        pass

    @property
    @abstractmethod
    def _root_event_label(self):
        """Hook which returns a label/name for the root event.

        Returns
        ----------
        str
            a label/name for the root event
        """
        pass

    def on(self, event, callback=None):  # decorate callback
        """
        """
        def _on(callback):
            self._event_handlers[event].append(callback)

        if callback:
            # decorator usage
            return _on(callback)
        else:
            # normal usage
            return _on

    def off(self, event, callback=None):
        """
        """
        if callback:
            self._event_handlers[event].remove(callback)
        else:
            del self._event_handlers[event]

    def emit(self, event, value):
        """
        """
        for handler in self._event_handlers[event]:
            handler(value)

    def register(self, event, fn, dep=None):  # decorate fn
        """

        Parameters
        ----------


        Raises
        ------
        ValueError:
            if cyclic dependencies are introduced
        """
        if event in self._event_providers:
            raise ValueError(f"A provider is already registered for this event ({event}).")

        if not dep:
            dep = self._root_event_label

        if isinstance(dep, str):
            dep = [dep]

        self._event_providers[event] = {
            'function': fn,
            'dependencies': dep
        }

        for d in dep:
            self._dag.add_edge(d, event)

        if not self._lazy_validation:
            self._refresh_event_sequence()


class TrackEventController(EventController):

    def __init__(self, **kwargs):  # pass in some camera config object??
        """
        """
        # super(self, kwargs)
        pass # self register some predefined functions?

    @property
    def _context(self):
        return get_camera_stream(multi_thread=True, framerate=30)

    @property
    def _root_event_label(self):
        return 'img'
