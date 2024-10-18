import json
import numpy
import matplotlib.gridspec as gridspec
import matplotlib.patches as patches
import matplotlib.pyplot as plt
#import matplotlib.widgets as widgets
import sqlite3 as sql

from matplotlib.pyplot import MultipleLocator
from matplotlib.widgets import Button, Slider

class AllHitAnalyze(object):
    def __init__(self) -> None:
        super(AllHitAnalyze,self).__init__();
        # sql init and select data
        db:sql.Connection = sql.connect("./musync_data/HitDelayHistory_v2.db");
        cur:sql.Cursor = db.cursor();
        self.sqlData:list[list[string]] = cur.execute("SELECT HitMap FROM HitDelayHistory").fetchall();
        # load config
		with open('./musync_data/ExtraFunction.cfg', 'r',encoding='utf8') as confFile:
			config:dict = json.load(confFile)
        # init PDF(Probability Density Function)
        self.summation:int = 0; # All Hit
        self.summationEx:int = 0; # Blue Exact & Cyan Exact
        self.summationEX:int = 0; # Only Cyan Exact
        # summation SYNC.Rate: [Cyan Exact, Blue Exact, Great, Right, Miss]
        # self.SYNC_Rate:list[int] = [0] * 5;
        # summation Accurate SYNC.Rate:
        #   [¡À5ms, ¡À10ms, ¡À20ms, ¡À45ms, Blue Exact, Great, Right, Miss]
        self.Accurate_Sync_Rate:list[int] = [0]*8;
        # init hit map: [-149, -0], [+0, +250]
        self.hitMapPositive:list[int] = [0]*150;
        self.hitMapNegative:list[int] = [0]*251;
        # init chart axis
        self.xAxis:list[int] = [i for i in range(-150,251,1)];
        self.yAxis:list[int] = self.hitMapPositive + self.hitMapNegative;
        self.LoadHitMap(0);
        # avg:Average , var:Variance ,std: Standard Deviation
		self.avg:float = sum([ids[0]*ids[1]/self.summation for ids in zip(self.xAxis,self.yAxis)]);
		self.var:float = sum([(ids[1]/self.summation)*((ids[0] - self.avg) ** 2) for ids in zip(self.xAxis,self.yAxis)]);
		self.std:float = self.var**0.5;
		print(f'All: avg:{self.avg:.4}, var:{self.var:.4}, std:{self.std:.4} sum:{self.summation}');
        self.avgEx:float = sum([ids[0]*ids[1]/self.summationEx for ids in zip(self.xAxis[61:240],self.yAxis[61:240])]);
		self.varEx:float = sum([(ids[1]/self.summationEx)*((ids[0] - self.avgEx) ** 2) for ids in zip(self.xAxis[61:240],self.yAxis[61:240])]);
		self.stdEx:float = self.varEx**0.5;
		print(f'All Exact: avg:{self.avgEx:.4}, var:{self.varEx:.4}, std:{self.stdEx:.4} sum:{self.summationEx}');
        if config['EnablePDFofCyanExact']:
			self.avgEX:float = sum([ids[0]*ids[1]/self.summationEX for ids in zip(self.xAxis[106:195],self.yAxis[106:195])]);
			self.varEX:float = sum([(ids[1]/self.summationEX)*((ids[0] - self.avgEX) ** 2) for ids in zip(self.xAxis[106:195],self.yAxis[106:195])]);
			self.stdEX:float = self.varEX**0.5;
			self.enablePDFofCyanExact:bool = True;
			print(f'cyan Exact: avg:{self.avgEX:.4}, var:{self.varEX:.4}, std:{self.stdEX:.4} sum:{self.summationEX}');
		else:
			self.enablePDFofCyanExact:bool = False;


    def LoadHitMap(self,limit:int) -> None:
        for ids in 