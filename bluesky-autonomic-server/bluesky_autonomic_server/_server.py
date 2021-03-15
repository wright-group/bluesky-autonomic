__all__ = ["Server"]


import asyncio
import json
from dataclasses import asdict

import zmq
import zmq.asyncio

from ._device import Device
from . import _logging as logging




class Server(object):

    def __init__(self, rpc_port:int, pub_port:int, debug):
        self.logger = logging.getLogger("bluesky-autonomic-server")
        if debug:
             self.logger.setLevel(logging.name_to_level["debug"])
             self.logger.debug("Logging level set to debug.")
        self.logger.info("test")
        self._devices = {}
        self._context = zmq.asyncio.Context()
        # setup REP socket
        self._rep_socket = self._context.socket(zmq.REP)
        self._rep_socket.bind(f"tcp://*:{rpc_port}")
        self.logger.info(f"RPC port = {rpc_port}")
        # setup PUB socket
        self._pub_socket = self._context.socket(zmq.PUB)
        self._pub_socket.bind(f"tcp://*:{pub_port}")
        self.logger.info(f"PUB port = {pub_port}")
        self._pub_port = pub_port
        # run
        loop = asyncio.get_event_loop()
        loop.create_task(self.recv_and_process())
        try:
            loop.run_forever()
        except asyncio.CancelledError:
            pass
        finally:
            loop.close()

    def add_device(self, device:str) -> dict:
        """Add new device. If the device already exists that's OK."""
        if device in self._devices:
            new = self._devices[device]
        else:
            new = Device(name=device)
            self._devices[device] = new
        self.publish(device)
        return asdict(new)

    def get_pub_port(self) -> int:
        return self._pub_port

    def publish(self, device:str) -> None:
        dic = asdict(self._devices[device])
        out = f"{device} {dic}"
        self.logger.debug(f"Publishing | Topic: {device} | Message: {dic}")
        self._pub_socket.send(out.encode())

    async def recv_and_process(self):
        """Recieve and process jsonrpc calls."""
        while True:
            msg = await self._rep_socket.recv()
            try:
                rpc = json.loads(msg.decode())
                method = getattr(self, rpc["method"])
                returned = method(**rpc["params"])
                if not "id" in rpc:
                    # lack of field "id" indicates that the client sent a "notification"
                    # and is not expecting a response
                    continue
                reply = dict()
                reply["jsonrpc"] = "2.0"
                reply["result"] = returned
                reply["id"] = rpc["id"]
                await self._rep_socket.send(json.dumps(reply).encode())
            except Exception as e:
                self.logger.warning(f"Exception in recv_and_process = {e}")

    def set_device_destination(self, device:str, destination:float) -> dict:
        device = self._devices[device]
        device.destination = destination
        self.publish(device)
        return asdict(new)
