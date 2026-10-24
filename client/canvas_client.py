import socket
import threading
from CDRT_Canvas import CRDT_Canvas, WIDTH_PIX, HEIGHT_PIX
from tkinter import *
from tkinter import ttk
import cv2
from PIL import Image, ImageTk
import numpy as np
import sys

SCALE = 8

class Sketchpad(Canvas):
    def __init__(self, parent, cdrt: CRDT_Canvas, client: socket.socket, **kwargs):
        super().__init__(parent, **kwargs)

        self.bind("<Button-1>", self.save_posn)
        self.bind("<B1-Motion>", self.add_line)
        self.bind("<Destroy>",  self.end)

        self.close = False
        self.cdrt = cdrt
        self.client= client

        self.displayim = self.create_image((0,0), image=self.data_PIL(), anchor="nw")
        self.display_image()
        
    def save_posn(self, event):
        self.lastx, self.lasty = event.x // SCALE, event.y // SCALE

    def data_PIL(self):
        img = cv2.resize(self.cdrt.get_canvas(), (WIDTH_PIX*SCALE,HEIGHT_PIX*SCALE))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        im = Image.fromarray(img)
        imgtk = ImageTk.PhotoImage(image=im)
        return imgtk

    def display_image(self):
        if self.close: raise RuntimeError
        self.imgtk = self.data_PIL()
        self.itemconfigure(self.displayim, image=self.imgtk)

    def add_line(self, event):        
        
        self.cdrt.update_draw(self.lastx, self.lasty, event.x // SCALE, event.y // SCALE)
        self.client.send(bytes((self.lastx, self.lasty, event.x // SCALE, event.y // SCALE, 1)))

        self.display_image()
        self.save_posn(event)

    def end(self, events): self.close = True


HOST = "127.0.0.1"
PORT = 12345


def recv_updates(client: socket.socket, canvas: CRDT_Canvas):
    try:
        while True:
            data = client.recv(5)
            #print("Server:", data.decode())

            if not data: continue

            event = tuple(data)

            print("Server: ", event)
            canvas.merge(event)
    except:
        pass 
    finally:
        client.close()


def main(HOST, PORT):
    canvas = CRDT_Canvas()

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))


    recieve_thread = threading.Thread(
        target=recv_updates,
        args=(client,canvas),
        daemon=True
    )

    recieve_thread.start()

    root = Tk()
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    sketch = Sketchpad(root, 
        cdrt= canvas,
        client=client,
        width=WIDTH_PIX * SCALE,
        height=HEIGHT_PIX * SCALE,
        bg="white",
        highlightthickness=0)
    sketch.grid(column=0, row=0, sticky=(N, W, E, S))

    try:
        while True:
            root.update_idletasks()
            sketch.display_image()
            root.update()
    except:
        client.send(bytes((0,)))
        client.close()
        quit()

host, port = "127.0.0.1", 12345
if len(sys.argv) > 1:
    addr_parts = sys.argv[1].split(":")
    host = addr_parts[0]
    if len(addr_parts) == 2:
        port = int(addr_parts[1])


main(host, port)