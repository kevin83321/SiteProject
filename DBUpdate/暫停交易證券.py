
from modules import crawl_json_data
from datetime import datetime, timedelta
import os

# 取得此py檔路徑
path = os.path.dirname(os.path.abspath(__file__))
if not os.path.isdir(path): 
    path = os.getcwd()

# Prepare for edit PDF
from reportlab.platypus import Table, SimpleDocTemplate, Paragraph,TableStyle,PageBreak
from reportlab.lib.enums import TA_JUSTIFY,TA_LEFT,TA_CENTER,TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from platform import system
arial_path = os.path.join(path,'Arial Unicode.ttf')
assert os.path.exists(arial_path)

def transforToPDF(datas, csvpath, filename):
    td = datetime.today()
    arial = TTFont("Arial", arial_path) # <--- This is where it fails
    pdfmetrics.registerFont(arial)
    sampleStyle = getSampleStyleSheet()
    sampleStyle.add(ParagraphStyle(fontName='Arial', name='Arial', leading=20, fontSize=12))

    maxr = 30
    # dfPartition = df.shape[0] // maxr + 1 # 將資料一最大可容納長度切割

    doc = SimpleDocTemplate(os.path.join(os.path.dirname(csvpath), f'{td.strftime("%Y-%m-%d")}_{filename}.pdf'),pagesize=(A4[1],A4[0]),topMargin = 10,bottomMargin = 10, encoding='utf-8-sig')
    sty= ParagraphStyle(name='Heading1',
                        parent=sampleStyle['Normal'],
                        fontName = 'Arial',
                        fontSize=18,
                        leading=22,
                        spaceAfter=6,
                        alignment=TA_CENTER,
                        alias='h1')
    para = Paragraph(f'{td.strftime("%Y-%m-%d")} {filename}', sty)
    para_conti = Paragraph(f'{td.strftime("%Y-%m-%d")} {filename} (續)', sty)
    flowable = [para]
    colWidth = [1.6 * cm] * df.shape[1]
    colWidth[0] = 4.2 * cm
    colWidth[-1] = 2.8 * cm
    cols = datas.pop(0)
    for i in range(dfPartition):
        style_list =[
            ('ALIGN',(0,0),(-1,-1),'CENTER'),
            ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
            ('GRID',(0,0), (-1,-1),1,colors.black),
            ('GRIDSIZE', (0,0), (-1,-1), 1),
            ('FONTSIZE',(0,0),(-1,-1),10),
            ('FONT', (0,0), (-1,-1), 'Arial'), # (sc, sr), (ec, er)
            ('BOTTOMPADDING',(0,0),(-1,-1),2),
            ('TOPPADDING',(0,0),(-1,-1),2),
            ('COLWIDTHS', (1,1), (1,-1), 50)
            ]
        data = [cols]
        while 1:
            data.append(datas.pop(0))
            if len(data) == 31:
                t = Table(data, repeatCols=Partition.shape[1], repeatRows=Partition.shape[0], colWidths=colWidth)
                t.setStyle(TableStyle(style_list))
        flowable.extend([t, PageBreak()])        
            
        
        
        if i < dfPartition -1:
            flowable.append(para_conti)
    doc.build(flowable)
    return filename, os.path.join(os.path.dirname(csvpath), f'{td.strftime("%Y-%m-%d")}_{filename}.pdf')

def StopTradeTWSE(date:datetime = datetime.today()):
    if date <= date.replace(hour=12, minute=0, second=0):
        date -= timedelta(1)
    dateStr = date.strftime('%Y%m%d')
    # dateStr = '20210316'
    url = f'https://www.twse.com.tw/exchangeReport/TWTAWU?response=json&startDate={dateStr}&endDate={dateStr}&stockNo=&querytype=3&selectType=&_=1616002611610'
    datas = crawl_json_data(url)
    if '抱歉' in datas['stat']:
        return
    print(datas)
    cols = datas['fields'][1:]
    data = datas['data']
    final_data = [dict((k, v) for k, v in zip(cols, temps[1:])) for temps in data]
    print(final_data)
    
if __name__ == '__main__':
    StopTradeTWSE()