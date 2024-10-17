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
        sqlData:list = cur.execute("SELECT HitMap FROM HitDelayHistory").fetchall();
        # init hit map: [-149, -0], [+0, +250]
        self.hitMapPositive:list[int] = [0]*150;
        self.hitMapNegative:list[int] = [0]*251;
        # init PDF(Probability Density Function)
        self.summation:int = 0; # All Hit
        self.summationEx:int = 0; # Blue Exact & Cyan Exact
        self.summationEX:int = 0; # Only Cyan Exact
        # summation SYNC.Rate: [Cyan Exact, Blue Exact, Great, Right, Miss]
        # self.SYNC_Rate:list[int] = [0] * 5;
        # summation Accurate SYNC.Rate:
        #   [¡À5ms, ¡À10ms, ¡À20ms, ¡À45ms, Blue Exact, Great, Right, Miss]
        self.Accurate_Sync_Rate:list[int] = [0]*8;
        self.LoadHitMap();

        # init chart axis
        self.xAxis:list[int] = [i for i in range(-150,251,1)];
        self.yAxis:list[int] = self.hitMapPositive + self.hitMapNegative;


    def LoadHitMap(self) -> None:
        pass