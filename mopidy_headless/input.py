from __future__ import unicode_literals

import logging

import threading

from evdev import ecodes, InputDevice, list_devices

from select import select

logger = logging.getLogger(__name__)


class InputThread(threading.Thread):
    def __init__(self):
        super(InputThread, self).__init__()
        self.name = "Input Thread"

        self._stop = threading.Event()
        self.devices_by_fn = {}
        self.devices_by_fd = {}
        self.handlers_by_fd = {}

    def stop(self):
        self._stop.set()
        logger.debug("Thread {0} is asked to stop".format(self.name))

    def register_handler(self, handler):
        if handler.device_fn in self.devices_by_fn:
            device = self.devices_by_fn[handler.device_fn]
        else:
            device = InputDevice(handler.device_fn)
            self.devices_by_fn[handler.device_fn] = device
            self.devices_by_fd[device.fd] = device
            self.handlers_by_fd[device.fd] = set()

        # Check if device has needed event
        capabilities = device.capabilities()
        if handler.event_type in capabilities:
            for event_code in handler.event_codes:
                if event_code in capabilities[handler.event_type]:
                    self.handlers_by_fd[device.fd].add(handler)
                else:
                    logger.warning('Event {0} not found in input device "{1}"'.format(
                        ecodes.bytype[handler.event_type][handler.event_code], device.name))
                    return False
        else:
            logger.warning(
                'Input device "{1}" has no capability {0}'.format(ecodes.EV[handler.event_type], device.name))
            return False

        return True

    def register_handlers(self, handlers):
        for handler in handlers:
            self.register_handler(handler)

    def run(self):
        while not self._stop.isSet():
            r, w, x = select(self.devices_by_fd, [], [], 10)
            for fd in r:
                for event in self.devices_by_fd[fd].read():
                    for handler in self.handlers_by_fd[fd]:
                        handler.check(event)
        logger.debug("Thread {0} stopped".format(self.name))


class Handler(object):
    def __init__(self, device_fn, event_type, event_codes):
        self.device_fn = device_fn

        if event_type in ecodes.ecodes:
            self.event_type = ecodes.ecodes[event_type]
        else:
            logger.error('Event type {0} unknown'.format(event_type))

        self.event_codes = list()
        for event_code in event_codes:
            if event_code in ecodes.ecodes:
                self.event_codes.append(ecodes.ecodes[event_code])
            else:
                logger.error('Event {0} not found for {1} events'.format(event_code, event_type))

    def check(self, event):
        if self.event_type == event.type:
            if event.code in self.event_codes:
                self.handle(event)

    def handle(self, event):
        pass
