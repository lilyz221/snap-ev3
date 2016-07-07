from __future__ import print_function

import threading


def broadcast(table, message):

    if message not in table:
        print("No handlers for message " + message)
        return

    for handler in table[message]:
        th = threading.Thread(target=handler)
        th.start()
    
