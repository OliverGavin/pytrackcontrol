from abc import ABC, abstractmethod
from functools import wraps, partial
from contextlib import contextmanager

from pytrackcontrol.event import EventEmitter
from pytrackcontrol.graph import Dag


class EventController(ABC, EventEmitter):

    def __init__(self, root_event_label):
        """

        Parameters
        ----------
        root_event_label: str
            The name of the root/source event produced in the main loop
        """
        EventEmitter.__init__(self)
        self._root_event_label = root_event_label
        self._running = False
        self._dag = Dag(root=self._root_event_label)
        self._event_providers = {}
        self._provider_event_sequence = []
        self._event_sequence = []

    def start(self):
        """Start the main loop.

        Emitted events in the registered providers will trigger the event
        handler callbacks.
        """
        @contextmanager
        def running():
            self._running = True
            try:
                yield
            finally:
                self._running = False

        with running():
            self._refresh_providers()

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

        for event in self._event_sequence[1:]:
            provider = self._event_providers[event]

            inputs = [outputs[dep] for dep in provider['dependencies']]
            provider['function'](partial(resolver, event), *inputs)

    def _refresh_handlers(self):  # TODO thread safety
        """
        When a handler is added or removed, dependencies on providers may be
        added or removed too. We need only execute providers (and their
        dependencies) that are needed by handlers.
        Refreshes the event sequence.
        """
        handler_events = self.handler_events

        def get_dependencies(events):
            dependency_events = set([
                d
                for e, p in self._event_providers.items()
                for d in p['dependencies']
                if e in events
            ])

            if not dependency_events:
                return events

            return events | get_dependencies(dependency_events)

        dependencies = get_dependencies(handler_events)
        self._event_sequence = [e for e in self._provider_event_sequence
                                if e in dependencies]

    def _refresh_providers(self):  # TODO thread safety
        """
        When a provider is added, cycles may be introduced or dependencies may
        need to be reolved in order to execute in the correct order.
        Updates the DAG and refreshes the event sequence.
        """
        self._provider_event_sequence = self._dag.topological_sort()
        self._refresh_handlers()

    def _on_change(self):
        if self._running:
            self._refresh_handlers()

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

    def register(self, event, fn=None, dep=None):
        """

        Parameters
        ----------
        event: str
            The event name
        fn: Callable[[Callable[[Any], None], Any], None]
            A function whose first parameter is a resolve(value) function for
            broadcasting a result. The function accepts at least one more
            parameter which is/are the values of the specified dependencies.
        dep: str or list[str]
            The dependencies that must be resolved beforehand and be supplied
            to `fn`.

        Raises
        ------
        ValueError:
            if cyclic dependencies are introduced
        """

        def _register(fn, dep):
            if event in self._event_providers:
                raise ValueError(f"A provider is already registered for"
                                 "this event ({event}).")

            if not dep:
                dep = self._root_event_label

            if isinstance(dep, str):
                dep = [dep]

            for d in dep:
                if d != self._root_event_label and \
                   d not in self._event_providers.keys():
                    raise ValueError(f"dependency '{d}' does not exist.")

            self._event_providers[event] = {
                'function': fn,
                'dependencies': dep
            }

            for d in dep:
                self._dag.add_edge(d, event)

            if self._running:
                self._refresh_providers()

        if fn:
            # normal usage
            return _register(fn)
        else:
            # decorator usage
            def decorator(fn):
                @wraps(fn)
                def wrapper(resolve, *values):
                    return fn(resolve, *values)
                # wrapper will be the new function, ensures reference
                # to the fn when passed to off will be the same
                _register(wrapper, dep)
                return wrapper
            return decorator
