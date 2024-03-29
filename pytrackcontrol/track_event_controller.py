from pytrackcontrol.event import EventController
from pytrackvision.utils.camera_stream import get_camera_stream


class TrackEventController(EventController):

    def __init__(self, src=None, **kwargs):
        """
        """
        EventController.__init__(self, root_event_label='src', **kwargs)
        self._src = src

    @property
    def _context(self):
        return get_camera_stream(multi_thread=True, framerate=30, src=self._src)
