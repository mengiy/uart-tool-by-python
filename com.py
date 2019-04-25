#!python3

import threading
import time
import serial
import serial.tools.list_ports
import sys
import os
import struct

class util:
    def mkdir_log(data):
#        dirpath = os.getcwd() + '\\log\\' + data + '-' + tm
#        or
#        dirpath = '.\\log\\' + data + '-' + tm
        dirpath = '.\\' + data
        dirpath = dirpath.replace("\\", "/")
#        print(dirpath)
        dirpath_exists = os.path.exists(dirpath)
        if not dirpath_exists:
            try:
                os.makedirs(dirpath)
            except Exception as err:
                exit(err)
        return (dirpath + '/')
    def print_hex(data):
        if(type(data) == bytes):
            result = ' '.join(hex(x) for x in data)
            #print(' '.join(hex(x) for x in data))  #' '.join(hex(x)[2:] for x in data)
            return result
        if(type(data) == str):
            result = ' '.join(hex(ord(x)) for x in data)
            #print(' '.join(hex(ord(x)) for x in data))
            return result
        if(type(data) == list):
            tmp = ''
            if(type(data[0]) == bytes):
                for x in data:            #bytes list 转换为字符串
                    #tmp = tmp + str(x, "utf-8")  
                    tmp = tmp + hex(x[0]) + ' '
                result = tmp
                #print(tmp)
                return result
            if(type(data[0]) == str):
                tmp = ''.join(data)
                #print(' '.join(hex(ord(x)) for x in tmp))
                result = ' '.join(hex(ord(x)) for x in tmp)
                return result
        return  ''

class ComThread:
    def __init__(self):
        self.l_serial = None
        self.alive = False
        self.waitEnd = None
        self.log_path = None
        self.log_file = None
        self.port = self.FindComPort()

    def FindComPort(self):
        com_ports = list(serial.tools.list_ports.comports())
        if len(com_ports) <= 0:
            exit("found no serial ports!")
        else:
            print("serial ports are:")
            com_ports_list = list(com_ports)
            for i in range(len(com_ports)):
                serialName = com_ports_list[i]
                print("(%d) %s" %(i,serialName))
                del serialName
        try:
            select_port_no = int(input("select the serial port:"), 10)
        except ValueError:
            exit(1)
    #    print(select_port_no)
        try:
            if select_port_no >= len(com_ports):
                raise Exception("selected a wrong com port")
        except Exception as err:
            exit(err)
        else:
            try:
                if sys.platform.startswith('win') or sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
                    port = com_ports_list[select_port_no].device
                else:
                    raise EnvironmentError('Error finding ports on your operation system')
            except Exception as err:
                exit(err)
            else:
                return port
    def waiting(self):
        try:
            if not self.waitEnd is None:
                self.waitEnd.wait()
        except KeyboardInterrupt:
            self.SetStopEvent()

    def SetStopEvent(self):
        if not self.waitEnd is None:
            self.waitEnd.set()
        self.alive = False
        self.stop()

    def start(self):
        self.l_serial = serial.Serial()
        self.l_serial.port = self.port
        baudratelist = ['9600','14400','19200','38400','115200','460800','921600']
        for i in range(len(baudratelist)):
            print("(%d) %s"%(i,baudratelist[i]))
        try:
            baudratelist_no = int(input('select baudrate:'), 10)
        except ValueError:
            baudratelist_no = baudratelist.index('115200')
            print('format wrong, and set the default value %d' %baudratelist[baudratelist_no])
        try:
            if baudratelist_no >= len(baudratelist):
                raise Exception("selected a wrong baudrate")
        except Exception as err:
            exit(err)
        self.l_serial.baudrate = baudratelist[baudratelist_no];
        self.l_serial.timeout = 2
        self.l_serial.open()
        if self.l_serial.isOpen():
            self.waitEnd = threading.Event()
            self.waitEnd.clear()
            self.alive = True
            if not sys.platform.startswith('win'):
                self.log_path = util.mkdir_log('MIY-SERIAL-LOG')
#                print(self.log_path)
                tm = time.strftime('%Y-%m-%d-%H-%M-%S',time.localtime(time.time()))
                try:
                    self.log_file = open(self.log_path + tm +'.log', 'a')
                except Exception as err:
                    exit(err)
#                print('file name: %s'%self.log_file.name)
                del tm
            else:
                pass
            self.thread_read = None
            self.thread_read = threading.Thread(target=self.FirstReader)
            self.thread_read.setDaemon(1)
            self.thread_read.start()
            return True
        else:
            return False

    def FirstReader(self):
        while self.alive:
            time.sleep(0.1)

            data = ''
            data = data.encode('utf-8')

            n = self.l_serial.inWaiting()
            if n:
                 data = data + self.l_serial.read(n)
#                 print('RX:', data)

            n = self.l_serial.inWaiting()
            if len(data)>0 and n==0:
                try:
                    temp = data.decode('gb18030')
                    truncation = str(temp).splitlines(False)
                    for i in range(len(truncation)):
                        print(truncation[i])
                        if not self.log_file is None:
                            self.log_file.write(truncation[i] + '\r\n')
                except:
                    print("error try again")

        self.waitEnd.set()
        self.alive = False

    def stop(self):
        self.alive = False
        self.thread_read.join()
        if self.l_serial.isOpen():
            self.l_serial.close()
            if not self.log_file is None:
                self.log_file.close()

def main():
    rt = ComThread()
    rt.sendport = '**1*80*'
    try:
        if  rt.start():
#            print(rt.l_serial.name)
            rt.waiting()
            rt.stop()
        else:
            pass
    except Exception as se:
        print(str(se))

    if rt.alive:
        rt.stop()

    del rt

if __name__ == '__main__':
    print('---WELCOME TO MIY-SERIAL-TOOL---')
    main()
    print("------EXIT MIY-SERIAL-TOOL------")
