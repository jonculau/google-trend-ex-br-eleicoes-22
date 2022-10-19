import math
from pickletools import uint8
from pytrends.request import TrendReq
from pandas import DataFrame
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import ipywidgets as widgets
from IPython.display import Markdown, display
def plotComparison(dataFrame:DataFrame, cols:uint8, showValues=False, Incerteza=False, ylin=[]):
    plt.figure(figsize=(20,5))
    Patch = []
    if (len(ylin)>0):
        plt.axes().set_ylim(ylin)
    for col in dataFrame.columns[0:cols]:
        color = 'red' if col == dataFrame.columns[0] else 'blue' if col == dataFrame.columns[1] else 'orange'
        Patch.append(mpatches.Patch(color=color, label=col))
        if Incerteza:
            for i in range(len(dataFrame[col])):
                plt.plot(dataFrame[col][i:i+2], label=col, color=color, linewidth=dataFrame['Incerteza'][i]*2)
        else:
            plt.plot(dataFrame[col], label=col, color=color)
    plt.legend(handles=Patch)
    if showValues:
        for index, row in dataFrame.iterrows():
            if index.minute == 0 and index.hour == 0 and index.second == 0 and index.microsecond == 0:
                for col in dataFrame.columns[0:cols]:
                    plt.text(index, row[col], "{:.1f}".format(row[col]))
                

def run(kw_list, gprop):
# Palavras-chave
    conn = TrendReq(hl='pt-BR', tz=360,  requests_args={'verify':False}) # Conexão com o Google Trends
    req = conn.get_historical_interest(kw_list, year_start=2022, month_start=10, day_start=3, hour_start=0, year_end=2022, month_end=10, day_end=30, hour_end=0, geo='BR', gprop=gprop) 
    display(Markdown("### Dados Lidos do Google Trends"))
    plotComparison(req, 3)
    
    # Acumulado
    accum = []
    idArr = []
    for index,row in req.iterrows():
        idArr.append(index)
        accum.append({})
        for col in kw_list:
            accum[-1][col] = row[col] + accum[-2][col] if len(accum)>1 else row[col] 
    dataFrame = DataFrame(accum,index=idArr)
    print(dataFrame.columns)
    for col in dataFrame.columns[0:len(kw_list)]:
        dataFrame[col] = dataFrame[col].apply(lambda x: math.log(x))
    display(Markdown("## Dados Acumulados (Escala Log)"))
    plotComparison(dataFrame, 2)
    
    # Embate Lula x Bolsonaro
    accumPercent = []
    for x in accum:
        accumPercent.append({})
        total = (math.fsum(x[v] for v in kw_list[0:2])) 
        for col in kw_list[0:2]:
            accumPercent[-1][col] = (x[col]/total)*100
        accumPercent[-1]["Incerteza"] = x[kw_list[2]] / (x[kw_list[2]]+total) * 100
    dataFrame = DataFrame(accumPercent,index=idArr)
    print(Markdown("## Acumulado (Percentual)\n(Espessura da linha determinada pelas pesquisas envolvendo os dois simultaneamente multiplicado por 2"))
    plotComparison(dataFrame, 2, True, True , ylin=[0,100])