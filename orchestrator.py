"""
Orchestrator has a lot of functions like manage the hardwares, data aquairing,
so state machine belongs to Orchestrator, and it is actually the encapsulation of the hardware management
"""

from enum import Enum, auto
from typing import Dict, Optional
import logging
from datetime import datetime
import asyncio
from dataclasses import dataclass
import threading
from queue import Queue

from state_machine import StateMachine


class EventType(Enum):
    STATE_CHANGED = auto()
    ERROR = auto()
    TASK_COMPLETED = auto()


@dataclass
class Event:
    type: EventType
    timestamp: datetime
    state: str
    data: dict = None


class Orchestrator:
    def __init__(self):
        self.event_queue: asyncio.Queue = asyncio.Queue()
        self.logger = logging.getLogger("Orchestrator")
        self.state_machine = StateMachine()
        self._running = False
        self._pause_event = threading.Event()
        self._stop_event = threading.Event()

    async def start(self):
        """Start the orchestrator and initialize state machine"""
        self._running = True
        self._stop_event.clear()
        self._pause_event.clear()

        # Start event handler
        asyncio.create_task(self.event_handler())

        # Initialize state machine in a separate thread
        self.state_machine_thread = threading.Thread(target=self._run_state_machine)
        self.state_machine_thread.daemon = True
        self.state_machine_thread.start()

        await self.event_queue.put(
            Event(
                EventType.STATE_CHANGED,
                datetime.now(),
                self.state_machine.state,
                {"message": "Orchestrator started"},
            )
        )

    def _run_state_machine(self):
        """Run state machine in a separate thread"""
        try:
            self.state_machine.auto_run()
        except Exception as e:
            asyncio.run_coroutine_threadsafe(
                self.handle_error(str(e)), asyncio.get_event_loop()
            )

    async def stop(self):
        """Stop the orchestrator and state machine"""
        self._running = False
        self._stop_event.set()
        if self.state_machine_thread and self.state_machine_thread.is_alive():
            self.state_machine_thread.join()

        await self.event_queue.put(
            Event(
                EventType.STATE_CHANGED,
                datetime.now(),
                self.state_machine.state,
                {"message": "Orchestrator stopped"},
            )
        )

    async def pause(self):
        """Pause the orchestrator"""
        self._pause_event.set()
        await self.event_queue.put(
            Event(
                EventType.STATE_CHANGED,
                datetime.now(),
                self.state_machine.state,
                {"message": "Orchestrator paused"},
            )
        )

    async def resume(self):
        """Resume the orchestrator"""
        self._pause_event.clear()
        await self.event_queue.put(
            Event(
                EventType.STATE_CHANGED,
                datetime.now(),
                self.state_machine.state,
                {"message": "Orchestrator resumed"},
            )
        )

    async def handle_error(self, error_msg: str):
        """Handle errors from the state machine"""
        await self.event_queue.put(
            Event(
                EventType.ERROR,
                datetime.now(),
                self.state_machine.state,
                {"error": error_msg},
            )
        )
        await self.stop()

    async def event_handler(self):
        """Process events from the event queue"""
        while self._running:
            event = await self.event_queue.get()

            if event.type == EventType.ERROR:
                self.logger.error(
                    f"Error in state {event.state}: {event.data['error']}"
                )
            elif event.type == EventType.STATE_CHANGED:
                self.logger.info(f"State changed to: {event.state}")
                if event.data:
                    self.logger.info(f"Additional info: {event.data['message']}")

            self.event_queue.task_done()

    def get_current_state(self) -> str:
        """Get current state of the state machine"""
        return self.state_machine.state

    def is_running(self) -> bool:
        """Check if orchestrator is running"""
        return self._running and not self._stop_event.is_set()

    def is_paused(self) -> bool:
        """Check if orchestrator is paused"""
        return self._pause_event.is_set()


# Example usage
async def main():
    # Create orchestrator
    orch = Orchestrator()

    try:
        # Start orchestrator
        await orch.start()

        # Let it run for a while
        await asyncio.sleep(10)

        # Pause example
        await orch.pause()
        await asyncio.sleep(2)

        # Resume example
        await orch.resume()
        await asyncio.sleep(5)

        # Stop orchestrator
        await orch.stop()

    except Exception as e:
        print(f"Error: {e}")
        await orch.stop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
