# auxiliar/workers/base_task.py
from PyQt5.QtCore import QObject, pyqtSignal, QRunnable

class TaskSignals(QObject):
    finished = pyqtSignal(object)
    error = pyqtSignal(str)

class BaseTask(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = TaskSignals()

    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
            self.signals.finished.emit(result)
        except Exception as e:
            print("❌ ERROR EN TASK:", e)
            import traceback
            traceback.print_exc()
            self.signals.error.emit(str(e))
