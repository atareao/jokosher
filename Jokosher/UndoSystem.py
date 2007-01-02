#
#	THIS FILE IS PART OF THE JOKOSHER PROJECT AND LICENSED UNDER THE GPL. SEE
#	THE 'COPYING' FILE FOR DETAILS
#
#	UndoSystem.py
#
#	Contains the decorator needed to allow other classes to hook specific
#	function calls into the undo stack.
#
#=========================================================================

import Project, Globals, Utils

def UndoCommand(*command):
	"""
	Decorates functions, enabling them to be logged in the undo stack.
	The decorating process is transparent to the clients.
	
	Parameters:
		command -- the undo command list of strings.
		
	Returns:
		an UndoFunction which decorates the original function.
	"""
	
	def UndoFunction(func):
		"""
		This is the actual decorator function. When decorated,
		this function will be called with func as the function to
		be decorated.
		
		Parameters:
			func -- the function to be decorated.
			
		Returns:
			an UndoWrapper to replace the function, so that when it
			is called, UndoWrapper will be called instead, and will:
				1)log the function call to the undo stack, and 
				2)call the function originally wanted.
		"""
		
		def UndoWrapper(funcSelf, *args, **kwargs):
			"""
			This function will wrap and take the place of the function
			that is being decorated. All arguments to the original function
			will be saved, and sent to the decorated function call.
			The funcSelf value must be the first parameter, because
			the first parameter will always be self, and it carries a
			reference to the decorated function's class.
			
			Considerations:
				All decorated undo functions *must* be in a class or this will fail.
				
			Parameters:
				funcSelf -- reference to the decorated function's class.
				*args -- parameters meant for the decorated function.
				**kwargs -- dictionary of keyword:value parameters meant
							for the decorated function.
			
			Returns:
				the wrapped function resulting value.
			"""
			atomicUndoObject = None
			if kwargs.has_key("_undoAction_"):
				atomicUndoObject = kwargs["_undoAction_"]
				#remove the keyword from kwargs so it doesn't get passed to the function
				del kwargs["_undoAction_"]
			
			try:
				result = func(funcSelf, *args, **kwargs)
			except CancelUndoCommand, e:
				return e.result
			
			# initialize the AtomicUndoAction object *after* we call the function,
			# so that if CancelUndoCommand is raise, nothing is appended to the stack
			if not atomicUndoObject:
				#if we were not provided one, create a default atomic undo object 
				atomicUndoObject = AtomicUndoAction()
			
			if isinstance(funcSelf, Project.Project):
				objectString = "P"
			elif isinstance(funcSelf, Project.Instrument):
				objectString = "I%d" % funcSelf.id
			elif isinstance(funcSelf, Project.Event):
				objectString = "E%d" % funcSelf.id
			
			paramList = []
			for param in command[1:]:
				try:
					value = getattr(funcSelf, param)
				except:
					continue
				else:
					paramList.append(value)
				
			atomicUndoObject.AddUndoCommand(objectString, command[0], paramList)
			
			return result
		
			#_____________________________________________________________________
			
		return UndoWrapper
	
		#_____________________________________________________________________
		
	return UndoFunction

	#_____________________________________________________________________
	
#=========================================================================

class CancelUndoCommand(Exception):
	"""
	This exception can be thrown by a decorated undo
	function in order to tell the undo system to not
	log the current action. This is useful if something
	in the function fails and the action that would have
	been logged to the undo stack was never actually completed.
	"""
	def __init__(self, result=None):
		"""
		Creates a new instance of CancelUndoCommand.
		
		Parameters:
			result -- value the wrapped function intended to return,
						but failed and called this exception.
		"""
		Exception.__init__(self)
		self.result = result
	
	#_____________________________________________________________________

#=========================================================================

class AtomicUndoAction:
	"""
	Contains several undo commands to be treated as a single undoable operation.
	
	Example:
		When deleting several Instruments at once, an AtomicUndoAction
		containing the commands to resurrect the Instruments will be created.
		When the user requests an undo operation, all of the commands stored
		in this	object will be rolled back, making the operation appear	to be
		atomic from the user's perspective.
	"""
	
	#_____________________________________________________________________
	
	def __init__(self, addToStack=True):
		"""
		Creates a new AtomicUndoAction instance and optionally adds it to the
		undo stack.
		
		Parameters:
			addToStack -- if True, this instance will be added to the currently
						active Project's undo/redo stack.
		"""
		self.commandList = []
		if addToStack:
			# add ourselves to the undo stack for the current Project.
			Project.GlobalProjectObject.AppendToCurrentStack(self)
	
	#_____________________________________________________________________
	
	def AddUndoCommand(self, objectString, function, paramList):
		"""
		Adds a new undo command to this AtomicUndoAction.
		
		Example:
			A command inside an AtomicUndoAction object:
				cmdList = ["E2", "Move", 1, 2]
			means
				'Call Move(1, 2)' on the Event with ID=2
		
		Parameters:
			objectString -- the string representing the object and its ID
							(ie "E2" for Event with ID == 2).
			function -- the name of the function to be called on the object.
			paramList -- a list of values to be passed to the function as parameters.
						Key, value parameters are not supported.
		"""
		newTuple = (objectString, function, paramList)
		self.commandList.append(newTuple)
		Globals.debug("LOG COMMAND: ", newTuple, "from", id(self))
	
	#_____________________________________________________________________
	
	def GetUndoCommands(self):
		"""
		Obtains the list of undo commands held by this AtomicUndoAction.
		
		Returns:
			a list of tuples, each of which contains a single undo command.
		"""
		return self.commandList
	
	#_____________________________________________________________________
	
	def StoreToXML(self, doc, node):
		"""
		Stores this instance of AtomicUndoAction into an XML node.
		
		Example:
				doc = xml.Document()
				node = doc.createElement("Action")
				doc.appendChild(node)
				StoreToXml(doc, node)
				
			will save this AtomicUndoAction in doc, inside node.
		
		Parameters:
			doc -- XML document to save this AtomicUndoAction into.
			node -- XML node to store this AtomicUndoAction under.
					This node's name should be "Action".
		"""
		for cmd in self.GetUndoCommands():
			commandXML = doc.createElement("Command")
			parent.appendChild(commandXML)
			commandXML.setAttribute("object", cmd[0])
			commandXML.setAttribute("function", cmd[1])
			Utils.StoreListToXML(doc, commandXML, cmd[2], "Parameter")
		
	#_____________________________________________________________________
	
#=========================================================================

def LoadUndoActionFromXML(node):
	"""
	Loads an AtomicUndoAction from an XML node.
	
	Parameters:
		node -- XML node from which the AtomicUndoAction is loaded.
				Should be an "<Action>" node.
		
	Returns:
		the loaded AtomicUndoAction object.
	"""
	# Don't add to the undo stack because the Project is being loaded
	undoAction = AtomicUndoAction(addToStack=False)
	for cmdNode in node.childNodes:
		if cmdNode.nodeName == "Command":
			objectString = str(cmdNode.getAttribute("object"))
			functionString = str(cmdNode.getAttribute("function"))
			paramList = Utils.LoadListFromXML(cmdNode)
			
			undoAction.AddUndoCommand(objectString, functionString, paramList)
	
	return undoAction

#=========================================================================
