import copy
import os
import sys
import time
import threading
from multiprocessing import Process, Queue

from PyQt4 import uic
from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.uic import loadUiType

import commander
import mappings


THISDIR = os.path.realpath(os.path.dirname(__file__))


class Commander(QtGui.QMainWindow):
    def __init__(self, parent=None):
        """
        MPPT Commander simple UI for viewing the state of the controller.
        """
        QtGui.QMainWindow.__init__(self, parent)
        uic.loadUi(os.path.join(THISDIR, "ui", "commander.ui"), self)
        self.__queue = Queue()
        self.__widgets = {}
        self.__running = True

        self.__timer = QtCore.QTimer(self)
        self.connect(self.__timer, QtCore.SIGNAL("timeout()"), self.update)
        self.__timer.start(10)

        self.__process = Process(target=self.populateColumns, args=())
        self.__process.start()

    def update(self):
        """
        Update the UI in the main thread.  This is triggered by a timer.
        """
        if self.__queue.empty():
            return
        key, name, register, num = self.__queue.get()
        key = "%s-%s" % (key, name)
        mess = "%s (%s): %s" % (name, register.unit, register.value)
        self.statusBar().showMessage(mess)
        if key not in self.__widgets:
            self.__widgets[key] = QtGui.QListWidgetItem(mess)
            if num <= 32:
                self.arrayInfoListWidget.addItem(self.__widgets[key])
            elif num <= 64:
                self.batteryInfoListWidget.addItem(self.__widgets[key])
            else:
                self.loadInfoListWidget.addItem(self.__widgets[key])
        else:
            #self.__widgets[key].setText(mess)
            #self.statusBar().showMessage(mess)
            pass

    def closeEvent(self, event):
        """
        Event that is triggered on close.
        """
        reply = QtGui.QMessageBox.question(self, 'Message',
            "Are you sure to quit?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            self.__running = False
            self.__timer.stop()
            self.__process.terminate()
            event.accept()
        else:
            event.ignore()

    def populateColumns(self):
        """
        Query the Commander unit and push all items into a queue to get popped
        off in the main thread.  This is run in a new process using the
        multiprocessing module in order to make the UI responsive while
        querying the device.  A thread would probably also work.
        """
        # The ID of the device we are going to communicate with.  Default is 1.
        deviceId = 0x01

        while self.__running:
            ser = commander.getRs485()

            try:
                num = 1
                for addr, reg in sorted(mappings.REGISTERS.iteritems()):
                    if not self.__running:
                        break
                    results = commander.communicate(ser,
                                                    deviceId,
                                                    addr,
                                                    reg,
                                                    debug=False)
                    wasList = False
                    if not isinstance(results, list):
                        wasList = True
                        results = [results, ]

                    for item in results:
                        if wasList:
                            key = "%s-%s" % (addr, reg.unit)
                            self.__queue.put([key, reg.name, item, num])
                        else:
                            self.__queue.put([addr, reg.name, item, num])
                    num += 1
            except:
                raise
            finally:
                # Close the port regardless of which errors occur
                ser.close()


if __name__ == "__main__":
    # Create the QApplication and spawn a Commander window.  Block until it is
    # done.
    app = QtGui.QApplication(sys.argv)
    w = Commander()
    w.setWindowTitle('MPPT Commander')
    w.show()
    sys.exit(app.exec_())

