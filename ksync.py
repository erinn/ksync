import logging

logger = logging.getLogger('KSync')


class KSync:
    """
    Provides methods to work with FleetSync.
    """

    def __init__(self, serial_port: object) -> None:
        """
        :param object serial_port: A serial port object, object must have a
        write() and flush() method.
        """
        self.serial_port: object = serial_port
        self.sequence: int = 0

    @staticmethod
    def _length_code(message: str) -> str:
        """
        :param str message: The message to be transmitted.

        Returns hex codes to indicate the length of the message to be sent to the serial port.

        If the message length is greater than 4096 characters an exception is thrown.

        <length_code> - indicates max possible message length, though the plain text message is not padded to that length
        46 hex (ascii F) - corresponds to 'S' (Short - 48 characters)
        47 hex (ascii G) - corresponds to both 'L' (Long - 1024 characters) and 'X' (Extra-long - 4096 characters)
        if you send COM port data with message body longer than that limit, the mobile will not transmit
        """

        length_of_message = len(message)

        if length_of_message <= 48:
            return '\x46'

        elif length_of_message <= 4096:
            return '\x47'

        else:
            raise Exception(f'Length of message is {length_of_message}, > 4096 characters and cannot be transmitted.')

    def send_text(self, message: str, fleet: str = '000', device: str = '0000', broadcast: bool = False) -> int:
        """
        :param str message: The text of the message to be sent.
        :param str fleet: The fleet code to be used as a string.
        :param device: The device code to be used as a string.
        :param bool broadcast: Is the message intended to be a broadcast.
        :return: The number of characters transmitted.
        :rtype: int

        Send a  message to a given radio, or broadcast a  message to all radios.
        """

        if fleet == '000' and device == '0000' and broadcast is False:
            raise Exception(f'Fleet number {fleet} and device number {device} can not be set to 000 '
                            'and 0000 respectively unless broadcast is desired, please set a fleet '
                            'number and device number or enable broadcast.')

        text = '\x02' + self._length_code(message) + fleet + device + message + str(self.sequence) + '\x03'

        return_length = self.serial_port.write(text.encode())
        self.sequence += 1

        # No assumption is made that this is used within a qthread, hence it is flushed.
        self.serial_port.flush()

        return return_length

    def poll_gnss(self):
        """
        Request a radio to return the current position using the
        Global Navigation Satellite Systems (commonly referred to as GPS).
        """
        pass

# sendText and pollGPS:
# self.firstComPort and secondComPort are not defined until valid FS data has been read from that port.
#  Even if we expand the definition of 'valid' data, we want to be able to send to a port regardless of
#  whether any data has yet been read from that port. May want to revise that to help with the send functions.

# How do we decide which COM port to send to?  There's no perfect solution, but, let's go with this plan:
# Q1: is self.firstComPort alive?
#   YES1: Q2: is self.secondComPort alive?
#     YES2: Q3: does self.fsLog have an entry for the device in question?
#       YES3: send to the com port specified for that device in self.fsLog
#                i.e. the com port on which that device was most recently heard from
#                 (if failed, send to the other port; if that also fails, show failure message)
#       NO3: send to the com port that has the most recent entry (for any device) in self.fsLog
#                 (if failed, send to the other port; if that also fails, show failure message)
#     NO2: send to firstComPort (if failed, show failure message - there is no second port to try)
#   NO1: cannot send - show a message box and return False
#

# def fsSendData(self,d,portList=None):
# 	portList=portList or [self.firstComPort]
# 	rprint('trying to send - portList='+str(portList))
# 	if portList and len(portList)>0:
# 		for port in portList:
# 			rprint('Sending FleetSync data to '+str(port.name)+'...')
# 			port.write(d.encode())
# 	else:
# 		rprint('Cannot send FleetSync data - no open ports were found.')

# can be called recursively by omitting arguments after d
# def fsSendData(self,d,fleet=None,device=None,port=None):
# 	# port=port or self.firstComPort
# 	if fleet and device:
# 		if int(fleet)==0 and int(device)==0: # it's a broadcast - send to both com ports in sequence
# 			self.firstComPort.write(d.encode())
# 			if self.secondComPort:
# 				time.sleep(3) # yes, we do want a blocking sleep
# 				self.secondComPort.write(d.encode())
# 			return True
# 		else:
# 			firstPortToTry=self.fsGetLatestComPort(fleet,device)
# 			secondPortToTry=None
# 			if firstPortToTry==self.firstComPort and self.secondComPort:
# 				secondPortToTry=self.secondComPort
# 			elif firstPortToTry==self.secondComPort and self.firstComPort:
# 				secondPortToTry=self.firstComPort
# 			firstPortToTry.write(d.encode())
# 			self.fsAwaitingResponse=[fleet,device,'Text message sent',0,d]
# 			[f,dev,t]=self.fsAwaitingResponse[0:3]
# 			self.fsAwaitingResponseMessageBox=QMessageBox(QMessageBox.Information,t,t+' to '+str(fleet)+':'+str(device)+'; awaiting response up to '+str(self.fsAwaitingResponseTimeout)+' seconds...',
# 							QMessageBox.Abort,self,Qt.WindowTitleHint|Qt.WindowCloseButtonHint|Qt.Dialog|Qt.MSWindowsFixedSizeDialogHint|Qt.WindowStaysOnTopHint)
# 			self.fsAwaitingResponseMessageBox.show()
# 			self.fsAwaitingResponseMessageBox.raise_()
# 			self.fsAwaitingResponseMessageBox.exec_()
# 			if self.fsFailedFlag: # timed out, or, got a '1' response
# 				rprint('failed; need to send again')
# 				if secondPortToTry:
# 					self.fsAwaitingResponseMessageBox.setText('No response after sending from preferred radio.  Sending from alternate radio; awaiting response up to '+str(self.fsAwaitingResponseTimeout)+' seconds...')
# 					secondPortToTry.write(d.encode())
# 					self.fsAwaitingResponse[3]=0 # reset the timer
# 			else:
# 				rprint('apparently successful')
# 			self.fsAwaitingResponse=None # clear the flag - this will happen after the messagebox is closed (due to valid response, or timeout in fsCheck, or Abort clicked)


# 	else: # this must be the recursive call where we actually send the data
# 		success=False
# 		if port:
# 			rprint('Sending FleetSync data to '+str(port.name)+'...')
# 			port.write(d.encode())
# 			return True
# 		else:
# 			msg='Cannot send FleetSync data - no valid FleetSync COM ports were found.  Keying the mic on a portable radio will trigger COM port recognition.'
# 			rprint(msg)
# 			box=QMessageBox(QMessageBox.Critical,'FleetSync error',msg,
# 				QMessageBox.Close,self,Qt.WindowTitleHint|Qt.WindowCloseButtonHint|Qt.Dialog|Qt.MSWindowsFixedSizeDialogHint|Qt.WindowStaysOnTopHint)
# 			box.open()
# 			box.raise_()
# 			box.exec_()
# 			return False


# Serial data format for sendText and pollGPS functions was discovered by using RADtext
#    https://radtext.morganized.com/radtext
#  along with a virtual COM port bridge, and a COM port terminal emulator to watch the traffic

# sendText - outgoing serial port data format:
#
# <start><length_code><fleet><device><msg><sequence><end>
#
# <start> - 02 hex (ascii smiley face)
# <length_code> - indicates max possible message length, though the plain text message is not padded to that length
#   46 hex (ascii F) - corresponds to 'S' (Short - 48 characters)
#   47 hex (ascii G) - corresponds to both 'L' (Long - 1024 characters) and 'X' (Extra-long - 4096 characters)
#   if you send COM port data with message body longer than that limit, the mobile will not transmit
# <fleet> - plain-text three-digit fleet ID (000 for broadcast)
# <device> - plain-text four-digit device ID (0000 for broadcast)
# <msg> - plain-text message
# UNUSED: <sequence> - plain-text two-digit decimal sequence identifier - increments with each send - probably not relevant
#   NOTE: sequnce is generated by radtext, but, it shows up as part of the message body on the
#          receiving device, which is probably not useful.  Interesting point that we could
#          add timestamp or such to the message body if needed, but, this is not a separate token.
# <end> - 03 hex (ascii heart)
#
# examples:
# broadcast 'test' (short):  02 46 30 30 30 30 30 30 30 74 65 73 74 32 39 03   F0000000test28  (sequence=28)
# 100:1002 'test' (short):  02 46 31 30 30 31 30 30 32 74 65 73 74 33 31 03   F1001002test31  (sequence=31)

# def sendText(self,fleetOrListOrAll,device=None,message=None):
# 	self.fsTimedOut=False
# 	self.fsResponseMessage=''
# 	broadcast=False
# 	self.fsSendList=[[]]
# 	self.fsFailedFlag=False
# 	if isinstance(fleetOrListOrAll,list):
# 		self.fsSendList=fleetOrListOrAll
# 	elif fleetOrListOrAll=='ALL':
# 		broadcast=True
# 	else:
# 		self.fsSendList=[[fleetOrListOrAll,device]]
# 	if message:
# 		if self.fsShowChannelWarning:
# 			m='WARNING: You are about to send FleetSync data burst noise on one or both mobile radios.\n\nMake sure that neither radio is set to any law or fire channel, or any other channel where FleetSync data bursts would cause problems.'
# 			box=QMessageBox(QMessageBox.Warning,'FleetSync Channel Warning',m,
# 							QMessageBox.Ok|QMessageBox.Cancel,self,Qt.WindowTitleHint|Qt.WindowCloseButtonHint|Qt.Dialog|Qt.MSWindowsFixedSizeDialogHint|Qt.WindowStaysOnTopHint)
# 			box.show()
# 			box.raise_()
# 			box.exec_()
# 			if box.clickedButton().text()=='Cancel':
# 				return
# 		timestamp=time.strftime("%b%d %H:%M") # this uses 11 chars plus space, leaving 36 usable for short message
# 		# timestamp=time.strftime('%m/%d/%y %H:%M') # this uses 14 chars plus space
# 		rprint('message:'+str(message))
# 		if broadcast:
# 			# portable radios will not attempt to send acknowledgement for broadcast
# 			rprint('broadcasting text message to all devices')
# 			d='\x02\x460000000'+timestamp+' '+message+'\x03'
# 			rprint('com data: '+str(d))
# 			suffix=' using one mobile radio'
# 			self.firstComPort.write(d.encode())
# 			if self.secondComPort:
# 				time.sleep(3) # yes, we do want a blocking sleep
# 				suffix=' using two mobile radios'
# 				self.secondComPort.write(d.encode())
# 			# values format for adding a new entry:
# 			#  [time,to_from,team,message,self.formattedLocString,status,self.sec,self.fleet,self.dev,self.origLocString]
# 			values=["" for n in range(10)]
# 			values[0]=time.strftime("%H%M")
# 			values[3]='TEXT MESSAGE SENT TO ALL DEVICES'+suffix+': "'+str(message)+'"'
# 			values[6]=time.time()
# 			self.newEntry(values)
# 		else:
# 			# recipient portable will send acknowledgement when fleet and device ase specified
# 			for [fleet,device] in self.fsSendList:
# 				# values format for adding a new entry:
# 				#  [time,to_from,team,message,self.formattedLocString,status,self.sec,self.fleet,self.dev,self.origLocString]
# 				values=["" for n in range(10)]
# 				callsignText=self.getCallsign(fleet,device)
# 				values[2]=str(callsignText)
# 				if callsignText:
# 					callsignText='('+callsignText+')'
# 				else:
# 					callsignText='(no callsign)'
# 				rprint('sending text message to fleet='+str(fleet)+' device='+str(device)+' '+callsignText)
# 				d='\x02\x46'+str(fleet)+str(device)+timestamp+' '+message+'\x03'
# 				rprint('com data: '+str(d))
# 				fsFirstPortToTry=self.fsGetLatestComPort(fleet,device) or self.firstComPort
# 				if fsFirstPortToTry==self.firstComPort:
# 					self.fsSecondPortToTry=self.secondComPort # could be None; inst var so fsCheck can see it
# 				else:
# 					self.fsSecondPortToTry=self.firstComPort # could be None; inst var so fsCheck can see it
# 				self.fsThereWillBeAnotherTry=False
# 				if self.fsSecondPortToTry:
# 					self.fsThereWillBeAnotherTry=True
# 				# rprint('1: fsThereWillBeAnotherTry='+str(self.fsThereWillBeAnotherTry))
# 				fsFirstPortToTry.write(d.encode())
# 				# if self.fsSendData(d,fsFirstPortToTry):
# 				self.fsAwaitingResponse=[fleet,device,'Text message sent',0,message]
# 				[f,dev,t]=self.fsAwaitingResponse[0:3]
# 				self.fsAwaitingResponseMessageBox=QMessageBox(QMessageBox.NoIcon,t,t+' to '+str(f)+':'+str(dev)+' on preferred COM port; awaiting response up to '+str(self.fsAwaitingResponseTimeout)+' seconds...',
# 								QMessageBox.Abort,self,Qt.WindowTitleHint|Qt.WindowCloseButtonHint|Qt.Dialog|Qt.MSWindowsFixedSizeDialogHint|Qt.WindowStaysOnTopHint)
# 				self.fsAwaitingResponseMessageBox.show()
# 				self.fsAwaitingResponseMessageBox.raise_()
# 				self.fsAwaitingResponseMessageBox.exec_()
# 				# add a log entry when Abort is pressed
# 				if self.fsAwaitingResponse and not self.fsTimedOut:
# 					values[0]=time.strftime("%H%M")
# 					values[1]='TO'
# 					values[3]='FLEETSYNC: Text message sent to '+str(f)+':'+str(dev)+' '+callsignText+' but radiolog operator clicked Abort before delivery could be confirmed: "'+str(message)+'"'
# 					values[6]=time.time()
# 					self.newEntry(values)
# 					self.fsResponseMessage+='\n\n'+str(f)+':'+str(dev)+' '+callsignText+': radiolog operator clicked Abort before delivery could be confirmed'
# 				if self.fsFailedFlag: # timed out, or, got a '1' response
# 					if self.fsSecondPortToTry:
# 						rprint('failed on preferred COM port; sending on alternate COM port')
# 						self.fsTimedOut=False
# 						self.fsFailedFlag=False # clear the flag
# 						self.fsSecondPortToTry.write(d.encode())
# 						self.fsThereWillBeAnotherTry=False
# 						# rprint('2: fsThereWillBeAnotherTry='+str(self.fsThereWillBeAnotherTry))
# 						self.fsAwaitingResponse[3]=0 # reset the timer
# 						self.fsAwaitingResponseMessageBox=QMessageBox(QMessageBox.NoIcon,t,t+' to '+str(f)+':'+str(dev)+' on alternate COM port; awaiting response up to '+str(self.fsAwaitingResponseTimeout)+' seconds...',
# 										QMessageBox.Abort,self,Qt.WindowTitleHint|Qt.WindowCloseButtonHint|Qt.Dialog|Qt.MSWindowsFixedSizeDialogHint|Qt.WindowStaysOnTopHint)
# 						self.fsAwaitingResponseMessageBox.show()
# 						self.fsAwaitingResponseMessageBox.raise_()
# 						self.fsAwaitingResponseMessageBox.exec_()
# 						# add a log entry when Abort is pressed
# 						if self.fsAwaitingResponse and not self.fsTimedOut:
# 							values[0]=time.strftime("%H%M")
# 							values[1]='TO'
# 							values[3]='FLEETSYNC: Text message sent to '+str(f)+':'+str(dev)+' '+callsignText+' but radiolog operator clicked Abort before delivery could be confirmed: "'+str(message)+'"'
# 							values[6]=time.time()
# 							self.newEntry(values)
# 							self.fsResponseMessage+='\n\n'+str(f)+':'+str(dev)+' '+callsignText+': radiolog operator clicked Abort before delivery could be confirmed'
# 						if self.fsFailedFlag: # timed out, or, got a '1' response
# 							rprint('failed on alternate COM port: message delivery not confirmed')
# 						else:
# 							rprint('apparently successful on alternate COM port')
# 							self.fsResponseMessage+='\n\n'+str(f)+':'+str(dev)+' '+callsignText+': delivery confirmed'
# 					else:
# 						rprint('failed on preferred COM port; no alternate COM port available')
# 				else:
# 					rprint('apparently successful on preferred COM port')
# 					self.fsResponseMessage+='\n\n'+str(f)+':'+str(dev)+' '+callsignText+': delivery confirmed'
# 				self.fsAwaitingResponse=None # clear the flag - this will happen after the messagebox is closed (due to valid response, or timeout in fsCheck, or Abort clicked)
# 			if self.fsResponseMessage:
# 				box=QMessageBox(QMessageBox.Information,'FleetSync Response Summary','FleetSync response summary:'+self.fsResponseMessage,
# 					QMessageBox.Close,self,Qt.WindowTitleHint|Qt.WindowCloseButtonHint|Qt.Dialog|Qt.MSWindowsFixedSizeDialogHint|Qt.WindowStaysOnTopHint)
# 				box.open()
# 				box.raise_()
# 				box.exec_()


# # pollGPS - outgoing serial port data format:
# #
# # <start><poll_code><fleet><device><sequence><end>
# #
# # <start> - 02 hex (ascii smiley face)
# # <poll_code> - 52 33 hex (ascii R3)
# # <fleet> - plain-text three-digit fleet ID (000 for broadcast)
# # <device> - plain-text four-digit device ID (0000 for broadcast)
# # UNUSED - see sendText notes - <sequence> - plain-text two-digit decimal sequence identifier - increments with each send - probably not relevant
# # <end> - 03 hex (ascii heart)

# # examples:
# # poll 100:1001:  02 52 33 31 30 30 31 30 30 31 32 35 03   R3100100120  (sequence=20)
# # poll 100:1002:  02 52 33 31 30 30 31 30 30 32 32 37 03   R3100100221  (sequence=21)

# def pollGPS(self,fleet,device):
# 	if self.fsShowChannelWarning:
# 		m='WARNING: You are about to send FleetSync data burst noise on one or both mobile radios.\n\nMake sure that neither radio is set to any law or fire channel, or any other channel where FleetSync data bursts would cause problems.'
# 		box=QMessageBox(QMessageBox.Warning,'FleetSync Channel Warning',m,
# 						QMessageBox.Ok|QMessageBox.Cancel,self,Qt.WindowTitleHint|Qt.WindowCloseButtonHint|Qt.Dialog|Qt.MSWindowsFixedSizeDialogHint|Qt.WindowStaysOnTopHint)
# 		box.show()
# 		box.raise_()
# 		box.exec_()
# 		if box.clickedButton().text()=='Cancel':
# 			return
# 	rprint('polling GPS for fleet='+str(fleet)+' device='+str(device))
# 	d='\x02\x52\x33'+str(fleet)+str(device)+'\x03'
# 	rprint('com data: '+str(d))
# 	self.fsTimedOut=False
# 	self.fsFailedFlag=False
# 	fsFirstPortToTry=self.fsGetLatestComPort(fleet,device) or self.firstComPort
# 	if fsFirstPortToTry==self.firstComPort:
# 		self.fsSecondPortToTry=self.secondComPort # could be None; inst var so fsCheck can see it
# 	else:
# 		self.fsSecondPortToTry=self.firstComPort # could be None; inst var so fsCheck can see it
# 	self.fsThereWillBeAnotherTry=False
# 	if self.fsSecondPortToTry:
# 		self.fsThereWillBeAnotherTry=True
# 	# rprint('3: fsThereWillBeAnotherTry='+str(self.fsThereWillBeAnotherTry))
# 	fsFirstPortToTry.write(d.encode())
# 	self.fsAwaitingResponse=[fleet,device,'Location request sent',0]
# 	[f,dev,t]=self.fsAwaitingResponse[0:3]
# 	self.fsAwaitingResponseMessageBox=QMessageBox(QMessageBox.NoIcon,t,t+' to '+str(f)+':'+str(dev)+' on preferred COM port; awaiting response up to '+str(self.fsAwaitingResponseTimeout)+' seconds...',
# 					QMessageBox.Abort,self,Qt.WindowTitleHint|Qt.WindowCloseButtonHint|Qt.Dialog|Qt.MSWindowsFixedSizeDialogHint|Qt.WindowStaysOnTopHint)
# 	self.fsAwaitingResponseMessageBox.show()
# 	self.fsAwaitingResponseMessageBox.raise_()
# 	self.fsAwaitingResponseMessageBox.exec_()
# 	# add a log entry when Abort is pressed
# 	if self.fsAwaitingResponse and not self.fsTimedOut:
# 		# values format for adding a new entry:
# 		#  [time,to_from,team,message,self.formattedLocString,status,self.sec,self.fleet,self.dev,self.origLocString]
# 		values=["" for n in range(10)]
# 		values[0]=time.strftime("%H%M")
# 		callsignText=self.getCallsign(f,dev)
# 		values[2]=str(callsignText)
# 		if callsignText:
# 			callsignText='('+callsignText+')'
# 		else:
# 			callsignText='(no callsign)'
# 		values[3]='FLEETSYNC: GPS location request set to '+str(f)+':'+str(dev)+' '+callsignText+' but radiolog operator clicked Abort before response was received'
# 		values[6]=time.time()
# 		self.newEntry(values)
# 	if self.fsFailedFlag: # timed out, or, got a '1' response
# 		if self.fsSecondPortToTry:
# 			rprint('failed on preferred COM port; sending on alternate COM port')
# 			self.fsTimedOut=False
# 			self.fsFailedFlag=False # clear the flag
# 			self.fsThereWillBeAnotherTry=False
# 			# rprint('5: fsThereWillBeAnotherTry='+str(self.fsThereWillBeAnotherTry))
# 			self.fsSecondPortToTry.write(d.encode())
# 			self.fsAwaitingResponse[3]=0 # reset the timer
# 			self.fsAwaitingResponseMessageBox=QMessageBox(QMessageBox.NoIcon,t,t+' to '+str(f)+':'+str(dev)+' on alternate COM port; awaiting response up to '+str(self.fsAwaitingResponseTimeout)+' seconds...',
# 							QMessageBox.Abort,self,Qt.WindowTitleHint|Qt.WindowCloseButtonHint|Qt.Dialog|Qt.MSWindowsFixedSizeDialogHint|Qt.WindowStaysOnTopHint)
# 			self.fsAwaitingResponseMessageBox.show()
# 			self.fsAwaitingResponseMessageBox.raise_()
# 			self.fsAwaitingResponseMessageBox.exec_()
# 			# add a log entry when Abort is pressed
# 			if self.fsAwaitingResponse and not self.fsTimedOut:
# 				# values format for adding a new entry:
# 				#  [time,to_from,team,message,self.formattedLocString,status,self.sec,self.fleet,self.dev,self.origLocString]
# 				values=["" for n in range(10)]
# 				values[0]=time.strftime("%H%M")
# 				callsignText=self.getCallsign(f,dev)
# 				values[2]=str(callsignText)
# 				if callsignText:
# 					callsignText='('+callsignText+')'
# 				else:
# 					callsignText='(no callsign)'
# 				values[3]='FLEETSYNC: GPS location request set to '+str(f)+':'+str(dev)+' '+callsignText+' but radiolog operator clicked Abort before response was received'
# 				values[6]=time.time()
# 				self.newEntry(values)
# 			if self.fsFailedFlag: # timed out, or, got a '1' response
# 				rprint('failed on alternate COM port: message delivery not confirmed')
# 			else:
# 				rprint('apparently successful on alternate COM port')
# 		else:
# 			rprint('failed on preferred COM port; no alternate COM port available')
# 	else:
# 		rprint('apparently successful on preferred COM port')
# 	self.fsAwaitingResponse=None # clear the flag - this will happen after the messagebox is closed (due to valid response, or timeout in fsCheck, or Abort clicked)
