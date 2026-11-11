import json
s=open('tpl.html').read(); q=json.load(open('quran.json'))
s=s.replace('${QURAN}',json.dumps(q,ensure_ascii=False))
a="const v=Math.min(sc.fi?P(t,sc.s,sc.fi):(t>=sc.s?1:0),1-(sc.fo?P(t,sc.e-sc.fo,sc.fo):(t>=sc.e?1:0)));"
b="const v=Math.min(sc.fi?P(t,sc.s,sc.fi):(t>=sc.s?1:0),1-(sc.fo?P(t,sc.e,sc.fo):(t>=sc.e?1:0)));"
assert a in s; s=s.replace(a,b)
s=s.replace("fi:o.fi===undefined?0.45:o.fi,fo:o.fo===undefined?0.45:o.fo","fi:o.fi===undefined?0.3:o.fi,fo:o.fo===undefined?0.3:o.fo")
open('index.html','w').write(s); print('built',len(s))
