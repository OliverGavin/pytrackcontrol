from collections import defaultdict
from functools import wraps


class EventEmitter:
    """Allows events to be triggered on attached handlers.
    """

    def __init__(self):
        self._event_handlers = defaultdict(list)

    @property
    def handler_events(self):
        """
        Returns
        -------
        set[str]
            event names which have attached handlers
        """
        return set(self._event_handlers)

    def on(self, event, callback=None):
        """Attaches an event handler which is fired on `event`.

        If no `callback` is supplied, decorator usage is assumed.

        >>> e = EventEmitter()

        >>> # Decorator usage
        >>> @e.on('img')
        >>> def img_handler(img):
        >>>     # do something with the image

        >>> # Alternatively
        >>> e.on('img', img_handler)


        Parameters
        ----------
        event: str
            The name of the event to handle
        callback: Callable[[Any], None]
            The event handler which excepts an input, where the type is
            dependant on the provider, and returns None
        """

        def _on(callback):
            self._event_handlers[event].append(callback)
            self._on_change()

        if callback:
            # normal usage
            return _on(callback)
        else:
            # decorator usage
            def decorator(callback):
                @wraps(callback)
                def wrapper(value):
                    return callback(value)
                # wrapper will be the new function, ensures reference
                # to the callback when passed to off will be the same
                _on(wrapper)
                return wrapper
            return decorator

    def off(self, event, callback=None):
        """Removes an existing event handler or all event handlers.

        If no `callback` is supplied, all the handlers for `event` will
        be removed.

        Parameters
        ----------
        event: str
            The name of the event
        callback: Callable[[Any], None], optional
            The event handler to remove
        """
        if callback:
            self._event_handlers[event].remove(callback)
            # return if there are still handlers attached

        # otherwise delete the event
        if not callback or not self._event_handlers[event]:
            del self._event_handlers[event]

        self._on_change()

    def emit(self, event, value):
        """Triggers handlers attached to `event` with `value` as a parameter.

        Parameters
        ----------
        event: str
            The name of the event
        value: Any
            The value to supply as a parameter to the handlers
        """
        for handler in self._event_handlers[event]:
            handler(value)

    def _on_change(self):
        """Optional hook to be notified of a change
        """
        pass
