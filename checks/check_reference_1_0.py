"""Vérification interne du livrable. Ce script n'est pas un validateur livré."""
from pathlib import Path
from urllib.parse import urljoin,urlparse,unquote
from datetime import datetime,timezone
from decimal import Decimal, ROUND_FLOOR
from email.utils import parsedate_to_datetime
from PIL import Image
import re,json,calendar,xml.etree.ElementTree as E

ROOT=Path(__file__).resolve().parents[1]/'reference-1.0'
NOW='2026-10-05T10:00:00Z'
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
    se=sch(d,schemas[kind],schemas[kind])
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
        u=urlcheck(src)
        if not u:return
        try:
            p=pathurl(u,overrides)
            with Image.open(p) as im:
                if im.format not in ('JPEG','PNG','WEBP'):err('CF_RESOURCE_FORMAT',u)
                im.verify()
        except FileNotFoundError:err('NET_HTTP',u)
        except Exception:err('CF_RESOURCE_FORMAT',u)
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
                if resources is not None and (len(resources)==0 or c.get('type')=='strip' and len(resources)!=1):err('CF_RESOURCE_COUNT')
                try:eligible=instant(p['publish_at'])<=instant(NOW) and acc=='public'
                except Exception:eligible=False
                if c.get('rss') and eligible and c.get('status')!='withdrawn' and meta.get('status')!='withdrawn' and not p.get('url'):err('CF_RSS_POLICY')
            for res in p.get('resources',[]):imagecheck(res['src'])
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

results=[]
def result(name,ok,details=None):results.append({'name':name,'passed':bool(ok),'details':details or []})
# Tous les $ref et motifs doivent être résolubles ; aucun chargement externe.
for k,s in schemas.items():
    def audit(x):
        if isinstance(x,dict):
            if '$ref'in x:assert x['$ref'].startswith('#/$defs/') and x['$ref'].split('/')[-1] in s['$defs']
            if 'pattern'in x:re.compile(x['pattern'])
            for v in x.values():audit(v)
        elif isinstance(x,list):
            for v in x:audit(v)
    audit(s);result('schema-local-'+k,True)

series_context={}
for m in mapping:
    for f in (ROOT/m['directory']).rglob('feed.json'):
        base=m['base_url']+f.relative_to(ROOT/m['directory']).as_posix()
        d=load(f.relative_to(ROOT));codes,detail=validate(d,base)
        result('reference:'+f.relative_to(ROOT).as_posix(),not codes,detail or sorted(codes))
        if isinstance(d['series'],dict):series_context[base]=d
        if isinstance(d.get('channels'),list):
            for c in d['channels']:
                if 'rss'in c:
                    rp=pathurl(urljoin(base,c['rss'])).relative_to(ROOT)
                    errors=rsscheck(rp,d,c,base);result('rss:'+str(rp),not errors,sorted(errors))

# Unicité des définitions à l’échelle des trois catalogues courants.
globalids=[]
for d in series_context.values():
    globalids.append(d['series']['id'])
    for c in d['channels']:
        globalids.append(c['id']);globalids.extend(p['id'] for p in c['publications'])
result('unicite-definitions-multi-publishers',len(globalids)==len(set(globalids)))

for case in load('invalid/manifest.json')['cases']:
    if case.get('kind')=='rss':
        d=load(case['series']);c=next(c for c in d['channels'] if c['id']==case['channel_id']);codes=rsscheck(case['file'],d,c,case['base_url'])
    else:
        try:
            d=load(case['file']);codes,detail=validate(d,case.get('base_context',case.get('base_url','https://aube.example/bd/feed.json')),
              case.get('resource_override'),load(case['parent']) if case.get('parent') else None,load(case['before']) if case.get('before') else None)
        except ValueError as e:codes={'CF_DUPLICATE_KEY' if 'CF_DUPLICATE_KEY'in str(e) else 'CF_JSON'}
    result('invalide:'+case['name'],case['expected']in codes,{'expected':case['expected'],'observed':sorted(codes)})

for c in load('scenarios/manifest.json')['scenarios']:
    if 'before'in c:
        before=load(c['before']);after=load(c['after']);overrides={x['url']:x['file'] for x in c['other_documents']}
        for phase,d in [('before',before),('after',after)]:
            over={**overrides,c['base_url']:c[phase],c['publisher_url']:c[phase+'_publisher']}
            codes,detail=validate(d,c['base_url'],over,before=before if phase=='after' else None)
            result('scenario:'+c['name']+':'+phase,not codes,detail or sorted(codes))
            codes,detail=validate(load(c[phase+'_publisher']),c['publisher_url'],over)
            result('scenario-index:'+c['name']+':'+phase,not codes,detail or sorted(codes))
        result('scenario-id:'+c['name'],before['channels'][0]['publications'][0]['id']==after['channels'][0]['publications'][0]['id'])
    elif c['name']=='programmation':
        d=load(c['document']);p=next(p for ch in d['channels'] for p in ch['publications'] if p['id']==c['publication_id'])
        for ev in c['evaluations']:result('programmation:'+ev['now'],(instant(ev['now'])>=instant(p['publish_at']))==ev['available'])
    else:result('scenario-migration-identite',load(c['source'])['publisher']['id']==load(c['target'])['publisher']['id'])

for c in load('compatibility/manifest.json')['cases']:
    d=load(c['file'])
    if d['version'].startswith('2.'):action='UNSUPPORTED'
    elif any(ch['type']not in ('strip','webtoon') for ch in d['channels']):action='UNSUPPORTED'
    else:action='KNOWN_SUBSET'
    result('compatibilite:'+c['file'],action==c['expected'])

summary={'reference_instant':NOW,'total':len(results),'passed':sum(x['passed'] for x in results),'failed':[x for x in results if not x['passed']],
 'scope':'Contrôles internes hors ligne, schémas avec leurs mots-clés employés, dates, médias, URLs virtuelles, relations, historique et RSS. Aucun test réseau réel ni validateur tiers exécuté.',
 'not_verified':['CORS et HTTPS sur des hébergements réels','Compatibilité observée dans des applications RSS réelles','Applications Reader, Admin et Collector','Validateur JSON Schema tiers complet'], 'results':results}
(Path(__file__).resolve().parent/'reference-results.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:summary[k] for k in ['total','passed','failed']},ensure_ascii=False,indent=2))
if summary['failed']:raise SystemExit(1)
