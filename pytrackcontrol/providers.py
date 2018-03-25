from pytrackvision.utils.fps import FPS
from pytrackvision.vision import FaceTracker


class FPSProvider:

    def __init__(self):
        self._fps = FPS(frame_buffer_size=10)

    def provide(self, resolve, img):
        self._fps.next()
        resolve(self._fps.fps)


class FaceBBoxProvider:

    def __init__(self):
        self._face_tracker = FaceTracker()

    def provide(self, resolve, img):
        bbox = self._face_tracker.track(img)
        if bbox:
            resolve(bbox)
