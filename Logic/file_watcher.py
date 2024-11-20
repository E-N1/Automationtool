from Configurations.read_timecontroll import ReadTimecontroll
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import datetime as dt
import time
import os

class FileWatcher:
    def __init__(self, file_path, function=None, *args):
        self.file_path = file_path
        self.function = function
        self.args = args
        self.observer = None
        self._stop_flag = False
        self.readTimeControll = ReadTimecontroll()

    def start(self):
        """
        Starts the file watcher.

        This method prints a message indicating the file path being watched,
        sets the stop flag to False, and starts a new daemon thread that runs
        the `run` method.
        """
        print(f"Überwache {self.file_path}")
        self._stop_flag = False
        threading.Thread(target=self.run, daemon=True).start()

    def run(self):
        """
        Monitors a specified file for changes and triggers a function when the file is modified.

        This method sets up a file system event handler that watches for modifications to a specific file.
        When the file is modified, it checks the current status of a machine and, if the machine is free,
        executes a specified function with given arguments.

        The method runs an infinite loop that periodically checks for a stop flag to terminate the observer.

        Attributes:
            file_path (str): The path of the file to be monitored.
            readTimeControll (object): An object that provides the current status of the machine.
            args (list): A list of arguments to be passed to the function.
            function (callable): The function to be executed when the file is modified.
            _stop_flag (bool): A flag to stop the observer loop.

        Classes:
            FileChangeHandler: A nested class that handles file modification events.

        Methods:
            on_modified(event): Called when the monitored file is modified.

        """
        class FileChangeHandler(FileSystemEventHandler):
            def __init__(self, outer_instance):
                self.outer_instance = outer_instance

            def on_modified(self, event):
                """
                Handles the event when a file is modified.

                Args:
                    event (FileSystemEvent): The event object containing information about the file system event.

                Behavior:
                    - Checks if the modified file is the one being watched.
                    - Retrieves the current status of the machine associated with the file.
                    - If the machine is free, logs the modification time and executes the associated function.
                    - If the machine is not free, logs a waiting message.
                    - Sleeps for 1 second before the next check.
                """
                if event.src_path == self.outer_instance.file_path:
                    now = dt.datetime.now()
                    status = self.outer_instance.readTimeControll.getCurrentStatus(self.outer_instance.args[0])
                    print(f"Status: {status}")
                    if status:
                        print("\033[32m" + f"[{now.strftime('%d.%m.%y - %H:%M')}] - Datei {self.outer_instance.file_path} wurde geändert." + "\033[0m")
                        self.outer_instance.function(*self.outer_instance.args)
                    else:
                        print(f"Machine {self.outer_instance.args[0]} is not free. Waiting..."),
                time.sleep(1)  # Check every second

        event_handler = FileChangeHandler(self)
        observer = Observer()
        observer.schedule(event_handler, path=os.path.dirname(self.file_path), recursive=False)
        observer.start()

        while not self._stop_flag:
            time.sleep(10)  # Überprüfung in regelmäßigen Abständen
        observer.stop()
        observer.join()

    def stop(self):
        """stops the file watcher"""
        self._stop_flag = True
        print(f"Beobachtung von {self.file_path} gestoppt.")