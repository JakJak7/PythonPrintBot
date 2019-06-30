#!/usr/bin/env python
# -*- coding: utf-8 -*-

from subprocess import check_output
import socket

def listen_for_connection():
    while (not is_connected()):
        print "sleeping..."
        time.sleep(5)
    return get_ip()

def is_connected():
    try:
        # connect to the host -- tells us if the host is actually
        # reachable
        socket.create_connection(("www.google.com", 80))
        return True
    except OSError:
        pass
    return False

def get_ip():
    return check_output(['hostname', '-I'])
