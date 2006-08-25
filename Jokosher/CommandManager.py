
import types
import Project

#=========================================================================

class CommandManaged(object):
	
	#_____________________________________________________________________
	
	def __getattribute__(self,attr):
		if attr == "__class__":
			return type(self)
		
		actual = super(CommandManaged,self).__getattribute__(attr)
		
		if not callable(actual) or (not actual.__doc__) or (not "undo : " in actual.__doc__):
			return actual
		else:
			return CommandManagerFunctionCurry(self.wrapperFunction,actual)

	#_____________________________________________________________________
	
	def wrapperFunction(self,func,*args,**kwargs):
		out = func(*args,**kwargs)
		d = func.__doc__
		
		undo = d[d.find("undo : ") + 7:].split("\n")[0]
		cmd = undo % makeDict(func.im_self)
		
		obj = ""
		if type(self) == Project.Project:
			obj = "P"
		elif type(self) == Project.Instrument:
			obj = "I%d"%self.id
		elif type(self) == Project.Event:
			obj = "E%d"%self.id
		print "LOG COMMAND: ",obj, cmd
		Project.GlobalProjectObject.AppendToCurrentStack("%s %s" % (obj, cmd))
		
		return out

	#_____________________________________________________________________

#=========================================================================

class makeDict(dict):
	
	#_____________________________________________________________________
	
	def __init__(self,obj):
		self.obj = obj
		
	#_____________________________________________________________________
		
	def __getitem__(self,item):
		return getattr(self.obj,item)
	
	#_____________________________________________________________________

#=========================================================================
	
class CommandManagerFunctionCurry:
	
	#_____________________________________________________________________
	
	def __init__(self, fun, *args, **kwargs):
		self.fun = fun
		self.pending = args[:]
		self.kwargs = kwargs.copy()

	#_____________________________________________________________________

	def __call__(self, *args, **kwargs):
		if kwargs and self.kwargs:
			kw = self.kwargs.copy()
			kw.update(kwargs)
		else:
			kw = kwargs or self.kwargs

		return self.fun(*(self.pending + args), **kw)
	
	#_____________________________________________________________________

#=========================================================================