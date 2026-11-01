#!/usr/bin/env python3
"""Verify all newly reviewed pages at three widths, including scrolled tables."""
from pathlib import Path
import json,math,time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from PIL import Image,ImageDraw

ROOT=Path('visual-review/remaining23-indonesian');ROOT.mkdir(parents=True,exist_ok=True)
audit=json.loads(Path('audit-reports/indonesian-remaining23-release-2026-11-02.json').read_text())
opts=Options()
for arg in ['--headless=new','--no-sandbox','--disable-dev-shm-usage','--hide-scrollbars']:opts.add_argument(arg)
browser=webdriver.Chrome(options=opts);report=[]
try:
    for name,width,height in [('desktop',1440,1100),('mobile',390,844),('narrow',360,800)]:
        browser.execute_cdp_cmd('Emulation.setDeviceMetricsOverride',{'width':width,'height':height,'deviceScaleFactor':1,'mobile':False})
        folder=ROOT/name;folder.mkdir(exist_ok=True)
        for r in audit['new_articles']:
            browser.get('http://127.0.0.1:4173'+r['url'].split('ahmedalhafiz.com',1)[1])
            WebDriverWait(browser,20).until(lambda b:b.execute_script('return document.readyState')=='complete')
            browser.execute_async_script('const done=arguments[0];document.fonts.ready.then(()=>done());')
            WebDriverWait(browser,15).until(lambda b:b.execute_script('return [...document.images].every(i=>i.complete&&i.naturalWidth>0)'))
            info=browser.execute_script('''
                const h=document.querySelector('h1'),b=document.querySelector('.reading-body'),rect=h.getBoundingClientRect();
                return {width:innerWidth,documentWidth:document.documentElement.scrollWidth,h1:document.querySelectorAll('h1').length,title:h.textContent.trim(),dir:getComputedStyle(b).direction,bodyText:b.textContent.length,headingLeft:rect.left,headingRight:rect.right,unloaded:[...document.images].filter(i=>!i.complete||!i.naturalWidth).length,tables:b.querySelectorAll('table').length,cells:b.querySelectorAll('th,td').length,quoteFont:document.fonts.check('20px "Amiri Quran"')};
            ''')
            assert info['documentWidth']<=width+1,(r['key'],name,info)
            assert info['h1']==1 and info['title']==r['title'] and info['dir']=='ltr'
            assert info['bodyText']>1500 and info['headingLeft']>=0 and info['headingRight']<=width+1
            assert info['unloaded']==0 and info['quoteFont']
            assert (info['tables'],info['cells'])==(r['tables'],r['table_cells'])
            bad=browser.execute_script('''return [...document.querySelectorAll('.reading-body h1,.reading-body h2,.reading-body h3,.reading-body img,.table-scroll')].filter(e=>!e.closest('table')).map(e=>({tag:e.tagName,left:e.getBoundingClientRect().left,right:e.getBoundingClientRect().right})).filter(r=>r.left < -1 || r.right > innerWidth+1)''')
            assert not bad,(r['key'],name,bad)
            browser.save_screenshot(str(folder/f"{r['number']:02}-opening.png"))
            for label,selector in [('table','.reading-body .table-scroll'),('quote','.reading-body [lang="ar"]')]:
                es=browser.find_elements(By.CSS_SELECTOR,selector)
                if es:
                    browser.execute_script("arguments[0].scrollIntoView({block:'center'})",es[0]);time.sleep(.04)
                    browser.save_screenshot(str(folder/f"{r['number']:02}-{label}.png"))
            browser.execute_script('scrollTo(0,document.body.scrollHeight)');time.sleep(.04)
            browser.save_screenshot(str(folder/f"{r['number']:02}-end.png"))
            report.append({'key':r['key'],'viewport':name,'pass':True,**info})
        print(f'Remaining23: {name} passed for all23 pages',flush=True)
finally:browser.quit()
for name,cols in [('desktop',3),('mobile',5),('narrow',5)]:
    for kind in ['opening','table','quote','end']:
        files=sorted((ROOT/name).glob('*-'+kind+'.png'))
        if not files:continue
        thumbw=400 if name=='desktop' else 216
        sample=Image.open(files[0]);thumbh=round(sample.height*thumbw/sample.width)
        canvas=Image.new('RGB',(cols*thumbw,math.ceil(len(files)/cols)*(thumbh+25)),'white');draw=ImageDraw.Draw(canvas)
        for i,f in enumerate(files):
            im=Image.open(f).convert('RGB');im.thumbnail((thumbw,thumbh));x=(i%cols)*thumbw;y=(i//cols)*(thumbh+25);canvas.paste(im,(x,y+25));draw.text((x+5,y+5),f.stem,fill='black')
        canvas.save(ROOT/f'contact-{name}-{kind}.png')
(ROOT/'report.json').write_text(json.dumps({'pass':True,'articles':23,'viewports':3,'checks':report},indent=2))
print('Remaining23 browser gate passed:23 full articles at3 widths; headings, tables, quote fonts, images and geometry verified.')
