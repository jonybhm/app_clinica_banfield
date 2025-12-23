# auxiliar/workers/task_manager.py
from PyQt5.QtCore import QThreadPool
from auxiliar.widgets.spinner import SpinnerDialog

class TaskManager:
    _instance = None

    def __init__(self):
        self.pool = QThreadPool.globalInstance()
        self.spinner = None
        self.active_tasks = 0

    @classmethod
    def instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    def run(self, task, mensaje="Procesando..."):
        if self.active_tasks == 0:
            self.spinner = SpinnerDialog(mensaje)
            self.spinner.show()

        self.active_tasks += 1

        task.signals.finished.connect(self._task_done)
        task.signals.error.connect(self._task_done)

        self.pool.start(task)

    def _task_done(self, *_):
        self.active_tasks -= 1
        if self.active_tasks <= 0 and self.spinner:
            self.spinner.close()
            self.spinner = None
