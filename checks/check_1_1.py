"""Contrôles internes de fixtures 1.1. Ce script ne constitue pas un validateur général."""
from pathlib import Path
from urllib.parse import urljoin,urlparse,unquote
from datetime import datetime,timezone
from decimal import Decimal, ROUND_FLOOR
from email.utils import parsedate_to_datetime
from PIL import Image
import re,json,calendar,xml.etree.ElementTree as E

ROOT=Path(__file__).resolve().parents[1]
NOW='2026-10-08T12:00:00Z'
mapping=json.loads((ROOT/'mapping.json').read_text())['origins']
schemas={k:json.loads((ROOT/'schemas'/f'{k}.schema.json').read_text()) for k in ['publisher','series']}
def load(path):
    def pairs(values):
        d={}
        for k,v in values:
            if k in d:raise ValueError('CF_DUPLICATE_KEY')
            d[k]=v
        return d
    return json.loads((ROOT/path).read_text(),object_pairs_hook=pairs,parse_constant=lambda x:(_ for _ in ()).throw(ValueError('CF_JSON')))
def pathurl(url,overrides=None):
    if url in (overrides or {}):return ROOT/overrides[url]
    for m in mapping:
        if url.startswith(m['base_url']):return ROOT/m['directory']/unquote(urlparse(url[len(m['base_url']):]).path)
    raise ValueError('Unmapped '+url)
def getdoc(url,overrides=None):return load(pathurl(url,overrides).relative_to(ROOT))
def instant(s):
    m=re.fullmatch(r'(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:[0-5]\d)(\.\d+)?(Z|[+-]\d{2}:\d{2})',s or '')
    if not m or m[4]=='-00:00':raise ValueError('date')
    t=datetime.fromisoformat(m[1]+'T'+m[2]+m[4].replace('Z','+00:00'))
    return Decimal(calendar.timegm(t.astimezone(timezone.utc).utctimetuple()))+Decimal(m[3] or '0')

# Évaluateur limité aux mots-clés effectivement utilisés par nos deux schémas.
# Il contrôle les exemples hors ligne, pas la conformité générale d'un moteur JSON Schema.
def sch(data,s,root,path='$'):
    if s is True:return []
    if s is False:return [(path,'false')]
    if '$ref'in s:return sch(data,root['$defs'][s['$ref'].rsplit('/',1)[-1]],root,path)
    out=[]
    typ=s.get('type')
    valid={'object':lambda x:isinstance(x,dict),'array':lambda x:isinstance(x,list),'string':lambda x:isinstance(x,str),'number':lambda x:isinstance(x,(int,float)) and not isinstance(x,bool),'integer':lambda x:isinstance(x,int) and not isinstance(x,bool)}
    if typ and not valid[typ](data):return [(path,'type')]
    if 'const'in s and data!=s['const']:out.append((path,'const'))
    if 'enum'in s and data not in s['enum']:out.append((path,'enum'))
    if isinstance(data,str):
        if 'pattern'in s and not re.search(s['pattern'],data):out.append((path,'pattern'))
        if len(data)<s.get('minLength',0):out.append((path,'minLength'))
    if isinstance(data,dict):
        for key in s.get('required',[]):
            if key not in data:out.append((path+'.'+key,'required'))
        for k,v in data.items():
            if 'propertyNames'in s:out+=sch(k,s['propertyNames'],root,path)
            if k in s.get('properties',{}):out+=sch(v,s['properties'][k],root,path+'.'+k)
            elif isinstance(s.get('additionalProperties'),dict):out+=sch(v,s['additionalProperties'],root,path+'.'+k)
            elif s.get('additionalProperties') is False:out.append((path+'.'+k,'additionalProperties'))
    if isinstance(data,list):
        if len(data)<s.get('minItems',0):out.append((path,'minItems'))
        if 'maxItems'in s and len(data)>s['maxItems']:out.append((path,'maxItems'))
        if 'items'in s:
            for i,x in enumerate(data):out+=sch(x,s['items'],root,path+f'[{i}]')
    for branch in s.get('allOf',[]):out+=sch(data,branch,root,path)
    if 'not'in s and not sch(data,s['not'],root,path):out.append((path,'not'))
    if 'if'in s:
        branch='then' if not sch(data,s['if'],root,path) else 'else'
        if branch in s:out+=sch(data,s[branch],root,path)
    return out

def validate(d,base,overrides=None,parent=None,before=None,relations=True):
    codes=set();details=[]
    def err(c,x=''):codes.add(c);details.append((c,x))
    if not isinstance(d,dict):return {'CF_TYPE'},[]
    kind='publisher' if isinstance(d.get('series'),list) else 'series'
    schema = schemas[kind] if d.get('version') == '1.1' else json.loads((ROOT/'reference-1.0/schemas'/f'{kind}.schema.json').read_text())
    se=sch(d,schema,schema)
    for path,keyword in se:
        if keyword=='type':err('CF_TYPE',path)
        elif keyword=='required':err('CF_REQUIRED',path)
        elif keyword in ['enum','const','not']:err('CF_ENUM',path)
        elif keyword=='pattern' and path.endswith('.id'):err('CF_ID',path)
        elif keyword=='pattern' and (path.endswith('_at') or path.endswith('.at')):err('CF_DATE',path)
        else:err('CF_STRUCTURE',path)
    if 'version'in d and not isinstance(d['version'],str):err('CF_TYPE','version')
    def date(s):
        try:return instant(s)
        except Exception:err('CF_DATE',str(s));return None
    def newer(parentdate,childdate):
        a=date(parentdate);b=date(childdate)
        if a is not None and b is not None and a<b:err('CF_TIME_ORDER',str((parentdate,childdate)))
    def urlcheck(v,feed=False):
        if not isinstance(v,str) or not v or re.search(r'[\s\\\x00-\x1f\x7f]',v):err('CF_URL',str(v));return None
        if re.search(r'%(?![0-9A-Fa-f]{2})',v):err('CF_URL',v);return None
        result=urljoin(base,v);p=urlparse(result)
        if p.scheme not in ('https','http') or not p.hostname or p.username or p.password or (feed and p.fragment):err('CF_URL',v);return None
        return result
    def imagecheck(src):
        # Référence URL seulement : les nouveaux médias ne sont pas déployés.
        urlcheck(src)
    def textwalk(x):
        if isinstance(x,dict):
            for k,v in x.items():
                if k=='extensions':continue
                if k in ('publish_at','updated_at') or k=='at':date(v)
                if k in ('src','url','feed','rss','moved_to','thumbnail','avatar','banner','cover'):urlcheck(v,k in ('feed','moved_to'))
                textwalk(v)
        elif isinstance(x,list):
            for y in x:textwalk(y)
    textwalk(d)
    if kind=='publisher':
        p=d.get('publisher',{})
        for v in p.get('images',{}).values():
            if isinstance(v,str):imagecheck(v)
        series_ids=[x.get('id') for x in d.get('series',[])]
        if len(series_ids)!=len(set(series_ids)):err('CF_DUPLICATE_ID')
        if p.get('status')=='moved':
            if 'moved_to' not in p:err('CF_REQUIRED','publisher.moved_to')
            elif relations:
                current=d;currentbase=base;seen={base}
                for _ in range(20):
                    target=urljoin(currentbase,current['publisher']['moved_to'])
                    if target in seen:err('CF_MOVE_LOOP');break
                    seen.add(target)
                    try:dest=getdoc(target,overrides)
                    except Exception:err('NET_HTTP',target);break
                    if dest.get('publisher',{}).get('id')!=p.get('id'):err('CF_MOVE_ID');break
                    if dest['publisher'].get('status')!='moved':break
                    current=dest;currentbase=target
        elif relations:
            for ent in d.get('series',[]):
                newer(d.get('updated_at'),ent.get('updated_at'))
                if ent.get('thumbnail'):imagecheck(ent['thumbnail'])
                try:child=getdoc(urljoin(base,ent['feed']),overrides)
                except Exception:err('NET_HTTP',ent.get('feed'));continue
                if child.get('publisher',{}).get('id')!=p.get('id'):err('CF_PARENT_ID')
                if child.get('series',{}).get('id')!=ent.get('id'):err('CF_SERIES_ID')
                if child.get('updated_at')!=ent.get('updated_at'):err('CF_INDEX_DATE')
        return codes,details
    meta=d.get('series',{})
    for v in meta.get('images',{}).values():
        if isinstance(v,str):imagecheck(v)
    ids=[]
    for c in d.get('channels',[]):
        ids.append(c.get('id'));newer(d.get('updated_at'),c.get('updated_at'))
        default=c.get('access',{}).get('mode')
        if d.get('version')=='1.1' and 'reading_direction' in c and c.get('type')!='pages':err('CF_FIELD_SCOPE','reading_direction')
        if 'rss'in c and (default!='public' or not c.get('url')):err('CF_RSS_POLICY')
        for p in c.get('publications',[]):
            ids.append(p.get('id'));newer(c.get('updated_at'),p.get('updated_at'))
            if 'thumbnail'in p:imagecheck(p['thumbnail'])
            if 'update_notice'in p:newer(p.get('updated_at'),p['update_notice'].get('at'))
            if p.get('status')!='withdrawn':
                acc=p.get('access',{}).get('mode',default)
                if default=='mixed' and 'access'not in p:err('CF_MIXED_ACCESS')
                resources=p.get('resources')
                if acc=='public' and not resources:err('CF_RESOURCE_COUNT')
                if resources is not None and (len(resources)==0 or c.get('type') in ('strip','square') and len(resources)!=1):err('CF_RESOURCE_COUNT')
                try:eligible=instant(p['publish_at'])<=instant(NOW) and acc=='public'
                except Exception:eligible=False
                if c.get('rss') and eligible and c.get('status')!='withdrawn' and meta.get('status')!='withdrawn' and not p.get('url'):err('CF_RSS_POLICY')
            for res in p.get('resources',[]):
                if isinstance(res,dict) and 'src' in res:imagecheck(res['src'])
    if len(ids)!=len(set(ids)):err('CF_DUPLICATE_ID')
    if relations and d.get('publisher',{}).get('feed'):
        try:pd=parent or getdoc(urljoin(base,d['publisher']['feed']),overrides)
        except Exception:pd=None;err('NET_HTTP')
        if pd:
            if pd.get('publisher',{}).get('id')!=d['publisher'].get('id'):err('CF_PARENT_ID')
            entries=[x for x in pd.get('series',[]) if x.get('id')==meta.get('id')]
            if not entries:err('CF_SERIES_ID')
            elif entries[0].get('updated_at')!=d.get('updated_at'):err('CF_INDEX_DATE')
    if before:
        oldc={c['id']:c for c in before['channels']}
        oldp={p['id']:(c,p) for c in before['channels'] for p in c['publications']}
        for c in d['channels']:
            if c['id']in oldc and c['type']!=oldc[c['id']]['type']:err('CF_IMMUTABLE')
            for p in c['publications']:
                if p['id']not in oldp:continue
                oc,op=oldp[p['id']]
                if oc['id']!=c['id']:err('CF_IMMUTABLE')
                if op['status']=='withdrawn' and p['status']!='withdrawn':err('CF_REACTIVATION')
                if op['status']!='withdrawn' and p['status']!='withdrawn' and instant(op['publish_at'])<=instant(NOW) and instant(p['publish_at'])!=instant(op['publish_at']):err('CF_IMMUTABLE')
                if p!=op and instant(p['updated_at'])<=instant(op['updated_at']):err('CF_TIME_ORDER')
    return codes,details

def rsscheck(path,d,c,base):
    out=set();raw=(ROOT/path).read_text()
    if '<!DOCTYPE'in raw or '<!ENTITY'in raw:out.add('CF_RSS_XML')
    try:r=E.fromstring(raw)
    except Exception:return {'CF_RSS_XML'}
    if r.tag!='rss' or r.get('version')!='2.0' or len(r.findall('channel'))!=1:return {'CF_RSS_XML'}
    ch=r.find('channel')
    for k in ['title','link','description']:
        if not ch.findtext(k):out.add('CF_RSS_XML')
    if ch.findtext('link')!=urljoin(base,c['url']):out.add('CF_RSS_XML')
    eligible={p['id']:p for p in c['publications'] if p['status']!='withdrawn' and instant(p['publish_at'])<=instant(NOW) and p.get('access',c['access'])['mode']=='public'}
    if c.get('status')=='withdrawn' or d['series'].get('status')=='withdrawn':eligible={}
    seen=[]
    for it in ch.findall('item'):
        guid=it.find('guid');pid=it.findtext('guid');seen.append(pid)
        if guid is None or guid.get('isPermaLink')!='false':out.add('CF_RSS_XML')
        if pid not in eligible:out.add('CF_RSS_POLICY');continue
        p=eligible[pid]
        if not it.findtext('title') or it.findtext('link')!=urljoin(base,p['url']):out.add('CF_RSS_XML')
        try:
            when=parsedate_to_datetime(it.findtext('pubDate')).astimezone(timezone.utc)
            if Decimal(calendar.timegm(when.utctimetuple()))!=instant(p['publish_at']).to_integral_value(rounding=ROUND_FLOOR):out.add('CF_RSS_XML')
        except Exception:out.add('CF_RSS_XML')
    if set(seen)!=set(eligible) or len(seen)!=len(set(seen)):out.add('CF_RSS_POLICY')
    return out


from copy import deepcopy
from hashlib import sha256
from html.parser import HTMLParser

results=[]
def result(name, ok, details=None):
    results.append({'name':name,'passed':bool(ok),'details':details or []})

class Fragment(HTMLParser):
    def __init__(self):
        super().__init__();self.images=[];self.urls=[];self.unsafe=False
    def handle_starttag(self, tag, attrs):
        attrs=dict(attrs)
        if tag not in ('p','a','img'):self.unsafe=True
        if any(k.lower().startswith('on') for k in attrs):self.unsafe=True
        if tag=='img':self.images.append(attrs.get('src'))
        self.urls.extend(v for k,v in attrs.items() if k in ('src','href'))

def profile_rss(path, d, c, base):
    codes=rsscheck(path,d,c,base)
    xml=E.parse(ROOT/path)
    pubs={p['id']:p for p in c['publications']}
    for item in xml.findall('./channel/item'):
        p=pubs.get(item.findtext('guid'))
        if not p or p.get('access',c['access'])['mode']!='public':continue
        desc=item.findtext('description')
        if not desc:codes.add('CF_RSS_XML');continue
        f=Fragment();f.feed(desc)
        if f.unsafe or any(urlparse(u or '').scheme!='https' for u in f.urls):codes.add('CF_RSS_XML')
        if c['type']=='square':
            wanted=[urljoin(base,p['resources'][0]['src'])]
        elif c['type']=='pages':
            wanted=[urljoin(base,p['thumbnail'])] if p.get('thumbnail') else []
        else:continue
        if f.images!=wanted:codes.add('CF_RSS_POLICY')
        if urljoin(base,p.get('url','')) not in f.urls:codes.add('CF_RSS_XML')
    return codes

for kind,s in schemas.items():
    def audit(x):
        if isinstance(x,dict):
            if '$ref' in x:
                assert x['$ref'].startswith('#/$defs/') and x['$ref'].split('/')[-1] in s['$defs']
            if 'pattern' in x:re.compile(x['pattern'])
            for v in x.values():audit(v)
        elif isinstance(x,list):
            for v in x:audit(v)
    audit(s);result('schema-references-internes:'+kind,True)

canonical={}
for path in sorted((ROOT/'examples/atelier').rglob('feed.json')):
    base='https://atelier-demo.example/'+path.relative_to(ROOT/'examples/atelier').as_posix()
    d=load(path.relative_to(ROOT));canonical[base]=d
    codes,details=validate(d,base)
    result('feed-complet:'+path.relative_to(ROOT).as_posix(),not codes,details)
    for c in d.get('channels',[]):
        if 'rss' in c:
            rsspath=pathurl(urljoin(base,c['rss'])).relative_to(ROOT)
            codes=profile_rss(rsspath,d,c,base)
            result('rss:'+rsspath.as_posix(),not codes,sorted(codes))

manifest=load('cases/manifest.json')
for case in manifest['cases']:
    d=load(case['file'])
    if case['schema_valid'] is not None:
        codes,details=validate(d,manifest['base_url'],relations=False)
        success=(not codes) if case['schema_valid'] else case['expected'] in codes
        result('cas:'+case['file'],success,{'expected':case.get('expected','VALID'),'observed':sorted(codes)})
    if 'consumer' in case:
        c=case['consumer'];known=set(c['known_types'])
        # Simulation de la règle de sélection, pas exécution d'un ancien Reader.
        kept=[x['type'] for x in d['channels'] if x['type'] in known]
        isolated=[x['type'] for x in d['channels'] if x['type'] not in known]
        result('regle-consommation-partielle:'+case['file'],kept==c['kept_types'] and isolated==c['isolated_types'],{'kept':kept,'isolated':isolated})

# Les documents de référence sont aussi projetés en mémoire en 1.1 : la
# structure Strip/Webtoon n'acquiert aucune nouvelle exigence obligatoire.
for path in sorted((ROOT/'reference-1.0/demo').rglob('feed.json')):
    d=json.loads(path.read_text());d['version']='1.1'
    kind='publisher' if isinstance(d['series'],list) else 'series'
    errors=sch(d,schemas[kind],schemas[kind])
    result('structure-ancienne-acceptee-en-1-1:'+path.relative_to(ROOT/'reference-1.0').as_posix(),not errors,errors)

mainbase='https://atelier-demo.example/series/quatre-formats/feed.json'
four=canonical[mainbase]
pages=next(c for c in four['channels'] if c['type']=='pages')
square=next(c for c in four['channels'] if c['type']=='square')
webtoon=next(c for c in four['channels'] if c['type']=='webtoon')
result('pages-huit-puis-deux',[len(p['resources']) for p in pages['publications']]==[8,2])
result('webtoon-une-puis-plusieurs-images',[len(p['resources']) for p in webtoon['publications']]==[1,2])
rtl=canonical['https://atelier-demo.example/series/droite-gauche/feed.json']['channels'][0]
order=[r['src'] for r in rtl['publications'][0]['resources']]
result('ordre-rtl-independant-du-nom',rtl['reading_direction']=='rtl' and order==['media/z-premiere.jpg','media/a-deuxieme.jpg'] and order!=sorted(order))
parent=canonical['https://atelier-demo.example/feed.json']
result('versions-parent-enfant-distinctes',parent['version']=='1.0' and four['version']=='1.1' and parent['publisher']['id']==four['publisher']['id'])
parent11=deepcopy(parent);parent11['version']='1.1'
codes,details=validate(parent11,'https://atelier-demo.example/feed.json')
result('publisher-1-1-meme-structure',not codes,details)

before=load('reference-1.0/demo/aube/series/les-lucioles/feed.json')
after=deepcopy(before);after['version']='1.1';after['updated_at']=NOW
target=next(c for c in after['channels'] if c['type']=='strip')
target['type']='square';target['updated_at']=NOW
codes,_=validate(after,'https://aube.example/bd/series/les-lucioles/feed.json',relations=False,before=before)
result('retypage-meme-chn-rejete','CF_IMMUTABLE' in codes,sorted(codes))

for channelmode,override,with_resources,expected in [
    ('public','restricted',False,True),
    ('restricted','public',False,False),
    ('restricted','public',True,True),
    ('mixed','public',True,True),
    ('mixed','restricted',False,True),
    ('mixed',None,True,False),
]:
    d=deepcopy(four);c=d['channels'][3];c.pop('rss',None)
    c['access']['mode']=channelmode;c['publications']=c['publications'][:1];p=c['publications'][0]
    if override:p['access']={'mode':override}
    if not with_resources:p.pop('resources',None)
    codes,details=validate(d,mainbase,relations=False)
    result(f'heritage-pages:{channelmode}:{override}:{with_resources}',(not codes)==expected,sorted(codes))

future=next(p for p in square['publications'] if p['status']=='scheduled')

# RSS invalides dérivés sans média réel : inclusion future/restreinte, image
# Square absente et page de chapitre diffusée à la place d'une miniature.
rsscases=[]
squarepath='examples/atelier/series/quatre-formats/rss/square.xml'
pagespath='examples/atelier/series/quatre-formats/rss/pages.xml'
def xmlcase(name, original, c, change, expected):
    tree=E.parse(ROOT/original);change(tree)
    p=ROOT/'cases/invalid'/f'{name}.xml';tree.write(p,encoding='utf-8',xml_declaration=True)
    codes=profile_rss(p.relative_to(ROOT),four,c,mainbase)
    result('rss-invalide:'+name,expected in codes,sorted(codes))
    rsscases.append({'file':p.relative_to(ROOT).as_posix(),'series':'examples/atelier/series/quatre-formats/feed.json','channel_id':c['id'],'expected':expected})

def replaceguid(tree,pid):tree.find('./channel/item/guid').text=pid
xmlcase('rss-square-futur',squarepath,square,lambda t:replaceguid(t,future['id']),'CF_RSS_POLICY')
restricted=next(p for p in square['publications'] if p.get('access',{}).get('mode')=='restricted')
xmlcase('rss-square-restreint',squarepath,square,lambda t:replaceguid(t,restricted['id']),'CF_RSS_POLICY')
xmlcase('rss-square-image-absente',squarepath,square,lambda t:setattr(t.find('./channel/item/description'),'text','<p>Annonce sans image</p>'),'CF_RSS_POLICY')
def leakpage(tree):
    target=pages['publications'][1]
    it=next(i for i in tree.findall('./channel/item') if i.findtext('guid')==target['id'])
    it.find('description').text+='<img src="'+urljoin(mainbase,target['resources'][0]['src'])+'" alt="Page non sélectionnée comme miniature">'
xmlcase('rss-pages-image-de-lecture',pagespath,pages,leakpage,'CF_RSS_POLICY')
(ROOT/'checks/rss-invalid-cases.json').write_text(json.dumps(rsscases,ensure_ascii=False,indent=2)+'\n')

baseline=json.loads((ROOT/'checks/reference-results.json').read_text())
assert baseline['passed']==baseline['total']==79, 'Les contrôles de référence doivent tous avoir réussi.'

combined=[dict(x,group='reference_1_0') for x in baseline['results']]+[dict(x,group='extension_1_1') for x in results]
summary={
    'edition':'1.1','reference_instant':NOW,'total':len(combined),'passed':sum(x['passed'] for x in combined),
    'failed':[x for x in combined if not x['passed']],
    'scope':'Fixtures hors ligne : structure et mots-clés employés des schémas, cardinalités, accès, versions, sens de lecture, IDs et dates, relations de démonstration, RSS et régression 1.0 avec médias factices.',
    'not_verified':['Validateur JSON Schema tiers complet','Existence et décodage des nouveaux médias documentaires','Déploiement HTTPS/CORS des exemples 1.1','Comportement réel du Reader 0.8.7 et des autres applications','Affichage réel dans les agrégateurs RSS','Corpus réel SPOON/CUVIER et interopérabilité sur hébergements réels'],
    'results':combined
}
(ROOT/'checks/extension-results.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:summary[k] for k in ('total','passed','failed')},ensure_ascii=False,indent=2))
if summary['failed']:raise SystemExit(1)
