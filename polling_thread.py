from time import sleep as _sleep
from threading import Thread as _Thread
from data_collector import DataCollector as _DataCollector


class PollingThread(_Thread):
    """This thread will call the data collector to poll for more data."""

    _running: bool = True

    def stop_polling(self) -> None:
        self._running = False

    def run(self) -> None:
        # The number of seconds the thread has been waiting between polls.
        seconds = 1800
        while self._running:
            # When we've waited for 30 minutes, poll again.
            if seconds == 1800:
                d = _DataCollector()
                d.retrieve_data_from_endpoints()
                d.save_data_to_file()
                seconds = 0
            else:
                # Sleeping for 30 minutes between requests
                _sleep(1)
                seconds += 1
