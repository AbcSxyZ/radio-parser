#!/usr/bin/env python3

import argparse
import signal
from radio_site import Site
from logger import LogRadio
import os
import sys
import time

LOGGER = None
MAX_PROCESS = 4
MAX_PARSE_TIME = 60 * 7

def get_options():
    """

    """

    parser = argparse.ArgumentParser(description="Retrieve mail from websites")
    parser.add_argument('filename', type=str, nargs=1)
    return parser.parse_args()

def exit_scan(*args, **kwargs):
    sys.exit(0)

def child_radio_scan(radio):
    signal.signal(signal.SIGALRM, exit_scan)
    signal.alarm(MAX_PARSE_TIME)
    if len(radio.site.strip()) == 0:
        return
    try:
        site_instance = Site(radio.site)
        site_instance.site_loop()

    except Exception as error:
        print(error)
    finally:
        LOGGER.update_info(radio.name, site_instance.list_mails)

def radio_scan(radio):
    pid = os.fork()
    if pid == 0:
        child_radio_scan(radio)
        sys.exit(0)
    return pid

def control_pid_state(pids):
    """
    Control if some process are over, and remove
    them from the current list of pid.
    """
    ended_pids = []
    for pid in pids:
        res = os.waitpid(pid, os.WNOHANG)
        if res[0] == pid:
            ended_pids.append(pid)
    
    for pid in ended_pids:
        pids.remove(pid)

def launch_scanner():
    """
    """
    launched_process = 0
    radio_list = LOGGER.radio_list()
    pids = []
    while radio_list:
        radio = radio_list.pop()
        
        while len(pids) >= MAX_PROCESS:
            control_pid_state(pids)
            time.sleep(1)
        if len(pids) < MAX_PROCESS:
            pids.append(radio_scan(radio))
            launched_process += 1

    while pids:
        control_pid_state(pids)
        time.sleep(1)







if __name__ == "__main__":
    args = get_options()
    # parse_site(args.url[0])
    # Site(args.url[0])
    LOGGER = LogRadio(args.filename[0])
    launch_scanner()
    
