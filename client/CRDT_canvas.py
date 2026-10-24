import cv2
import numpy as np

WIDTH_PIX = 228
HEIGHT_PIX = 80


class CRDT_Canvas:
    def __init__(self) -> None:
        self.data = np.array = np.full(
            shape=(HEIGHT_PIX, WIDTH_PIX, 3), fill_value=(255,255,255), dtype=np.uint8
        )
        self.events: list[tuple[int]] = []

    # event : (x1,y1,x2,y2, 0/1)

    def get_canvas(self):
        return self.data

    def update_draw(self, x1, y1, x2, y2):
        # A single line draw update
        self.merge((x1, y1, x2, y2, 1))

    def update_erase(self, x1, y1, x2, y2):
        # A single delete draw update
        self.merge((x1, y1, x2, y2, 0))

    def merge(self, event):
        # Applies an event to OUR Canvas

        self.data = cv2.line(
            self.data,
            event[:2],
            event[2:4],
            (0, 0, 0) if event[4] == 1 else (255, 255, 255),
            1 if event[4] == 1 else 5,
        )

        print(event[4])
        # Add event to 'events'
        self.events.append(event)
