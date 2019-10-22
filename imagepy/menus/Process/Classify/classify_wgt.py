import wx, joblib, os, shutil, os.path as osp
from glob import glob
from imagepy.core.manager import RoiManager, ImageManager, ReaderManager, ViewerManager
from . import classify_plgs as manager
from .predict_plg import Plugin as FCL
from imagepy import IPy

ReaderManager.add('fcl', lambda x:x, 'fcl')
ViewerManager.add('fcl', lambda x,n:wx.CallAfter(FCL(path=x).start))

class Plugin( wx.Panel ):
	title = 'Feature Classify Panel'

	def __init__( self, parent ):
		wx.Panel.__init__ ( self, parent, id = wx.ID_ANY, pos = wx.DefaultPosition, size = wx.Size(256, 256), style = wx.TAB_TRAVERSAL )
		
		sizer = wx.BoxSizer( wx.HORIZONTAL )
		
		sizer_btns = wx.BoxSizer( wx.VERTICAL )
		
		self.btn_save = wx.Button( self, wx.ID_ANY, u"Save", wx.DefaultPosition, wx.DefaultSize, 0 )
		sizer_btns.Add( self.btn_save, 0, wx.ALL, 5 )

		self.btn_saveas = wx.Button( self, wx.ID_ANY, u"Save As", wx.DefaultPosition, wx.DefaultSize, 0 )
		sizer_btns.Add( self.btn_saveas, 0, wx.ALL, 5 )

		self.btn_export = wx.Button( self, wx.ID_ANY, u"Export", wx.DefaultPosition, wx.DefaultSize, 0 )
		sizer_btns.Add( self.btn_export, 0, wx.ALL, 5 )
		
		self.btn_run = wx.Button( self, wx.ID_ANY, u"Run", wx.DefaultPosition, wx.DefaultSize, 0 )
		sizer_btns.Add( self.btn_run, 0, wx.ALL, 5 )
		
		self.btn_rename = wx.Button( self, wx.ID_ANY, u"Rename", wx.DefaultPosition, wx.DefaultSize, 0 )
		sizer_btns.Add( self.btn_rename, 0, wx.ALL, 5 )
		
		self.btn_remove = wx.Button( self, wx.ID_ANY, u"Remove", wx.DefaultPosition, wx.DefaultSize, 0 )
		sizer_btns.Add( self.btn_remove, 0, wx.ALL, 5 )
		
		sizer.Add( sizer_btns, 0, wx.EXPAND, 5 )
		
		sizer_list = wx.BoxSizer( wx.VERTICAL )
		
		self.lst_model = wx.ListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, ['a', 'b'], 0 )
		self.lst_model.SetFont( wx.Font( 12, 70, 90, 90, False, wx.EmptyString ) )
		sizer_list.Add( self.lst_model, 1, wx.ALL|wx.EXPAND, 5 )
		
		sizer.Add( sizer_list, 1, wx.EXPAND, 5 )
		self.models = []
		self.AddEvent()
		self.LoadModel()
		
		self.SetSizer( sizer )
		self.Layout()

	def LoadModel(self):
		fs = glob(osp.join(IPy.root_dir, 'data/ilastik/*.fcl'))
		self.models = [osp.split(i)[1] for i in fs]
		self.lst_model.SetItems(self.models)

	def AddEvent(self):
		self.btn_save.Bind(wx.EVT_BUTTON, self.on_save)
		self.btn_saveas.Bind(wx.EVT_BUTTON, self.on_saveas)
		self.btn_export.Bind(wx.EVT_BUTTON, self.on_export)
		self.btn_rename.Bind(wx.EVT_BUTTON, self.on_rename)
		self.btn_remove.Bind(wx.EVT_BUTTON, self.on_remove)
		self.btn_run.Bind(wx.EVT_BUTTON, self.on_run)


	def on_save(self, event):
		if manager.model_para is None:
		 	return IPy.alert('you must train your model first!')
		para = {'name':'New Model'}
		if not IPy.get_para('name', [(str, 'name', 'model', 'name')], para): return
		if not osp.exists(osp.join(IPy.root_dir, 'data/ilastik')):
			os.mkdir(osp.join(IPy.root_dir, 'data/ilastik'))
		joblib.dump( manager.model_para, osp.join(IPy.root_dir, 'data/ilastik/%s.fcl'%para['name']))
		self.LoadModel()

	def on_saveas(self, event):
		if manager.model_para is None:
		 	return IPy.alert('you must train your model first!')
		para = {'path':''}
		filt = '|'.join(['%s files (*.%s)|*.%s'%('FCL', 'fcl', 'fcl')])
		if not IPy.getpath('Save..', filt, 'save', para): return
		joblib.dump( manager.model_para, para['path'])

	def on_export(self, event):
		idx = self.lst_model.GetSelection()
		if idx==-1: return IPy.alert('no model selected!')
		para = {'path':''}
		filt = '|'.join(['%s files (*.%s)|*.%s'%('FCL', 'fcl', 'fcl')])
		if not IPy.getpath('Save..', filt, 'save', para): return
		oldname = osp.join(IPy.root_dir, 'data/ilastik/%s'%self.lst_model.GetStringSelection())
		print(para['path'])
		shutil.copyfile(oldname, para['path'])
		self.LoadModel()

	def on_rename(self, event):
		idx = self.lst_model.GetSelection()
		if idx==-1: return IPy.alert('no model selected!')
		para = {'name':'New Model'}
		if not IPy.get_para('name', [(str, 'name', 'model', 'name')], para): return
		oldname = osp.join(IPy.root_dir, 'data/ilastik/%s'%self.lst_model.GetStringSelection())
		os.rename(oldname, osp.join(IPy.root_dir, 'data/ilastik/%s.fcl'%para['name']))
		self.LoadModel()

	def on_remove(self, event):
		idx = self.lst_model.GetSelection()
		if idx==-1: return IPy.alert('no model selected!')
		os.remove(osp.join(IPy.root_dir, 'data/ilastik/%s'%self.lst_model.GetStringSelection()))
		self.LoadModel()

	def on_run(self, event):
		idx = self.lst_model.GetSelection()
		if idx==-1: return IPy.alert('no model selected!')
		FCL(path=self.lst_model.GetStringSelection()).start()
		
	def __del__( self ):
		pass
	