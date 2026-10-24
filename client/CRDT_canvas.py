import cv2
import numpy as np

WIDTH_PIX = 250
HEIGHT_PIX = 90


class CRDT_Canvas:
    def __init__(self) -> None:
        self.data = np.array = np.full(
            shape=(HEIGHT_PIX, WIDTH_PIX, 3), fill_value=(255,255,255), dtype=np.uint8
        )
        cv2.rectangle(self.data, (2,2), (WIDTH_PIX-2, HEIGHT_PIX-2), (255, 10, 6), 1)
        cv2.rectangle(self.data, (2,2), (50, 13), (255, 150, 6), -1)
        cv2.rectangle(self.data, (2,2), (50, 13), (255, 10, 6), 1)
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

        x1 = min(max(0, event[0]), WIDTH_PIX)
        x2 = min(max(0, event[2]), WIDTH_PIX)

        y1 = min(max(0, event[1]), HEIGHT_PIX)
        y2 = min(max(0, event[3]), HEIGHT_PIX)

        self.data = cv2.line(
            self.data,
            (x1,y1),
            (x2,y2),
            (0, 0, 0) if event[4] == 1 else (255, 255, 255),
            1 if event[4] == 1 else 5,
        )

        print(event[4])
        # Add event to 'events'
        self.events.append(event)
