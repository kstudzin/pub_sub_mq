import argparse as ap
import logging
import sys
import threading
import time
import tkinter as tk
import tkinter.tix as widget

from pubsub.subscriber import Subscriber


class SubscriberUI:
    sub_logger = logging.getLogger("Subscriber")
    formatter = logging.Formatter('[%(levelname)s] %(message)s')
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(formatter)
    handler.setLevel(logging.DEBUG)
    sub_logger.addHandler(handler)
    sub_logger.setLevel(logging.DEBUG)

    def __init__(self):
        self.topic = None
        self.subscriber = None
        self.subscribe_btn = None
        self.topics = ['None']
        self.topic_menu = None
        self.selection = None
        self.unsubscribe_btn = None
        self.message_list = None
        self.list_scroll = None

    @staticmethod
    def config_parser() -> ap.ArgumentParser:
        """
        Configures the arguments accepted by the argparse module.
        :return: A (argparse.ArgumentParser)
        """
        parser = ap.ArgumentParser(prog='Subscriber', usage='%(prog)s [options]',
                                   description='Start subscribing to topics.')
        parser.add_argument('--port', metavar='Port', type=int, nargs='?',
                            help='port numbers')
        parser.add_argument('--topics', metavar='Topics', type=str, nargs='+',
                            help='topics to subscribe to')
        return parser

    @staticmethod
    def register(args) -> Subscriber:
        """
        Register a subscriber based upon user arguments.
        :param args: A port number and a list of topics provided in arguments
        :return: A Subscriber object
        """
        if args.port is not None:
            subscriber = Subscriber(f"tcp://localhost:{args.port}")
        else:
            return None

        if args.topics is not None:
            for topic in args.topics:
                subscriber.register(topic)
        return subscriber

    def listen_for_messages(self, window):
        self.sub_logger.info("Listening....")
        self.message_list.insert("end", "Listening....")
        while True:
            # this.subscriber getMessages
            sample = "2021-05-25 13:19:42.504443 : FB : 202.11"
            sent_time, topic, message = sample.split(" : ")
            self.message_list.insert(tk.END, f"Time= {sent_time} Topic= {topic} Message= {message}")
            self.message_list.see(tk.END)
            window.update()
            time.sleep(3)

    def build_ui(self) -> widget.WINDOW:
        window = tk.Tk()
        window.title("Subscriber")
        window.geometry("480x320+200+50")
        window.config(border=10, bg='#eee')
        window.columnconfigure(0, weight=100)
        window.columnconfigure(1, weight=300)
        window.columnconfigure(2, weight=100)
        window.columnconfigure(3, weight=1)
        window.rowconfigure(0, weight=1)
        window.rowconfigure(1, weight=1)
        window.rowconfigure(2, weight=10)

        # ************************ Subscribe ********************************
        label = tk.Label(window, bg='#eee', text="Enter topic to subscribe")
        label.grid(row=0, column=0, sticky='w')
        self.topic = tk.StringVar()
        self.topic.trace_add("write", self.field_changed)
        field = tk.Entry(window, textvariable=self.topic, width=10, justify='left')
        field.config(relief='sunken', borderwidth=3, selectborderwidth=5, background='#fff')
        field.config(highlightbackground='#eee', highlightcolor='#777')
        field.grid(row=0, column=1, sticky='ew')
        self.subscribe_btn = tk.Button(window, text='Subscribe', command=self.submit_subscribe, state='disabled')
        self.subscribe_btn.config(activebackground='#888', fg='#000', default='active')
        self.subscribe_btn.grid(row=0, column=2, sticky='w')

        # ************************ Unsubscribe ********************************
        self.selection = tk.StringVar()
        self.selection.set(self.topics[0])
        self.selection.trace_add("write", self.selection_changed)
        self.topic_menu = tk.OptionMenu(window, self.selection, *self.topics)
        self.topic_menu.config(fg='#000', width=15, highlightbackground='#eee', background='#fff')
        self.topic_menu.grid(row=1, column=1, sticky='ew')
        self.unsubscribe_btn = tk.Button(window, text='Unsubscribe', command=self.submit_unsubscribe, state='disabled')
        self.unsubscribe_btn.config(activebackground='#888', fg='#000')
        self.unsubscribe_btn.grid(row=1, column=2, sticky='w', columnspan=2)

        # ************************ Message box ********************************
        self.message_list = tk.Listbox(window)
        self.message_list.config(border=3, relief='sunken', selectmode='single')
        self.message_list.grid(row=2, column=0, sticky='nsew', columnspan=3)
        for i in range(20):
            self.message_list.insert(tk.END, f"Sample{i}")
        self.list_scroll = tk.Scrollbar(window, orient=tk.VERTICAL, width=11)
        self.list_scroll.config(command=self.message_list.yview)
        self.list_scroll.grid(row=2, column=3, sticky='nsw')
        self.message_list['yscrollcommand'] = self.list_scroll.set
        self.message_list.see(tk.END)

        window.update()
        window.minsize(width=400, height=250)
        window.maxsize(width=500, height=350)
        return window

    def field_changed(self, *args):
        topic = self.topic.get().strip()
        self.sub_logger.info(f"Text changed: {topic}")
        if len(topic) > 0:
            self.subscribe_btn['state'] = "normal"
        else:
            self.subscribe_btn['state'] = "disabled"

    def selection_changed(self, *args):
        selection = self.selection.get()
        self.sub_logger.info(f"Selection changed: {selection}")
        if not selection:
            self.unsubscribe_btn['state'] = "normal"
        else:
            self.unsubscribe_btn['state'] = "disabled"

    def submit_subscribe(self):
        value = self.topic.get()
        self.sub_logger.info(f"Subscribe button pressed {value}")
        self.subscriber.register(value)
        self.topics.append(value)
        self.topic
        self.topic.set("")

    def submit_unsubscribe(self):
        value = self.selection.get()
        self.sub_logger.info(f"Unsubscribe button pressed {value}")
        if value:
            self.topics.remove(value)


def main():
    sub_ui = SubscriberUI()
    arg_parser = sub_ui.config_parser()
    args = arg_parser.parse_args()
    sub_ui.subscriber = sub_ui.register(args)
    time.sleep(3)
    window = sub_ui.build_ui()
    window.mainloop()
    sub_ui.listen_for_messages(window)

    # threading.Thread(target=listen_for_messages, daemon=True).start()


if __name__ == "__main__":
    main()
