from pytrackcontrol.event import EventController
from pytrackvision.utils.camera_stream import get_camera_stream


class TrackEventController(EventController):

    def __init__(self, **kwargs):  # pass in some camera config object??
        """
        """
        EventController.__init__(self, root_event_label='img', **kwargs)
        pass  # self register some predefined functions?

    @property
    def _context(self):
        return get_camera_stream(multi_thread=True, framerate=30)
