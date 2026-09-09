#!/usr/bin/env python3
"""Capability-driven validator for offline interactive-classroom HTML.

The validator ignores public Skill release numbers and numeric schema branches.
It validates the stable Stage/Scene contract and applies feature-specific gates
when the corresponding capability or policy is present.
"""
from __future__ import annotations
import argparse,re,sys,json
from pathlib import Path

FORBIDDEN={
 r"\bfetch\s*\(":"network fetch() call",
 r"\bXMLHttpRequest\b":"XMLHttpRequest network API",
 r"\bWebSocket\b":"WebSocket network API",
 r"\bEventSource\b":"EventSource network API",
 r"\bnavigator\.sendBeacon\s*\(":"navigator.sendBeacon network API",
 r"\bimport\s*\(\s*[\"']https?://":"remote dynamic import",
 r"\bserviceWorker\.register\s*\(\s*[\"']https?://":"remote service-worker registration",
 r"\bwindow\.open\s*\(\s*[\"']https?://":"remote window.open target",
 r"\.(?:src|href)\s*=\s*[\"']https?://":"remote DOM src/href assignment",
 r"\.setAttribute\s*\(\s*[\"'](?:src|href|srcset|data|poster)[\"']\s*,\s*[\"']https?://":"remote DOM attribute assignment",
 r"url\(\s*[\"']?https?://":"remote CSS url() resource",
 r"@import\s+(?:url\()?\s*[\"']?https?://":"remote CSS @import",
 r"<script[^>]+src\s*=\s*[\"']https?://":"external script",
 r"<link[^>]+href\s*=\s*[\"']https?://":"external stylesheet/resource link",
 r"<(?:img|audio|video|source|iframe)[^>]+src\s*=\s*[\"']https?://":"remote media/frame",
 r"<(?:img|source)[^>]+srcset\s*=\s*[\"'][^\"']*https?://":"remote srcset",
 r"<object[^>]+data\s*=\s*[\"']https?://":"remote object data",
 r"<video[^>]+poster\s*=\s*[\"']https?://":"remote video poster",
 r"api\.openai\.com":"OpenAI API endpoint",
 r"api\.anthropic\.com":"Anthropic API endpoint",
 r"generativelanguage\.googleapis\.com":"Gemini API endpoint",
}
WARN={
  r"<[a-z][^>]*\bonclick\s*=\s*[\"']":"inline onclick handler; prefer addEventListener",
 r"target\s*=\s*[\"']_blank":"external navigation target; verify intentional",
 r"allow-same-origin":"sandbox allow-same-origin detected; review isolation",
}
STRICT_REQUIRED={
 r'<meta\s+name=["\']interactive-classroom-schema["\']\s+content=["\']stage-scene["\']':"missing stable Stage/Scene schema marker",
 r'data-interactive-classroom=["\']stable["\']':"missing stable classroom app marker",
 r"互动学习":"missing learner-visible learning chrome",
 r"prefers-reduced-motion":"missing reduced-motion handling",
 r"aria-live":"missing aria-live feedback/status region",
}

def _flatten_text(obj):
 if obj is None: return ""
 if isinstance(obj,str): return obj
 if isinstance(obj,(int,float,bool)): return str(obj)
 if isinstance(obj,list): return " ".join(_flatten_text(x) for x in obj)
 if isinstance(obj,dict): return " ".join(_flatten_text(v) for k,v in obj.items() if k not in {"id"})
 return ""

def _visible_len(text):
 # Approximate meaningful reading length across Chinese and alphabetic languages.
 return len(re.findall(r"[\u3400-\u9fffA-Za-z0-9]", text or ""))

def _knowledge_components(k):
 if not isinstance(k,dict): return 0
 keys=["prerequisites","mentalModel","intuition","definition","mechanism","keyPoints","sections","semanticBlocks","workedExamples","example","comparison","evidence","boundaries","pitfalls","connections","glossary","checkYourself"]
 return sum(bool(k.get(x)) for x in keys)

def _experiment_entries(cfg):
 if not isinstance(cfg,dict): return []
 entries=[]
 if cfg.get('experimentKey'):
  entries.append({'key':str(cfg.get('experimentKey')).strip(),'role':str(cfg.get('experimentRole') or '').strip(),'prompt':str(cfg.get('prompt') or '').strip(),'source':'scene'})
 values=cfg.get('experimentPrompts') if cfg.get('experimentPrompts') is not None else cfg.get('experiments')
 if not isinstance(values,list): values=[] if values is None else [values]
 for item in values:
  if isinstance(item,dict):
   entries.append({'key':str(item.get('experimentKey') or item.get('key') or '').strip(),'role':str(item.get('experimentRole') or item.get('role') or '').strip(),'prompt':str(item.get('prompt') or item.get('text') or item.get('title') or '').strip(),'source':'item'})
  elif item is not None:
   entries.append({'key':'','role':'','prompt':str(item).strip(),'source':'item'})
 return entries

def _normalized_prompt(value):
 return re.sub(r'\s+',' ',str(value or '').strip()).casefold()

def validate(path:Path,strict=False)->int:
 text=path.read_text(encoding='utf-8',errors='replace'); fails=[]; warns=[]
 if '<!doctype html>' not in text.lower(): fails.append('missing <!doctype html>')
 if not re.search(r'<meta[^>]+name=["\']viewport["\']',text,re.I): fails.append('missing responsive viewport meta')
 if '<script' not in text.lower(): warns.append('no JavaScript found; classroom may not be interactive')
 for pat,label in FORBIDDEN.items():
  if re.search(pat,text,re.I|re.S): fails.append(label)
 for pat,label in WARN.items():
  if re.search(pat,text,re.I|re.S): warns.append(label)
 unresolved=re.findall(r'\{\{[A-Z0-9_]+\}\}',text)
 if unresolved: fails.append('unresolved template placeholders: '+', '.join(sorted(set(unresolved))))
 if strict:
  for pat,label in STRICT_REQUIRED.items():
   if not re.search(pat,text,re.I|re.S): fails.append(label)
  # Runtime contracts when corresponding content appears.
  if 'knowledge-graph' in text and 'ArrowLeft' not in text: warns.append('knowledge graph found but keyboard movement not detected')
  if '"widgetType":"simulation"' in text or 'widgetType: simulation' in text:
   if '模型假设' not in text and 'assumptions' not in text: warns.append('simulation found without visible assumptions contract')
  if '"widgetType":"visualization3d"' in text and 'reset3d' not in text: warns.append('visualization3d found without reset control')
  if '"widgetType":"code"' in text and '确定性代码跟踪' not in text: warns.append('code widget should state deterministic trace boundary')
  if 'procedural-skill' in text and '教学模拟' not in text and '资格认证' not in text: warns.append('procedural skill should state educational/safety boundary')
  modern_runtime='interactive-classroom-runtime" content="modern-react' in text or "interactive-classroom-runtime' content='modern-react" in text
  if 'scene.actions' in text or '"actions":[' in text:
   for token in ['HIGHLIGHT_ELEMENT','SET_WIDGET_STATE','REVEAL_STEP','RESET_WIDGET']:
    if token not in text: warns.append(f'action bus does not expose common action token {token}')
  if not modern_runtime and 'Action Bus' not in text and 'executeAction' not in text:
   warns.append('portable classroom does not appear to include the local action bus')
  course_match=re.search(r'const\s+course\s*=\s*(\{.*?\})\s*;\s*const\s+initialState', text, re.S)
  modern_course_match=re.search(r'<script[^>]+id=["\']course-data["\'][^>]*type=["\']application/json["\'][^>]*>(.*?)</script>',text,re.I|re.S) if modern_runtime else None
  course_blob=modern_course_match.group(1) if modern_course_match else (course_match.group(1) if course_match else None)
  if course_blob:
   try:
    course_data=json.loads(course_blob)
    meta0=course_data.get('meta') or {}
    for forbidden_key in ('version','schemaVersion','runtimeProfileVersion','runtimeProfileContract'):
     if forbidden_key in meta0: fails.append(f'version-neutral contract violation; remove meta.{forbidden_key}')
    if modern_runtime:
     meta=course_data.get('meta') or {}
     if meta.get('runtimeProfile')!='modern-react': fails.append('modern runtime violation; course meta.runtimeProfile must be modern-react')
     for token in ['data-runtime-profile="modern-react"','interactive-classroom-react','interactive-classroom-motion','interactive-classroom-tailwind']:
      if token not in text: fails.append(f'modern runtime violation; missing {token}')
     # A Modern course must expose the concrete implementation contract for
     # every native animation/model widget it actually uses. Checking the
     # compiled bundle tokens catches a registry entry that exists only as a
     # route or placeholder, while keeping the validator independent of React
     # server-side rendering.
     used_modern_widgets={((sc.get('content') or {}).get('widgetType')) for sc in course_data.get('scenes',[]) if (sc.get('content') or {}).get('widgetType')}
     widget_marker=re.search(r'<meta[^>]+name=["\']interactive-classroom-widgets["\'][^>]+content=["\']([^"\']*)["\']',text,re.I|re.S)
     marked_modern_widgets={x.strip() for x in (widget_marker.group(1).split(',') if widget_marker else []) if x.strip()}
     if widget_marker is None: fails.append('modern runtime violation; missing interactive-classroom-widgets marker')
     for wt in sorted(used_modern_widgets-marked_modern_widgets): fails.append(f'modern runtime violation; build marker missing used widget {wt}')
     modern_widget_tokens={
      'process-animation':['data-modern-widget','timeline-autoplay-reduced-motion','prefers-reduced-motion'],
      'motion-lab':['data-modern-widget','motion-lab-raf-trials','requestAnimationFrame'],
      'simulation':['data-modern-widget','simulation-raf-model','requestAnimationFrame'],
      'equation':['data-modern-widget','equation-mathml-fallback','ic-math'],
     }
     for wt in used_modern_widgets:
      for token in modern_widget_tokens.get(wt,[]):
       if token not in text: fails.append(f'modern runtime violation; {wt} requires {token}')
    # Source/citation and long-course runtime gate
    sources=course_data.get('sources') or []
    source_ids={}
    for i,src in enumerate(sources,1):
     if not isinstance(src,dict):
      fails.append(f'source/bibliography violation; source {i} is not an object'); continue
     sid=src.get('id')
     if not sid: fails.append(f'source/bibliography violation; source {i} has no stable id')
     elif sid in source_ids: fails.append(f'source/bibliography violation; duplicate source id: {sid}')
     else: source_ids[sid]=src
     if not src.get('title'): fails.append(f'source/bibliography violation; source {sid or i} has no title')
    def _walk_citations(o, path='course'):
     if isinstance(o,dict):
      if isinstance(o.get('citations'),list):
       for j,c in enumerate(o.get('citations') or [],1):
        sid=c if isinstance(c,str) else (c or {}).get('sourceId')
        if not sid: fails.append(f'source/citation violation; citation at {path}[{j}] has no sourceId')
        elif sid not in source_ids: fails.append(f'source/citation violation; citation at {path}[{j}] references unknown source {sid}')
       
      for k,v in o.items():
       if k!='citations': _walk_citations(v,f'{path}.{k}')
     elif isinstance(o,list):
      for i,v in enumerate(o): _walk_citations(v,f'{path}[{i}]')
    _walk_citations(course_data)
    if (course_data.get('meta') or {}).get('sourcePolicy')=='grounded':
     for sc in course_data.get('scenes',[]):
      if sc.get('type') not in {'orientation','concept','discussion','interactive','pbl'}: continue
      found=[]
      def _collect(o):
       if isinstance(o,dict):
        if o.get('citations'): found.extend(o.get('citations') or [])
        for k,v in o.items():
         if k!='citations': _collect(v)
       elif isinstance(o,list):
        for v in o:_collect(v)
      _collect(sc)
      if not found: fails.append(f'source/citation violation; grounded core scene {sc.get("id","?")} has no citation')
    if not modern_runtime:
     baseline_tokens=['sceneSearch','bookmarkCurrentBtn','bibliographyDialog','renderCitations','executeAction','lessonToc','data-toc-title','sessionFeedbackBundle']
     for token in baseline_tokens:
      if token not in text: fails.append(f'portable runtime violation; missing {token}')
     used_widgets={((sc.get('content') or {}).get('widgetType')) for sc in course_data.get('scenes',[]) if (sc.get('content') or {}).get('widgetType')}
     widget_runtime_tokens={
      'proof-practice':['proof-practice'], 'quantity-lab':['quantity-lab','quantity-input'], 'chemistry':['chemistry','chem-coeff-up'],
      'diagram':['diagram-play'], 'data-lab':['data-input','experiment-panel'], 'motion-lab':['motion-lab','renderMotionLab','motion-param','motion-time','motion-record'],
      'geometry-lab':['geometry-lab','renderGeometryLab'], 'fbd-lab':['fbd-lab','renderFbdLab'], 'circuit-lab':['circuit-lab'],
      'molecule-lab':['molecule-lab'], 'genetics-lab':['genetics-lab'], 'stats-lab':['stats-lab'], 'search-tree-lab':['search-tree-lab'],
      'ml-boundary-lab':['ml-boundary-lab'], 'map-lab':['map-lab','haversineKm','geoProject'], 'data-structure-lab':['data-structure-lab','renderDataStructureLab'],
      'recursion-lab':['recursion-lab','renderRecursionLab'], 'complexity-lab':['complexity-lab','renderComplexityLab'], 'cloze-lab':['cloze-lab','renderClozeLab'],
      'sentence-builder-lab':['sentence-builder-lab'], 'grammar-tree-lab':['grammar-tree-lab'], 'source-comparison-lab':['source-comparison-lab','renderSourceComparisonLab'],
      'argument-map-lab':['argument-map-lab'], 'causal-dag-lab':['causal-dag-lab','renderCausalDagLab'], 'evidence-matrix-lab':['evidence-matrix-lab'],
      'solid-geometry-lab':['solid-geometry-lab','renderSolidGeometryLab'], 'space-geometry-lab':['space-geometry-lab','renderSpaceGeometryLab'],
      'process-animation':['process-animation','renderProcessAnimation','processAnimationState','process-debrief','process-why'],
      'random-trial-lab':['random-trial-lab','renderRandomTrialLab'], 'visualization3d':['reset3d'], 'code':['确定性代码跟踪']
     }
     if any(sc.get('type')=='explain-back' for sc in course_data.get('scenes',[])):
      for token in ['explain-back','renderExplainBack']:
       if token not in text: fails.append(f'portable runtime violation; missing {token}')
     if any((sc.get('content') or {}).get('masteryGate') for sc in course_data.get('scenes',[])):
      for token in ['masteryGateHtml','practiceLevelLabel']:
       if token not in text: fails.append(f'portable runtime violation; missing {token}')
     if any((sc.get('knowledge') or (sc.get('content') or {}).get('knowledge') or {}).get('pedagogicalFigures') for sc in course_data.get('scenes',[])):
      for token in ['renderPedagogicalFigure','figureKindLabel','figure-helpful','figure-confusing-or-missing']:
       if token not in text: fails.append(f'portable runtime violation; missing {token}')
     for wt in used_widgets:
      for token in widget_runtime_tokens.get(wt,[]):
       if token not in text: fails.append(f'portable runtime violation; {wt} requires {token}')
    required={'orientation','concept','discussion','interactive','pbl'}
    missing=[]; shallow=[]; weak=[]; lengths=[]
    for sc in course_data.get('scenes',[]):
     if sc.get('type') not in required: continue
     k=sc.get('knowledge') or (sc.get('content') or {}).get('knowledge')
     sid=sc.get('id') or sc.get('title') or '?'
     if not k:
      missing.append(sid); continue
     for field in ['keyPoints','pitfalls','connections','checkYourself']:
      if k.get(field) is not None and not isinstance(k.get(field),list): fails.append(f'knowledge-schema violation; scene {sid} field {field} must be a list')
     n=_visible_len(_flatten_text(k)); lengths.append((sid,n))
     profile=str((course_data.get('meta') or {}).get('depthProfile','learn-deep')); threshold={'overview':220,'learn-deep':600,'systematic':900,'deep':900}.get(profile,500);
     if sc.get('type')!='mastery' and n < threshold: shallow.append(f"{sid}({n}<{threshold})")
     if _knowledge_components(k) < 3: weak.append(sid)
    if missing:
     fails.append('knowledge-first violation; core scenes missing knowledge blocks: '+', '.join(missing))
    if shallow:
     fails.append('deep-explanation violation; core knowledge blocks are too thin: '+', '.join(shallow))
    if weak:
     warns.append('knowledge blocks use fewer than 3 explanatory components: '+', '.join(weak))
    profile=str((course_data.get('meta') or {}).get('depthProfile','learn-deep')); avg_target={'overview':300,'learn-deep':720,'systematic':1100,'deep':1100}.get(profile,650);
    if lengths and sum(n for _,n in lengths)/len(lengths) < avg_target:
     warns.append(f'average core explanation is short for {profile} mode (<{avg_target} meaningful characters)')
    # Math quality gate
    def _has_formula(o):
     if isinstance(o,dict):
      if ('mathml' in o and ('tex' in o or 'spoken' in o or 'ariaLabel' in o)): return True
      return any(_has_formula(x) for x in o.values())
     if isinstance(o,list): return any(_has_formula(x) for x in o)
     return False
    eq_scenes=[sc for sc in course_data.get('scenes',[]) if ((sc.get('content') or {}).get('widgetType')=='equation')]
    authored_math=_has_formula(course_data)
    if authored_math or eq_scenes:
     if '<math' not in text.lower(): fails.append('math-typesetting violation; authored formulas/equation course contains no native MathML')
     if re.search(r'<pre[^>]*class=["\\\'][^"\\\']*math',text,re.I): fails.append('math-typesetting violation; formula rendered primarily as pre/code monospace')
     for sc in eq_scenes:
      bad=[]
      for i,st in enumerate((((sc.get('content') or {}).get('widgetConfig') or {}).get('steps') or []),1):
       f=st.get('formula') if isinstance(st,dict) else None
       if not isinstance(f,dict) or not f.get('mathml') or not (f.get('tex') or f.get('spoken') or f.get('ariaLabel')): bad.append(str(i))
      if bad: fails.append(f"math-typesetting violation; equation scene {sc.get('id','?')} steps missing structured MathML+fallback: "+', '.join(bad))
    # Every declared formula slot must use a structured MathML object.
    if True:
     bad_formula_slots=[]
     def _scan_formula_slots(o,path='course'):
      if isinstance(o,dict):
       for k,v in o.items():
        pth=f'{path}.{k}'
        if k in {'formula','definitionFormula','resultFormula','promptFormula','feedbackFormula'} and v is not None:
         if not (isinstance(v,dict) and v.get('mathml') and (v.get('tex') or v.get('spoken') or v.get('ariaLabel'))): bad_formula_slots.append(pth)
        elif k=='formulas' and isinstance(v,list):
         for i,f in enumerate(v):
          if not (isinstance(f,dict) and f.get('mathml') and (f.get('tex') or f.get('spoken') or f.get('ariaLabel'))): bad_formula_slots.append(f'{pth}[{i}]')
        _scan_formula_slots(v,pth)
      elif isinstance(o,list):
       for i,v in enumerate(o): _scan_formula_slots(v,f'{path}[{i}]')
     _scan_formula_slots(course_data)
     if bad_formula_slots: fails.append('math-typesetting violation; formula slots must use structured MathML+fallback objects: '+', '.join(bad_formula_slots[:12]))

    # Raw-math leakage gate: substantive equations belong in structured formula objects.
    if True:
     math_like=re.compile(r'(?:[A-Za-z\u0370-\u03ffŷŶ][A-Za-z0-9_\u0370-\u03ffŷŶ()*\'′]*\s*(?:=|≤|≥|≡|≈)\s*[^。；，,\n]{1,70}|\\(?:frac|sum|int|lim|sqrt|begin)\b)')
     skip_keys={'id','tex','mathml','spoken','ariaLabel','code','dimension','lhsDimension','rhsDimension','unit','src','url','locator','sourceId','expectedOutput','answer','answers'}
     narrative_keys={'text','body','summary','mentalModel','intuition','definition','mechanism','statement','prompt','result','conclusion','strategy','reason','justification','note','takeaway','evidence','feedback','correct','incorrect','explanation','detail','rationale','title'}
     leaks=[]
     def _scan_raw(o,path='course',parent_key=''):
      if isinstance(o,dict):
       if o.get('mathml') and (o.get('tex') or o.get('spoken') or o.get('ariaLabel')): return
       for k,v in o.items():
        if k in skip_keys: continue
        _scan_raw(v,f'{path}.{k}',k)
      elif isinstance(o,list):
       for i,v in enumerate(o): _scan_raw(v,f'{path}[{i}]',parent_key)
      elif isinstance(o,str) and (parent_key in narrative_keys or '.knowledge.' in path or '.content.items' in path):
       m=math_like.search(o)
       if m: leaks.append((path,m.group(0)[:90]))
     _scan_raw(course_data)
     if leaks:
      sample='; '.join(f'{p}: {x}' for p,x in leaks[:8])
      fails.append('math-typesetting violation; substantive math leaked into plain narrative strings instead of structured MathML formula atoms: '+sample)
    def _valid_formula_obj(f):
     return isinstance(f,dict) and bool(f.get('mathml')) and bool(f.get('tex') or f.get('spoken') or f.get('ariaLabel'))
    # Textbook semantic-block quality gate
    sem_index={}
    sem_blocks=[]
    sem_pos={}
    for si,sc in enumerate(course_data.get('scenes',[])):
     k=sc.get('knowledge') or (sc.get('content') or {}).get('knowledge') or {}
     for bi,b in enumerate(k.get('semanticBlocks') or []):
      if not isinstance(b,dict): continue
      bid=b.get('id'); sem_blocks.append((sc,b))
      if not bid: fails.append(f"textbook-semantics violation; semantic block in scene {sc.get('id','?')} has no stable id")
      elif bid in sem_index: fails.append(f"textbook-semantics violation; duplicate semantic block id: {bid}")
      else:
       sem_index[bid]=(sc,b)
       sem_pos[bid]=(si,bi)
    # Formula IDs participate in cross references and auto numbering.
    formula_ids=set()
    def _formula_ids(o):
     if isinstance(o,dict):
      if o.get('mathml') and o.get('id'):
       if o.get('id') in formula_ids: fails.append(f'math-typesetting violation; duplicate formula id: {o.get("id")}')
       formula_ids.add(o.get('id'))
      for v in o.values(): _formula_ids(v)
     elif isinstance(o,list):
      for v in o:_formula_ids(v)
    _formula_ids(course_data)
    formal=((course_data.get('meta') or {}).get('discipline') or {})
    if isinstance(formal,dict): formal=formal.get('primary')
    theoremish={'theorem','lemma','proposition','corollary'}
    for sc,b in sem_blocks:
     kind=b.get('kind','remark'); bid=b.get('id','?')
     if kind in theoremish and not (b.get('statement') or b.get('body')):
      fails.append(f"textbook-semantics violation; {kind} {bid} has no statement/body")
     if b.get('formula') and not _valid_formula_obj(b.get('formula')):
      fails.append(f"math-typesetting violation; semantic block {bid} formula lacks MathML+fallback")
     if kind in {'example','exercise'}:
      for j,st in enumerate((b.get('steps') or []),1):
       if isinstance(st,dict) and st.get('formula') and not _valid_formula_obj(st.get('formula')):
        fails.append(f"math-typesetting violation; {kind} {bid} step {j} lacks structured MathML+fallback")
      sol=b.get('solution')
      if isinstance(sol,dict) and sol.get('formula') and not _valid_formula_obj(sol.get('formula')):
       fails.append(f"math-typesetting violation; exercise {bid} solution formula lacks structured MathML+fallback")
     if kind=='proof':
      target=b.get('of')
      if target and target not in sem_index: fails.append(f"textbook-semantics violation; proof {bid} references unknown target {target}")
      elif target and bid in sem_pos and sem_pos.get(target,(-1,-1))>=sem_pos.get(bid,(10**9,10**9)):
       fails.append(f"textbook-semantics violation; proof {bid} appears before the claim it proves ({target})")
      steps=b.get('steps') or []
      if not b.get('body') and len(steps)<2: warns.append(f"proof {bid} is very short; use multiple justified steps or a substantive proof body")
      for j,st in enumerate(steps,1):
       if isinstance(st,dict) and st.get('formula'):
        f=st.get('formula')
        if not isinstance(f,dict) or not f.get('mathml') or not (f.get('tex') or f.get('spoken') or f.get('ariaLabel')):
         fails.append(f"math-typesetting violation; proof {bid} step {j} lacks structured MathML+fallback")
        if not (st.get('reason') or st.get('justification') or st.get('citation')):
         fails.append(f"textbook-semantics violation; proof {bid} formula step {j} has no reason/justification")
       elif isinstance(st,dict) and st.get('text') and not (st.get('reason') or st.get('justification') or st.get('citation')):
        warns.append(f"proof {bid} prose step {j} has no explicit reason/justification")
     if kind=='exercise':
      if not b.get('prompt'): fails.append(f"textbook-semantics violation; exercise {bid} has no prompt")
      if not (b.get('hints') or b.get('solution') or b.get('selfCheck')):
       warns.append(f"exercise {bid} has no hint/solution/selfCheck support")
      for dep in (b.get('dependsOn') or []):
       if dep not in sem_index: fails.append(f"textbook-semantics violation; exercise {bid} depends on unknown semantic block {dep}")
       elif bid in sem_pos and sem_pos.get(dep,(-1,-1))>=sem_pos.get(bid,(10**9,10**9)):
        fails.append(f"textbook-semantics violation; exercise {bid} depends on knowledge that appears later ({dep})")
     for ref in (b.get('references') or []):
      rid=ref if isinstance(ref,str) else (ref.get('id') if isinstance(ref,dict) else None)
      if rid and rid not in sem_index and rid not in formula_ids: fails.append(f"textbook-semantics violation; semantic block {bid} references unknown block/formula {rid}")
    if formal=='formal-quantitative':
     for sc,b in sem_blocks:
      kind=b.get('kind'); bid=b.get('id','?')
      if kind in {'theorem','lemma','proposition'}:
       has_proof=any(pb.get('kind')=='proof' and pb.get('of')==b.get('id') for _,pb in sem_blocks)
       has_just=bool(b.get('proofSketch') or b.get('justification') or b.get('proofRequired') is False)
       if not (has_proof or has_just): fails.append(f"textbook-semantics violation; formal claim {bid} has no linked proof/proofSketch/justification/explicit proofRequired:false")
    profile=str((course_data.get('meta') or {}).get('depthProfile','learn-deep'))
    if profile in {'systematic','deep'} and sem_blocks:
     for _,b in sem_blocks:
      if (course_data.get('meta') or {}).get('autoNumbering') is False and b.get('kind') in {'definition','theorem','lemma','proposition','corollary','example','exercise'} and not (b.get('number') or b.get('label')):
       warns.append(f"systematic textbook block {b.get('id','?')} has no stable number/label while autoNumbering is disabled")
    # Subject-specific widget quality gates
    for sc in course_data.get('scenes',[]):
     c=sc.get('content') or {}; wt=c.get('widgetType'); cfg=c.get('widgetConfig') or {}; sid=sc.get('id','?')
     if wt=='proof-practice':
      mode=cfg.get('mode','ordering'); steps=cfg.get('steps') or []
      ids=[x.get('id') for x in steps if isinstance(x,dict)]
      if len(ids)<3 or any(not x for x in ids): fails.append(f'proof-practice violation; scene {sid} needs at least 3 stable step ids')
      for j,st in enumerate(steps,1):
       if isinstance(st,dict) and st.get('formula') and not _valid_formula_obj(st.get('formula')): fails.append(f'math-typesetting violation; proof-practice scene {sid} step {j} formula lacks MathML+fallback')
      if mode=='ordering':
       ans=cfg.get('answer') or []
       if sorted(ans)!=sorted(ids): fails.append(f'proof-practice violation; scene {sid} ordering answer must contain exactly the step ids')
      elif mode=='reason-match':
       reasons={x.get('id') for x in (cfg.get('reasons') or []) if isinstance(x,dict)}; ans=cfg.get('answer') or {}
       if set(ans)!=set(ids) or any(v not in reasons for v in ans.values()): fails.append(f'proof-practice violation; scene {sid} reason-match answer/reasons are incomplete')
      else: fails.append(f'proof-practice violation; scene {sid} has unsupported mode {mode}')
     if wt=='quantity-lab':
      qs=cfg.get('quantities') or []
      if len(qs)<2: fails.append(f'quantity/unit violation; scene {sid} needs at least two quantities')
      for q in qs:
       if not q.get('unit') or not q.get('dimension'): fails.append(f'quantity/unit violation; scene {sid} quantity {q.get("id") or q.get("symbol") or "?"} needs unit and dimension')
      eq=cfg.get('equation') or {}
      if not eq.get('lhsDimension') or not eq.get('rhsDimension'): fails.append(f'quantity/unit violation; scene {sid} needs declared lhs/rhs dimensions')
      if cfg.get('expectDimensionallyConsistent',True) and eq.get('lhsDimension')!=eq.get('rhsDimension'): fails.append(f'quantity/unit violation; scene {sid} expected a dimensionally consistent relation')
     if wt=='motion-lab':
      params={x.get('id'):x for x in (cfg.get('parameters') or []) if isinstance(x,dict)}
      if (cfg.get('model') or {}).get('kind')!='horizontal-projectile': fails.append(f'motion-lab violation; scene {sid} needs model.kind horizontal-projectile')
      for qid,unit,dim in [('v0','m/s','L T^-1'),('h','m','L'),('g','m/s^2','L T^-2')]:
       q=params.get(qid)
       if not q: fails.append(f'motion-lab violation; scene {sid} missing parameter {qid}')
       else:
        if q.get('unit')!=unit: fails.append(f'motion-lab violation; scene {sid} parameter {qid} unit should be {unit}')
        if q.get('dimension')!=dim: fails.append(f'motion-lab violation; scene {sid} parameter {qid} dimension should be {dim}')
        if q.get('min') is None or q.get('max') is None or q.get('step') is None: fails.append(f'motion-lab violation; scene {sid} parameter {qid} needs min/max/step')
      if cfg.get('fixedComparisonScale') is not True: fails.append(f'motion-lab violation; scene {sid} should use fixedComparisonScale:true for parameter comparison')
      if cfg.get('timeControl') is not True: fails.append(f'motion-lab violation; scene {sid} needs timeControl:true')
      if cfg.get('trialLogging') is not True: fails.append(f'motion-lab violation; scene {sid} needs trialLogging:true')
      if len(cfg.get('experiments') or [])<2: fails.append(f'motion-lab violation; scene {sid} needs at least two control-variable experiment prompts')
      if len(cfg.get('assumptions') or [])<2: warns.append(f'motion-lab scene {sid} should state model assumptions explicitly')
     if wt=='chemistry':
      rx=(cfg.get('reaction') or {}); react=rx.get('reactants') or []; prod=rx.get('products') or []
      if not react or not prod: fails.append(f'chemistry violation; scene {sid} reaction needs reactants and products')
      def _counts(side):
       out={}
       for cp in side:
        coef=float(cp.get('coefficient',1))
        atoms=cp.get('atoms') or []
        if not atoms: fails.append(f'chemistry violation; scene {sid} compound {cp.get("label") or "?"} needs structured atoms')
        for a in atoms:
         sym=a.get('symbol'); cnt=float(a.get('count',1))
         if not sym: fails.append(f'chemistry violation; scene {sid} atom has no symbol')
         else: out[sym]=out.get(sym,0)+coef*cnt
       return out
      l,r=_counts(react),_counts(prod); atoms=set(l)|set(r); balanced=all(abs(l.get(a,0)-r.get(a,0))<1e-9 for a in atoms)
      if cfg.get('expectBalanced') is True and not balanced: fails.append(f'chemistry violation; scene {sid} is marked expectBalanced but atom counts do not balance')
      if cfg.get('expectBalanced') is False and balanced: warns.append(f'chemistry scene {sid} is marked unbalanced but atom counts already balance')
    # Discipline-pack and discipline-native widget gates.
    if True:
     meta=course_data.get('meta') or {}; pack=meta.get('disciplinePack'); secondary=meta.get('secondaryPacks') or []
     allowed_packs={'mathematics','physics','chemistry','biology','computer-science','ml-ai','statistics','social-science','humanities','language','geography','procedural-vocational'}
     if pack not in allowed_packs: fails.append(f'discipline-pack violation; substantial course needs canonical meta.disciplinePack, got {pack!r}')
     if not isinstance(secondary,list): fails.append('discipline-pack violation; meta.secondaryPacks must be a list')
     elif len(secondary)>2: fails.append('discipline-pack violation; use at most two secondary packs')
     elif any(x not in allowed_packs for x in secondary): fails.append('discipline-pack violation; secondaryPacks contains unknown pack id')
     active={pack,*secondary} if pack else set(secondary)
     native_owner={'geometry-lab':'mathematics','solid-geometry-lab':'mathematics','space-geometry-lab':'mathematics','fbd-lab':'physics','circuit-lab':'physics','molecule-lab':'chemistry','genetics-lab':'biology','stats-lab':'statistics','search-tree-lab':'ml-ai','ml-boundary-lab':'ml-ai','map-lab':'geography','data-structure-lab':'computer-science','recursion-lab':'computer-science','complexity-lab':'computer-science','cloze-lab':'language','sentence-builder-lab':'language','grammar-tree-lab':'language','source-comparison-lab':'humanities','argument-map-lab':'humanities','causal-dag-lab':'social-science','evidence-matrix-lab':'social-science'}
     for sc in course_data.get('scenes',[]):
      c=sc.get('content') or {}; wt=c.get('widgetType'); cfg=c.get('widgetConfig') or {}; sid=sc.get('id','?')
      owner=native_owner.get(wt)
      if owner and owner not in active: fails.append(f'discipline-pack violation; scene {sid} uses {wt} but pack {owner} is not active')
      if wt=='geometry-lab':
       b=cfg.get('bounds') or {}; pts=cfg.get('points') or []; meas=cfg.get('measurements') or []
       if not all(k in b for k in ['xmin','xmax','ymin','ymax']) or not (b.get('xmin',0)<b.get('xmax',0) and b.get('ymin',0)<b.get('ymax',0)): fails.append(f'geometry-lab violation; scene {sid} needs valid fixed bounds')
       ids={x.get('id') for x in pts if isinstance(x,dict)}
       if len(ids)<2 or None in ids: fails.append(f'geometry-lab violation; scene {sid} needs at least two stable point ids')
       if not any(isinstance(x,dict) and x.get('draggable') for x in pts): fails.append(f'geometry-lab violation; scene {sid} needs at least one draggable point')
       if not meas: fails.append(f'geometry-lab violation; scene {sid} needs at least one measurable relation')
       for m in meas:
        if m.get('kind') not in {'distance','slope'} or m.get('from') not in ids or m.get('to') not in ids: fails.append(f'geometry-lab violation; scene {sid} has invalid measurement')
      if wt=='solid-geometry-lab':
       shapes=cfg.get('shapes') or []
       allowed={'prism','pyramid','cylinder','cone','sphere','frustum-pyramid','frustum-cone'}
       if len(shapes)<2: fails.append(f'solid-geometry-lab violation; scene {sid} needs at least two selectable solid models')
       for sh in shapes:
        if sh.get('kind') not in allowed: fails.append(f'solid-geometry-lab violation; scene {sid} shape {sh.get("id","?")} has unsupported kind')
        if not sh.get('id') or not sh.get('label'): fails.append(f'solid-geometry-lab violation; scene {sid} shapes need stable id and label')
        if not (sh.get('parameters') or []): fails.append(f'solid-geometry-lab violation; scene {sid} shape {sh.get("id","?")} needs adjustable parameters')
        if sh.get('formula') and not _valid_formula_obj(sh.get('formula')): fails.append(f'math-typesetting violation; solid-geometry-lab scene {sid} shape {sh.get("id","?")} formula lacks MathML+fallback')
       if not cfg.get('experiments') and not any((sh.get('experiments') or []) for sh in shapes): fails.append(f'solid-geometry-lab violation; scene {sid} needs control-variable experiment prompts')
      if wt=='space-geometry-lab':
       qs=cfg.get('questions') or []
       if len(qs)<3: fails.append(f'space-geometry-lab violation; scene {sid} needs at least three spatial-relation questions')
       allowed_rel={'parallel','intersect','skew','contained','perpendicular','line-plane-parallel','line-plane-intersect','plane-plane-parallel','plane-plane-intersect'}
       for q in qs:
        if not q.get('left') or not q.get('right') or q.get('answer') not in allowed_rel: fails.append(f'space-geometry-lab violation; scene {sid} question {q.get("id","?")} needs two objects and a canonical relation')
        opts={o.get('id') if isinstance(o,dict) else o for o in (q.get('options') or cfg.get('relationOptions') or [])}
        if q.get('answer') not in opts: fails.append(f'space-geometry-lab violation; scene {sid} question {q.get("id","?")} answer must appear among options')
      if wt=='fbd-lab':
       forces=cfg.get('candidateForces') or []; ids={x.get('id') for x in forces if isinstance(x,dict)}; target=set(cfg.get('targetForceIds') or [])
       if len(forces)<2 or not target: fails.append(f'fbd-lab violation; scene {sid} needs candidate forces and non-empty targetForceIds')
       if not target.issubset(ids): fails.append(f'fbd-lab violation; scene {sid} targetForceIds must reference candidates')
       for f in forces:
        if not f.get('source') or not f.get('direction'): fails.append(f'fbd-lab violation; scene {sid} force {f.get("id","?")} needs interaction source and direction')
      if wt=='circuit-lab':
       rs=cfg.get('resistors') or []
       if cfg.get('kind') not in {'series','parallel'}: fails.append(f'circuit-lab violation; scene {sid} kind must be series or parallel')
       if not isinstance(cfg.get('sourceVoltage'),(int,float)) or cfg.get('sourceVoltage')<=0: fails.append(f'circuit-lab violation; scene {sid} needs positive sourceVoltage')
       if not rs: fails.append(f'circuit-lab violation; scene {sid} needs resistors')
       for r in rs:
        if r.get('unit','Ω')!='Ω' or r.get('min') is None or r.get('max') is None: fails.append(f'circuit-lab violation; scene {sid} resistor {r.get("id","?")} needs Ω unit and min/max')
       if not cfg.get('assumption'): warns.append(f'circuit-lab scene {sid} should state ideal-model assumptions')
      if wt=='molecule-lab':
       atoms=cfg.get('atoms') or []; bonds=cfg.get('bonds') or []; ids={a.get('id') for a in atoms if isinstance(a,dict)}
       if len(atoms)<2 or not bonds: fails.append(f'molecule-lab violation; scene {sid} needs atoms and bonds')
       for a in atoms:
        if not a.get('element') or any(k not in a for k in ['x','y','z']): fails.append(f'molecule-lab violation; scene {sid} atom {a.get("id","?")} needs element/x/y/z')
       for b in bonds:
        if b.get('from') not in ids or b.get('to') not in ids: fails.append(f'molecule-lab violation; scene {sid} bond references unknown atom')
       if not cfg.get('disclaimer'): fails.append(f'molecule-lab violation; scene {sid} needs geometry/scale disclaimer')
      if wt=='genetics-lab':
       allowed=cfg.get('allowedGenotypes') or []
       if len(allowed)<2 or cfg.get('parentA') not in allowed or cfg.get('parentB') not in allowed: fails.append(f'genetics-lab violation; scene {sid} parents must belong to allowedGenotypes')
       if not cfg.get('phenotypeMap'): fails.append(f'genetics-lab violation; scene {sid} needs explicit genotype→phenotype rule')
      if wt=='stats-lab':
       if (cfg.get('distribution') or 'normal')!='normal': fails.append(f'stats-lab violation; scene {sid} currently supports distribution normal')
       if not isinstance(cfg.get('sd'),(int,float)) or cfg.get('sd')<=0: fails.append(f'stats-lab violation; scene {sid} needs positive sd')
       if not cfg.get('interpretationPrompt'): fails.append(f'stats-lab violation; scene {sid} needs interpretationPrompt')
      if wt=='search-tree-lab':
       steps=cfg.get('steps') or []
       if len(steps)<2 or not cfg.get('algorithm'): fails.append(f'search-tree-lab violation; scene {sid} needs algorithm and at least two trace steps')
       if len(cfg.get('nodes') or [])<2 or not (cfg.get('edges') or []): fails.append(f'search-tree-lab violation; scene {sid} needs explicit tree nodes/edges')
       for i,st in enumerate(steps,1):
        if 'current' not in st or 'open' not in st or 'closed' not in st: fails.append(f'search-tree-lab violation; scene {sid} step {i} needs current/open/closed')
      if wt=='ml-boundary-lab':
       pts=cfg.get('points') or []
       if len(pts)<4: fails.append(f'ml-boundary-lab violation; scene {sid} needs at least four labeled points')
       if any(p.get('label') not in {0,1} or 'x' not in p or 'y' not in p for p in pts): fails.append(f'ml-boundary-lab violation; scene {sid} points need x/y and binary label')
       if not cfg.get('dataNote'): fails.append(f'ml-boundary-lab violation; scene {sid} needs dataNote describing synthetic/observed provenance')
      if wt=='map-lab':
       prov=cfg.get('provenance'); pts=cfg.get('points') or []; feats=cfg.get('features') or []
       if cfg.get('verified') is not True or not prov: fails.append(f'map-lab violation; scene {sid} requires verified:true and provenance')
       if not (pts or feats): fails.append(f'map-lab violation; scene {sid} needs embedded geographic features/points')
       if True:
        if cfg.get('projection') not in {'equirectangular','mercator'}: fails.append(f'geography-pack violation; scene {sid} needs a canonical projection')
        if not cfg.get('coordinateSystem') or not cfg.get('scaleNote'): fails.append(f'geography-pack violation; scene {sid} needs coordinateSystem and scaleNote')
        if not isinstance(prov,dict) or not prov.get('title') or not prov.get('edition') or not prov.get('sourceRef'): fails.append(f'geography-pack violation; scene {sid} provenance must be structured with title/edition/sourceRef')
        elif prov.get('sourceRef') not in source_ids: fails.append(f'geography-pack violation; scene {sid} provenance sourceRef is not declared in course.sources')
        if len(pts)<3 and not feats: fails.append(f'geography-pack violation; scene {sid} needs enough embedded geography for spatial comparison')
        for j,pnt in enumerate(pts,1):
         if not pnt.get('id') or not pnt.get('name') or not pnt.get('sourceRef'): fails.append(f'geography-pack violation; scene {sid} point {j} needs id/name/sourceRef')
         elif pnt.get('sourceRef') not in source_ids: fails.append(f'geography-pack violation; scene {sid} point {pnt.get("id",j)} sourceRef is not declared in course.sources')
         lon=pnt.get('lon'); lat=pnt.get('lat')
         if not isinstance(lon,(int,float)) or not -180<=lon<=180 or not isinstance(lat,(int,float)) or not -90<=lat<=90: fails.append(f'geography-pack violation; scene {sid} point {pnt.get("id",j)} has invalid lon/lat')
        if feats and not cfg.get('boundaryPolicy'): fails.append(f'geography-pack violation; scene {sid} renders polygons/features but has no boundaryPolicy')
        if not cfg.get('spatialTask'): fails.append(f'geography-pack violation; scene {sid} needs a learner spatialTask')
      if wt=='data-structure-lab':
       kind=cfg.get('kind'); initial=cfg.get('initial') or []; max_size=cfg.get('maxSize')
       if kind not in {'stack','queue'}: fails.append(f'computer-science-pack violation; scene {sid} data-structure kind must be stack or queue')
       if not isinstance(max_size,int) or not 2<=max_size<=20 or len(initial)>max_size: fails.append(f'computer-science-pack violation; scene {sid} needs valid maxSize and initial state')
       if not cfg.get('prompt') or not cfg.get('invariant'): fails.append(f'computer-science-pack violation; scene {sid} data-structure lab needs prompt and invariant')
       elif kind=='stack' and 'LIFO' not in cfg.get('invariant',''): fails.append(f'computer-science-pack violation; scene {sid} stack invariant must state LIFO')
       elif kind=='queue' and 'FIFO' not in cfg.get('invariant',''): fails.append(f'computer-science-pack violation; scene {sid} queue invariant must state FIFO')
      if wt=='recursion-lab':
       if cfg.get('model')!='factorial': fails.append(f'computer-science-pack violation; scene {sid} canonical recursion-lab currently supports model factorial')
       if not isinstance(cfg.get('n'),int) or not 1<=cfg.get('n')<=7: fails.append(f'computer-science-pack violation; scene {sid} recursion n must be 1..7')
       if not cfg.get('baseCase') or not cfg.get('recursiveCase'): fails.append(f'computer-science-pack violation; scene {sid} recursion lab needs baseCase and recursiveCase')
      if wt=='complexity-lab':
       models=cfg.get('models') or []; kinds=[m.get('kind') for m in models if isinstance(m,dict)]; allowed={'constant','log2','linear','nlogn','quadratic'}
       if len(models)<3 or any(k not in allowed for k in kinds) or len(set(kinds))!=len(kinds): fails.append(f'computer-science-pack violation; scene {sid} complexity lab needs >=3 distinct canonical models')
       if not isinstance(cfg.get('max'),(int,float)) or cfg.get('max')<=8: fails.append(f'computer-science-pack violation; scene {sid} complexity lab needs meaningful max input size')
       if not cfg.get('interpretationPrompt') or not cfg.get('assumption') or cfg.get('scale')!='log1p' or not cfg.get('scaleNote'): fails.append(f'computer-science-pack violation; scene {sid} complexity lab needs interpretationPrompt, assumption and disclosed log1p scale')
      if wt=='cloze-lab':
       segs=cfg.get('segments') or []; blanks=[]
       for seg in segs:
        if isinstance(seg,dict):
         b=seg.get('blank') or (seg if seg.get('id') else None)
         if b: blanks.append(b)
       if not cfg.get('prompt') or not blanks: fails.append(f'language-pack violation; scene {sid} cloze-lab needs prompt and at least one blank')
       ids=[]
       for b in blanks:
        bid=b.get('id'); answers=b.get('answers') or []
        if not bid or bid in ids: fails.append(f'language-pack violation; scene {sid} cloze blank ids must be stable and unique')
        ids.append(bid)
        if not answers or any(not str(a).strip() for a in answers): fails.append(f'language-pack violation; scene {sid} cloze blank {bid or "?"} needs non-empty accepted answers')
       if len(cfg.get('strategies') or [])<2: fails.append(f'language-pack violation; scene {sid} cloze-lab needs at least two strategy cues')
      if wt=='sentence-builder-lab':
       toks=cfg.get('tokens') or []; ids=[x.get('id') for x in toks if isinstance(x,dict)]; target=cfg.get('targetOrder') or []
       if len(toks)<3 or len(ids)!=len(set(ids)) or None in ids: fails.append(f'language-pack violation; scene {sid} sentence-builder needs >=3 unique token ids')
       if sorted(target)!=sorted(ids): fails.append(f'language-pack violation; scene {sid} targetOrder must use every token exactly once')
       if not cfg.get('prompt') or not cfg.get('correctFeedback') or not cfg.get('incorrectFeedback'): fails.append(f'language-pack violation; scene {sid} sentence-builder needs prompt and differentiated feedback')
      if wt=='grammar-tree-lab':
       nodes=cfg.get('nodes') or []; ids={x.get('id') for x in nodes if isinstance(x,dict)}; roots=[x for x in nodes if isinstance(x,dict) and not x.get('parentId')]
       if len(nodes)<3 or len(roots)!=1 or None in ids: fails.append(f'language-pack violation; scene {sid} grammar-tree needs >=3 nodes and exactly one root')
       for n in nodes:
        if n.get('parentId') and n.get('parentId') not in ids: fails.append(f'language-pack violation; scene {sid} grammar node {n.get("id","?")} references unknown parent')
        if not n.get('role') or not n.get('explanation'): fails.append(f'language-pack violation; scene {sid} grammar node {n.get("id","?")} needs role and explanation')
      if wt=='source-comparison-lab':
       ss=cfg.get('sources') or []; lenses=cfg.get('lenses') or []
       if len(ss)<2 or len(lenses)<2: fails.append(f'humanities-pack violation; scene {sid} source-comparison needs >=2 sources and >=2 comparison lenses')
       for s in ss:
        if s.get('textStatus') not in {'quote','paraphrase','summary','translation'}: fails.append(f'humanities-pack violation; scene {sid} source {s.get("id","?")} must label textStatus')
        if not s.get('sourceRef') or s.get('sourceRef') not in source_ids: fails.append(f'humanities-pack violation; scene {sid} source {s.get("id","?")} needs declared sourceRef')
        if not s.get('context') or not s.get('perspective'): fails.append(f'humanities-pack violation; scene {sid} source {s.get("id","?")} needs context and perspective')
        analysis=s.get('analysis') or {}
        for lens in lenses:
         if not analysis.get(lens.get('id')): fails.append(f'humanities-pack violation; scene {sid} source {s.get("id","?")} lacks analysis for lens {lens.get("id","?")}')
       if not cfg.get('synthesisPrompt'): fails.append(f'humanities-pack violation; scene {sid} needs a synthesisPrompt that compares rather than isolates sources')
      if wt=='argument-map-lab':
       nodes=cfg.get('nodes') or []; edges=cfg.get('edges') or []; ids={n.get('id') for n in nodes if isinstance(n,dict)}; kinds={'claim','evidence','objection','context','qualification'}
       if len(nodes)<3 or not edges: fails.append(f'humanities-pack violation; scene {sid} argument-map needs nodes and relations')
       for n in nodes:
        if n.get('kind') not in kinds: fails.append(f'humanities-pack violation; scene {sid} argument node {n.get("id","?")} has invalid kind')
        if n.get('kind')=='evidence' and (not n.get('sourceRef') or n.get('sourceRef') not in source_ids): fails.append(f'humanities-pack violation; scene {sid} evidence node {n.get("id","?")} needs sourceRef')
       for e in edges:
        if e.get('from') not in ids or e.get('to') not in ids or e.get('relation') not in {'support','oppose','qualify','contextualize'}: fails.append(f'humanities-pack violation; scene {sid} has invalid argument relation')
       if not cfg.get('boundary'): fails.append(f'humanities-pack violation; scene {sid} must distinguish argument structure from proof/fact')
      if wt=='causal-dag-lab':
       nodes=cfg.get('nodes') or []; edges=cfg.get('edges') or []; ids={n.get('id') for n in nodes if isinstance(n,dict)}; roles=[n.get('role') for n in nodes if isinstance(n,dict)]
       if roles.count('exposure')!=1 or roles.count('outcome')!=1: fails.append(f'social-science-pack violation; scene {sid} causal DAG needs exactly one exposure and one outcome')
       if len(nodes)<3 or not edges: fails.append(f'social-science-pack violation; scene {sid} causal DAG needs >=3 nodes and edges')
       graph={i:[] for i in ids}
       for e in edges:
        if e.get('from') not in ids or e.get('to') not in ids: fails.append(f'social-science-pack violation; scene {sid} DAG edge references unknown node')
        else: graph[e['from']].append(e['to'])
       seen=set(); stack=set()
       def _dfs(v):
        if v in stack: return False
        if v in seen: return True
        seen.add(v); stack.add(v)
        ok=all(_dfs(w) for w in graph.get(v,[])); stack.remove(v); return ok
       if any(not _dfs(v) for v in list(ids) if v not in seen): fails.append(f'social-science-pack violation; scene {sid} causal graph contains a directed cycle')
       cands=cfg.get('adjustmentCandidates') or []; valid=cfg.get('validAdjustmentSets') or []
       if not cands or not valid: fails.append(f'social-science-pack violation; scene {sid} causal DAG needs adjustmentCandidates and validAdjustmentSets')
       if any(x not in ids for x in cands) or any(any(x not in ids for x in s) for s in valid): fails.append(f'social-science-pack violation; scene {sid} adjustment sets reference unknown variables')
       if not cfg.get('dataNote') or not cfg.get('causalClaimBoundary'): fails.append(f'social-science-pack violation; scene {sid} causal DAG needs dataNote and causalClaimBoundary')
      if wt=='evidence-matrix-lab':
       rows=cfg.get('rows') or []
       if len(rows)<2: fails.append(f'social-science-pack violation; scene {sid} evidence matrix needs at least two evidence rows')
       for r in rows:
        if not r.get('sourceRef') or r.get('sourceRef') not in source_ids: fails.append(f'social-science-pack violation; scene {sid} evidence row {r.get("id","?")} needs declared sourceRef')
        if not r.get('design') or not r.get('claimScope') or not r.get('limitation') or not r.get('evidenceType'): fails.append(f'social-science-pack violation; scene {sid} evidence row {r.get("id","?")} needs design/evidenceType/claimScope/limitation')
       if not cfg.get('boundary'): fails.append(f'social-science-pack violation; scene {sid} evidence matrix needs explicit inference boundary')
    if True:
     widgets=[((sc.get('content') or {}).get('widgetType')) for sc in course_data.get('scenes',[])]
     if pack=='geography' and 'map-lab' not in widgets: fails.append('geography-pack violation; validated-native geography course needs at least one map-lab')
     if pack=='computer-science' and not any(w in {'data-structure-lab','recursion-lab','complexity-lab','code'} for w in widgets): fails.append('computer-science-pack violation; course needs at least one native CS state/algorithm lab')
    if True:
     widgets=[((sc.get('content') or {}).get('widgetType')) for sc in course_data.get('scenes',[])]
     if pack=='language' and not any(w in {'cloze-lab','sentence-builder-lab','grammar-tree-lab'} for w in widgets): fails.append('language-pack violation; validated-native language course needs a native language lab')
     if pack=='humanities' and not any(w in {'source-comparison-lab','argument-map-lab'} for w in widgets): fails.append('humanities-pack violation; validated-native humanities course needs source-comparison or argument-map')
     if pack=='social-science' and not any(w in {'causal-dag-lab','evidence-matrix-lab'} for w in widgets): fails.append('social-science-pack violation; validated-native social-science course needs causal/evidence native lab')
    # Source inventory + deliberate-practice + independent mastery gate.
    if True:
     meta=course_data.get('meta') or {}; policy=meta.get('practicePolicy') or {}
     coverage=course_data.get('sourceCoverage') or {}
     if coverage:
      if coverage.get('status') not in {'complete','partial'}: fails.append('source-coverage violation; status must be complete or partial')
      if coverage.get('status')=='partial' and not (coverage.get('omissions') or []): fails.append('source-coverage violation; partial source coverage must list omissions')
     if policy.get('mode')=='mastery-loop':
      inv=course_data.get('contentInventory') or []
      if not inv: fails.append('mastery-loop violation; contentInventory is required')
      scene_ids={sc.get('id') for sc in course_data.get('scenes',[]) if sc.get('id')}
      examples=set(); exercises=set(); questions={}; explain_scenes={}
      for sc in course_data.get('scenes',[]):
       k=sc.get('knowledge') or (sc.get('content') or {}).get('knowledge') or {}
       for ex in k.get('workedExamples') or []:
        if isinstance(ex,dict) and ex.get('id'): examples.add(ex.get('id'))
       for b in k.get('semanticBlocks') or []:
        if isinstance(b,dict) and b.get('kind')=='example' and b.get('id'): examples.add(b.get('id'))
        if isinstance(b,dict) and b.get('kind')=='exercise' and b.get('id'): exercises.add(b.get('id'))
       if sc.get('type') in {'quiz','mastery'}:
        for q in (sc.get('content') or {}).get('items') or []:
         if isinstance(q,dict) and q.get('id'): questions[q['id']]=q
       if sc.get('type')=='explain-back':
        for cid in (sc.get('content') or {}).get('conceptIds') or []: explain_scenes.setdefault(cid,[]).append(sc.get('id'))
      all_practice=set(questions)|exercises
      min_ex=int(policy.get('minWorkedExamplesPerCore',2)); min_pr=int(policy.get('minPracticeItemsPerCore',3))
      for item in inv:
       if not isinstance(item,dict): fails.append('mastery-loop violation; contentInventory entries must be objects'); continue
       iid=item.get('id') or '?'; imp=item.get('importance','support')
       if not item.get('label') or not item.get('sourceLocator'): fails.append(f'mastery-loop violation; inventory item {iid} needs label and sourceLocator')
       if any(x not in scene_ids for x in (item.get('sceneIds') or [])): fails.append(f'mastery-loop violation; inventory item {iid} references unknown scene')
       if any(x not in examples for x in (item.get('exampleRefs') or [])): fails.append(f'mastery-loop violation; inventory item {iid} references unknown worked example')
       if any(x not in all_practice for x in (item.get('practiceRefs') or [])): fails.append(f'mastery-loop violation; inventory item {iid} references unknown practice item')
       if imp=='core':
        if len(item.get('sceneIds') or [])<1: fails.append(f'mastery-loop violation; core inventory item {iid} has no teaching scene')
        if len(item.get('exampleRefs') or [])<min_ex: fails.append(f'mastery-loop violation; core inventory item {iid} needs at least {min_ex} worked examples')
        if len(item.get('practiceRefs') or [])<min_pr: fails.append(f'mastery-loop violation; core inventory item {iid} needs at least {min_pr} practice items')
        if policy.get('requireExplainBack') and not (item.get('explainBackRefs') or explain_scenes.get(iid)): fails.append(f'mastery-loop violation; core inventory item {iid} needs explain-back coverage')
      if policy.get('requireCumulativeRetrieval'):
       cumulative=[]
       for sc in course_data.get('scenes',[]):
        c=sc.get('content') or {}
        if sc.get('type')=='quiz' and c.get('cumulative'):
         objs={oid for q in c.get('items') or [] for oid in (q.get('objectiveIds') or [])}; cumulative.append((sc.get('id'),objs))
       if not cumulative or not any(len(objs)>=2 for _,objs in cumulative): fails.append('mastery-loop violation; cumulative retrieval quiz must mix at least two objectives')
      explain=[sc for sc in course_data.get('scenes',[]) if sc.get('type')=='explain-back']
      if policy.get('requireDiagnostic'):
       diagnostics=[sc for sc in course_data.get('scenes',[]) if sc.get('type')=='quiz' and (sc.get('content') or {}).get('diagnostic')]
       if not diagnostics: fails.append('mastery-loop violation; requireDiagnostic:true but no diagnostic quiz exists')
      if policy.get('requireExplainBack') and not explain: fails.append('mastery-loop violation; at least one explain-back scene is required')
      for sc in explain:
       c=sc.get('content') or []
       if len(c.get('requiredIdeas') or [])<2 or len(c.get('commonGaps') or [])<3: fails.append(f'explain-back violation; scene {sc.get("id","?")} needs >=2 requiredIdeas and >=3 commonGaps')
      mastery=[sc for sc in course_data.get('scenes',[]) if sc.get('type')=='mastery' and (sc.get('content') or {}).get('masteryGate')]
      if not mastery: fails.append('mastery-loop violation; deterministic masteryGate scene is required')
      else:
       gate=(mastery[-1].get('content') or {}).get('masteryGate') or {}; items=(mastery[-1].get('content') or {}).get('items') or []; ids={q.get('id') for q in items if isinstance(q,dict)}
       if not (0<float(gate.get('threshold',0))<=1): fails.append('mastery-gate violation; threshold must be in (0,1]')
       obj_ids={o if isinstance(o,str) else o.get('id') for o in course_data.get('objectives') or []}
       rules=gate.get('objectiveRules') or []; ruled={r.get('objectiveId') for r in rules}
       if obj_ids and not obj_ids.issubset(ruled): fails.append('mastery-gate violation; every course objective needs an objectiveRule')
       for r in rules:
        qids=r.get('questionIds') or []
        if len(qids)<2: fails.append(f'mastery-gate violation; objective {r.get("objectiveId","?")} needs at least two gate questions')
        if any(q not in ids for q in qids): fails.append(f'mastery-gate violation; objective {r.get("objectiveId","?")} references unknown question')
        if int(r.get('minCorrect',0))<1 or int(r.get('minCorrect',0))>len(qids): fails.append(f'mastery-gate violation; objective {r.get("objectiveId","?")} has invalid minCorrect')
        if policy.get('requireTwoNovelTransfers'):
         qmap={q.get('id'):q for q in items if isinstance(q,dict)}
         if len(qids)<2 or int(r.get('minCorrect',0))<2: fails.append(f'mastery-gate violation; objective {r.get("objectiveId","?")} must pass at least two transfer questions')
         if any(not (qmap.get(qid) or {}).get('novelTransfer') for qid in qids): fails.append(f'mastery-gate violation; objective {r.get("objectiveId","?")} gate questions must declare novelTransfer:true')
      # deliberate-practice semantics on ordinary quizzes
      levels={'diagnostic','guided','independent','transfer','retrieval'}
      for sc in course_data.get('scenes',[]):
       if sc.get('type')!='quiz': continue
       c=sc.get('content') or {}
       for q in c.get('items') or []:
        pl=q.get('practiceLevel') or c.get('practiceLevel')
        if pl and pl not in levels: fails.append(f'practice-ladder violation; question {q.get("id","?")} uses unsupported practiceLevel {pl}')
        if q.get('id') in questions and not (q.get('objectiveIds') or []): fails.append(f'practice-ladder violation; question {q.get("id","?")} needs objectiveIds')
    # Pedagogical figures + example diversity + real practice progression.
    if True:
     meta=course_data.get('meta') or {}; policy=meta.get('practicePolicy') or {}; fig_policy=meta.get('figurePolicy') or {}; pack=meta.get('disciplinePack')
     allowed_kinds={'concept','compare','step','reasoning','misconception'}
     allowed_templates={'solid-family','oblique-projection','surface-net','spatial-relations','bridge-line','generic-flow','motion-components'}
     figure_map={}; figure_scene={}; examples_map={}; practice_map={}
     for sc in course_data.get('scenes',[]):
      sid=sc.get('id','?'); k=sc.get('knowledge') or (sc.get('content') or {}).get('knowledge') or {}
      for f in k.get('pedagogicalFigures') or []:
       if not isinstance(f,dict): fails.append(f'pedagogical-figure violation; scene {sid} contains a non-object figure'); continue
       fid=f.get('id')
       if not fid: fails.append(f'pedagogical-figure violation; scene {sid} figure needs stable id'); continue
       if fid in figure_map: fails.append(f'pedagogical-figure violation; duplicate figure id {fid}')
       figure_map[fid]=f; figure_scene[fid]=sid
       if f.get('figureKind') not in allowed_kinds: fails.append(f'pedagogical-figure violation; figure {fid} has unsupported figureKind')
       if f.get('template') not in allowed_templates: fails.append(f'pedagogical-figure violation; figure {fid} has unsupported template {f.get("template")}')
       for req in ['title','learningPurpose','caption']:
        if not str(f.get(req,'')).strip(): fails.append(f'pedagogical-figure violation; figure {fid} needs {req}')
       if f.get('sourceRef') and f.get('sourceRef') not in source_ids: fails.append(f'pedagogical-figure violation; figure {fid} references unknown source {f.get("sourceRef")}')
       if fig_policy.get('requireSourceBinding') and pack=='mathematics' and not f.get('sourceRef'): fails.append(f'pedagogical-figure violation; figure {fid} needs sourceRef under requireSourceBinding')
       local_figure_ids={str(f.get('id')) for f in (k.get('pedagogicalFigures') or []) if isinstance(f,dict) and f.get('id')}
       for ex in k.get('workedExamples') or []:
        if isinstance(ex,dict):
         if ex.get('id'): examples_map[ex['id']]=ex
         ref=ex.get('figureRef')
         if ref and str(ref) not in local_figure_ids: fails.append(f'worked-example violation; scene {sid} example {ex.get("id","?")} figureRef {ref} must resolve within the same knowledge block')
         need_visual=str(ex.get('visualNeed') or '').strip().casefold()
         direct_first=fig_policy.get('mode')=='direct-first'
         visual_needs={'spatial','mechanical','structural','process','dynamic','geometry'}
         if direct_first and (fig_policy.get('requireWorkedExampleFigure') is True or need_visual in visual_needs) and not ref: fails.append(f'worked-example violation; scene {sid} example {ex.get("id","?")} needs figureRef under direct-first policy')
      for b in k.get('semanticBlocks') or []:
       if isinstance(b,dict) and b.get('kind')=='example' and b.get('id'): examples_map[b['id']]=b
       if isinstance(b,dict) and b.get('kind')=='exercise' and b.get('id'): practice_map[b['id']]=b
      if sc.get('type') in {'quiz','mastery'}:
       for q in (sc.get('content') or {}).get('items') or []:
        if isinstance(q,dict) and q.get('id'): practice_map[q['id']]=q
     if fig_policy.get('mode')=='geometry-native':
      if pack!='mathematics': fails.append('pedagogical-figure violation; geometry-native figurePolicy requires mathematics Pack')
      min_fig=int(fig_policy.get('minFiguresPerCore',2))
      for item in course_data.get('contentInventory') or []:
       if not isinstance(item,dict) or item.get('importance','support')!='core': continue
       iid=item.get('id','?'); refs=item.get('figureRefs') or []
       if len(refs)<min_fig: fails.append(f'pedagogical-figure violation; core inventory item {iid} needs at least {min_fig} pedagogical figures')
       if any(x not in figure_map for x in refs): fails.append(f'pedagogical-figure violation; inventory item {iid} references unknown figure')
       kinds={figure_map[x].get('figureKind') for x in refs if x in figure_map}
       if fig_policy.get('requireKindDiversity'):
        if not kinds.intersection({'concept','step','reasoning'}): fails.append(f'pedagogical-figure violation; inventory item {iid} needs a representation-building figure')
        if not kinds.intersection({'compare','misconception'}): fails.append(f'pedagogical-figure violation; inventory item {iid} needs a compare/misconception figure')
     if fig_policy.get('mode')=='direct-first':
      mind_map_kinds={'mind-map','mindmap','knowledge-graph','hierarchy','hierarchical'}; valid_purposes={'hierarchy','network','taxonomy','dependency','state-machine','argument-structure'}; mind_maps=[]
      for sc in course_data.get('scenes',[]):
       c=sc.get('content') or {}; cfg=c.get('widgetConfig') or {}
       if c.get('widgetType')!='diagram': continue
       kind=str(cfg.get('kind') or '').strip().casefold()
       if kind not in mind_map_kinds: continue
       purpose=str(cfg.get('visualPurpose') or '').strip().casefold(); justification=str(cfg.get('mindMapJustification') or '').strip()
       if purpose not in valid_purposes: fails.append(f'figure-policy violation; mind-map-like diagram {sc.get("id","?")} needs visualPurpose hierarchy/network/taxonomy/dependency/state-machine/argument-structure')
       if not justification: fails.append(f'figure-policy violation; mind-map-like diagram {sc.get("id","?")} needs mindMapJustification')
       mind_maps.append((sc.get('id','?'),bool(justification)))
      try: max_mind_maps=max(0,int(fig_policy.get('maxMindMapLikeDiagrams',1)))
      except Exception: max_mind_maps=1; fails.append('figure-policy violation; maxMindMapLikeDiagrams must be an integer')
      if len(mind_maps)>max_mind_maps:
       extras=mind_maps[max_mind_maps:]
       if any(not justified for _,justified in extras): fails.append(f'figure-policy violation; at most {max_mind_maps} mind-map-like diagram(s) may be used without a justified exception')
      if policy.get('mode')=='mastery-loop':
       if policy.get('requireExampleContrast'):
        for item in course_data.get('contentInventory') or []:
         if not isinstance(item,dict) or item.get('importance','support')!='core': continue
         iid=item.get('id','?'); refs=item.get('exampleRefs') or []; variants={str((examples_map.get(x) or {}).get('variantType','')) for x in refs}
         if 'standard' not in variants: fails.append(f'practice-progression violation; core inventory item {iid} needs a standard worked example')
         if not variants.intersection({'contrast','boundary','misconception','reverse'}): fails.append(f'practice-progression violation; core inventory item {iid} needs a contrast/boundary/misconception worked example')
      if policy.get('requirePracticeProgression'):
        for item in course_data.get('contentInventory') or []:
         if not isinstance(item,dict) or item.get('importance','support')!='core': continue
         iid=item.get('id','?'); refs=item.get('practiceRefs') or []; levels={str((practice_map.get(x) or {}).get('practiceLevel','')) for x in refs}
         if 'guided' not in levels: fails.append(f'practice-progression violation; core inventory item {iid} needs guided practice')
         if 'independent' not in levels: fails.append(f'practice-progression violation; core inventory item {iid} needs independent practice')
         if not levels.intersection({'transfer','retrieval'}): fails.append(f'practice-progression violation; core inventory item {iid} needs transfer/retrieval practice')
    # Learner-first surface + true process animation contracts.
    if True:
     meta=course_data.get('meta') or {}; learner_policy=meta.get('learnerSurfacePolicy') or {}; anim_policy=meta.get('animationPolicy') or {}
     if learner_policy.get('hideEngineering'):
      learner_parts=[]
      def _learner_strings(o):
       if isinstance(o,str): learner_parts.append(o)
       elif isinstance(o,dict):
        for v in o.values(): _learner_strings(v)
       elif isinstance(o,list):
        for v in o: _learner_strings(v)
      _learner_strings(course_data.get('scenes') or [])
      _learner_strings([meta.get('title',''),meta.get('subtitle','')])
      surface='\n'.join(learner_parts).lower()
      banned=['sourcecoverage','contentinventory','disciplinepack','schemaversion','validator','refinement bundle','automutation','mastery gate','codex','skill 版本','pack 规则']
      for term in banned:
       if term in surface: fails.append(f'learner-surface violation; engineering term "{term}" appears in learner-facing course content')
     process_count=0
     for sc in course_data.get('scenes',[]):
      c=sc.get('content') or {}; wt=c.get('widgetType'); cfg=c.get('widgetConfig') or {}; sid=sc.get('id','?')
      if wt=='process-animation':
       process_count+=1; actors=cfg.get('actors') or []; steps=cfg.get('steps') or []
       if not str(cfg.get('principle','')).strip(): fails.append(f'process-animation violation; scene {sid} needs principle')
       if len(actors)<1 or len(steps)<3: fails.append(f'process-animation violation; scene {sid} needs >=1 actor and >=3 process steps')
       ids=[a.get('id') for a in actors if isinstance(a,dict)]
       if len(ids)!=len(set(ids)) or any(not x for x in ids): fails.append(f'process-animation violation; scene {sid} actor ids must be stable and unique')
       idset=set(ids); amap={a.get('id'):a for a in actors if isinstance(a,dict) and a.get('id')}; dynamic_changes=0; prev=None
       motion_keys={'x','y','rotation','scale','w','h','r','x2','y2','face'}
       layout=cfg.get('layoutPolicy') or {}; canvas=cfg.get('canvas') or {}; W=float(canvas.get('width',760)); H=float(canvas.get('height',380)); safe=float(layout.get('safeMargin',0)); gap=float(layout.get('minGap',0))
       if anim_policy.get('preventVisualOverlap'):
        if not layout.get('preventOverlap'): fails.append(f'process-animation layout violation; scene {sid} must declare layoutPolicy.preventOverlap=true')
        if safe<float(anim_policy.get('minSafeMargin',20)): fails.append(f'process-animation layout violation; scene {sid} safeMargin is too small')
        if gap<float(anim_policy.get('minActorGap',10)): fails.append(f'process-animation layout violation; scene {sid} minGap is too small')
       def _bbox(actor,state):
        if float(state.get('opacity',1))<=0.05: return None
        typ=actor.get('type','circle'); x=float(state.get('x',actor.get('x',0))); y=float(state.get('y',actor.get('y',0))); scale=abs(float(state.get('scale',1)))
        if typ in {'line','track','text'}: return None
        if typ in {'circle','coin','sample-point','math-point','projection-marker','projectile','ion','electron','water-drop'}:
         defaults={'sample-point':24,'math-point':18,'projection-marker':16,'projectile':22,'ion':24,'electron':12,'water-drop':20}
         r=float(state.get('r',actor.get('r',defaults.get(typ,28))))*scale; return (x-r,y-r,x+r,y+r)
        dims={'molecule':(120,72),'energy-token':(82,42),'stack-frame':(150,58),'array-cell':(58,58),'pointer':(72,38),'air-mass':(130,72),'plate':(150,58),'vector':(96,38)}
        dw,dh=dims.get(typ,(100,56))
        w=float(state.get('w',actor.get('w',dw)))*scale; h=float(state.get('h',actor.get('h',dh)))*scale; return (x-w/2,y-h/2,x+w/2,y+h/2)
       def _separated(a,b,extra):
        return a[2]+extra<=b[0] or b[2]+extra<=a[0] or a[3]+extra<=b[1] or b[3]+extra<=a[1]
       for i,st in enumerate(steps):
        if not isinstance(st,dict) or not str(st.get('title','')).strip() or not str(st.get('caption',st.get('explanation',''))).strip(): fails.append(f'process-animation violation; scene {sid} step {i+1} needs title and caption')
        if not isinstance(st,dict) or any(not str(st.get(k,'')).strip() for k in ('semanticAction','whyItMatters','focus','changeSummary')): fails.append(f'process-animation semantics violation; scene {sid} step {i+1} needs semanticAction, whyItMatters, focus and changeSummary')
        if anim_policy.get('requireSpecificSteps') and (not str(st.get('focus','')).strip() or not str(st.get('changeSummary','')).strip()): fails.append(f'process-animation specificity violation; scene {sid} step {i+1} needs focus and changeSummary')
        states=(st.get('states') or {}) if isinstance(st,dict) else {}
        if any(aid not in idset for aid in states): fails.append(f'process-animation violation; scene {sid} step {i+1} references unknown actor')
        if layout.get('preventOverlap'):
         boxes={}
         for aid in idset:
          actor=amap.get(aid,{}) ; state_i=states.get(aid,{}) or {}; box=_bbox(actor,state_i)
          if box is None: continue
          boxes[aid]=box
          if box[0]<safe or box[1]<safe or box[2]>W-safe or box[3]>H-safe: fails.append(f'process-animation layout violation; scene {sid} step {i+1} actor {aid} leaves safe canvas')
         aids=list(boxes)
         for ia in range(len(aids)):
          for ib in range(ia+1,len(aids)):
           a_id,b_id=aids[ia],aids[ib]; aa,bb=amap.get(a_id,{}),amap.get(b_id,{})
           allowed=(aa.get('type')=='zone' and b_id in (aa.get('contains') or [])) or (bb.get('type')=='zone' and a_id in (bb.get('contains') or []))
           if not allowed:
            rels=((cfg.get('animationSemantics') or {}).get('semanticRelations') or [])
            overlap_types={'passes-through','touches','contains','enters','attached-to','points-to'}
            for rel in rels:
             if not isinstance(rel,dict) or rel.get('type') not in overlap_types: continue
             scoped={str(x) for x in (rel.get('whenSteps') or [])}
             if scoped and str(st.get('semanticAction','')) not in scoped: continue
             src=str(rel.get('source','')); tgts={str(x) for x in (rel.get('targets') or [])}
             if (a_id==src and b_id in tgts) or (b_id==src and a_id in tgts): allowed=True; break
           if not allowed and not _separated(boxes[a_id],boxes[b_id],gap): fails.append(f'process-animation layout violation; scene {sid} step {i+1} actors {a_id} and {b_id} overlap/crowd')
        if prev is not None:
         for aid in idset:
          a=prev.get(aid,{}) or {}; b=states.get(aid,{}) or {}
          if any(a.get(k)!=b.get(k) and (k in a or k in b) for k in motion_keys): dynamic_changes+=1
        prev=states
       if dynamic_changes<2: fails.append(f'process-animation violation; scene {sid} must animate actual position/shape/rotation changes, not only reveal labels or a mind map')
       if cfg.get('autoplay') is not False:
        for marker in ('requestAnimationFrame','process-play','process-replay','prefers-reduced-motion'):
         if marker not in text: fails.append(f'process-animation runtime violation; scene {sid} autoplay requires {marker}')
      if wt=='motion-lab' and 'requestAnimationFrame' not in text: fails.append(f'motion-lab runtime violation; scene {sid} requires requestAnimationFrame playback')
      if wt=='diagram' and (cfg.get('animation') or {}).get('enabled') and anim_policy.get('mode')=='process-first':
       fails.append(f'process-animation violation; scene {sid} uses staged diagram animation under process-first policy; use process-animation for motion and keep diagram static/step-reveal')
      if wt=='random-trial-lab':
       p0=cfg.get('theoreticalP')
       if p0 is None or not (0<=float(p0)<=1): fails.append(f'random-trial violation; scene {sid} needs theoreticalP in [0,1]')
       if int(cfg.get('maxTrials',0))<100: fails.append(f'random-trial violation; scene {sid} maxTrials should be at least 100')
       if len(cfg.get('experimentPrompts') or [])<2: fails.append(f'random-trial violation; scene {sid} needs at least two learner experiment prompts')
       if not str(cfg.get('boundary','')).strip(): fails.append(f'random-trial violation; scene {sid} needs a boundary explaining simulation variability')
     if anim_policy.get('requireProcessAnimation') and process_count<1: fails.append('process-animation violation; animationPolicy requires at least one process-animation scene')
    # Three-indicator learner quality + visual quality contracts.
    if True:
     meta=course_data.get('meta') or {}; qpol=meta.get('learnerQualityPolicy') or {}; vpol=meta.get('visualQualityPolicy') or {}
     if qpol.get('mode')=='three-indicator':
      if vpol.get('mode')!='reader-first-accessible': fails.append('visual-quality violation; three-indicator courses need visualQualityPolicy.mode=reader-first-accessible')
      if float(vpol.get('minTextContrast',0))<4.5: fails.append('visual-quality violation; minTextContrast must be at least 4.5')
      if float(vpol.get('minNonTextContrast',0))<3.0: fails.append('visual-quality violation; minNonTextContrast must be at least 3.0')
      if int(vpol.get('animationLabelMinPx',0))<14: fails.append('visual-quality violation; animationLabelMinPx must be at least 14')
      if vpol.get('avoidColorOnlyEncoding') is not True: fails.append('visual-quality violation; avoidColorOnlyEncoding must be true')
      if vpol.get('mobileAnimationStrategy')!='scroll-inside': fails.append('visual-quality violation; mobileAnimationStrategy must be scroll-inside')
     if qpol.get('mode')=='three-indicator':
      if not str(qpol.get('targetLearner','')).strip(): fails.append('learner-quality violation; targetLearner is required')
      # Explanation suitability: core scenes need mental model + example + misconception/boundary.
      for sc in course_data.get('scenes',[]):
       if sc.get('type') not in {'concept','interactive','discussion','pbl'} or not (sc.get('objectiveIds') or []): continue
       sid=sc.get('id','?'); k=sc.get('knowledge') or (sc.get('content') or {}).get('knowledge') or {}
       examples=k.get('workedExamples') or []
       if not str(k.get('mentalModel','')).strip(): fails.append(f'learner-quality explanation violation; scene {sid} needs a mentalModel')
       if not examples: fails.append(f'learner-quality explanation violation; scene {sid} needs at least one worked example')
       if not (k.get('boundaries') or k.get('pitfalls')): fails.append(f'learner-quality explanation violation; scene {sid} needs a boundary or misconception')
      # Principle animation: if present, require a learner debrief that connects motion to principle.
      for sc in course_data.get('scenes',[]):
       c=sc.get('content') or {}; sid=sc.get('id','?')
       if c.get('widgetType')=='process-animation':
        cfg=c.get('widgetConfig') or {}
        pc=cfg.get('principleCheck')
        if not isinstance(pc,dict) or not str(pc.get('prompt','')).strip(): fails.append(f'learner-quality animation violation; scene {sid} needs principleCheck.prompt')
        if not (pc or {}).get('expectedIdeas'): fails.append(f'learner-quality animation violation; scene {sid} needs principleCheck.expectedIdeas')
      # Gap-revealing practice: tagged diagnostics and at least two gap types per objective represented in practice.
      if qpol.get('requireDiagnosticGapTags'):
       gaps={}
       for sc in course_data.get('scenes',[]):
        c=sc.get('content') or {}
        for item in (c.get('items') or [])+(c.get('questions') or []):
         if not isinstance(item,dict): continue
         tags=item.get('gapTags') or ([] if not item.get('diagnosticTag') else [item.get('diagnosticTag')])
         if not tags: fails.append(f'learner-quality practice violation; item {item.get("id","?")} needs gapTags')
         oids=item.get('objectiveIds') or ([item.get('objectiveId')] if item.get('objectiveId') else sc.get('objectiveIds') or [])
         for oid in oids:
          gaps.setdefault(oid,set()).update(str(x) for x in tags if x)
       for o in course_data.get('objectives',[]):
        oid=o.get('id')
        if oid and len(gaps.get(oid,set()))<2: fails.append(f'learner-quality practice violation; objective {oid} needs at least two distinct gapTags')
    # Content-fit animation semantics: animation must be isomorphic to the taught mechanism.
    if True:
     meta=course_data.get('meta') or {}; apol=meta.get('animationContentPolicy') or {}
     if apol.get('mode')=='content-fit':
      for flag in ['requireSemantics','requireDomainPrimitiveWhenAvailable','requireStepWhy','requireMisleadingBoundary','requireKeyStep','animateOnlyWhenMechanismBenefits']:
       if apol.get(flag) is not True: fails.append(f'animation-content-fit policy violation; {flag} must be true')
      pack=meta.get('disciplinePack')
      allowed_knowledge={'mechanism-process','dynamic-quantity','structure-build','reasoning-evolution','simulation-experiment','static-relation'}
      domain_primitives={
       'mathematics':{'die','coin','sample-point','math-point','vector'},
       'statistics':{'die','coin','sample-point','math-point','vector'},
       'physics':{'projectile','projection-marker','vector','electron','ion'},
       'biology':{'molecule','energy-token','water-drop'},
       'chemistry':{'molecule','ion','electron','energy-token','vector'},
       'computer-science':{'stack-frame','array-cell','pointer'},
       'geography':{'water-drop','air-mass','plate','vector'},
       'ml-ai':{'math-point','vector','array-cell','pointer'},
      }
      pack_prefix={'computer-science':'computer-science','ml-ai':'ml-ai'}.get(pack,pack or '')+'-'
      for sc in course_data.get('scenes',[]):
       c=sc.get('content') or {}
       if c.get('widgetType')!='process-animation': continue
       sid=sc.get('id','?'); cfg=c.get('widgetConfig') or {}; sem=cfg.get('animationSemantics') or {}; actors=cfg.get('actors') or []; steps=cfg.get('steps') or []
       for field in ['profile','knowledgeType','teachingGoal','corePrinciple','entities','stateVariables','stepLogic','mustNotMislead','motionRationale','contentFitAudit']:
        if not sem.get(field): fails.append(f'animation-content-fit violation; scene {sid} needs animationSemantics.{field}')
       profile=str(sem.get('profile',''))
       if pack_prefix and not profile.startswith(pack_prefix): fails.append(f'animation-content-fit violation; scene {sid} profile {profile or "?"} does not match discipline pack {pack}')
       if sem.get('knowledgeType') not in allowed_knowledge: fails.append(f'animation-content-fit violation; scene {sid} has unsupported knowledgeType {sem.get("knowledgeType")}')
       if sem.get('knowledgeType')=='static-relation': fails.append(f'animation-content-fit violation; scene {sid} declares static-relation but uses process-animation; use a diagram/figure instead')
       ids={str(a.get('id')) for a in actors if isinstance(a,dict) and a.get('id')}
       if len(ids)!=len(actors): fails.append(f'animation-content-fit violation; scene {sid} every actor needs a stable id')
       for a in actors:
        if isinstance(a,dict) and a.get('type') not in {'track','line','secant-line','text','zone'} and not str(a.get('semanticRole','')).strip(): fails.append(f'animation-content-fit violation; scene {sid} actor {a.get("id","?")} needs semanticRole')
       entity_actor_ids=set()
       for e in sem.get('entities') or []:
        if not isinstance(e,dict) or not str(e.get('concept','')).strip(): fails.append(f'animation-content-fit violation; scene {sid} conceptual entity needs concept')
        for aid in (e.get('actorIds') or []):
         entity_actor_ids.add(str(aid))
         if str(aid) not in ids: fails.append(f'animation-content-fit violation; scene {sid} entity references unknown actor {aid}')
       meaningful={str(a.get('id')) for a in actors if isinstance(a,dict) and a.get('type') not in {'track','line','secant-line','text'} and a.get('id')}
       if meaningful and not meaningful.issubset(entity_actor_ids | {str(a.get('id')) for a in actors if a.get('type')=='zone'}): fails.append(f'animation-content-fit violation; scene {sid} has visible knowledge actors not bound to conceptual entities')
       relation_types={'passes-through','touches','contains','enters','attached-to','points-to'}
       amap={str(a.get('id')):a for a in actors if isinstance(a,dict) and a.get('id')}
       for rel in sem.get('semanticRelations') or []:
        if not isinstance(rel,dict) or rel.get('type') not in relation_types: fails.append(f'animation-content-fit violation; scene {sid} has unsupported semanticRelation') ; continue
        src=str(rel.get('source','')); tgts=[str(x) for x in (rel.get('targets') or [])]
        if src not in ids or not tgts or any(x not in ids for x in tgts): fails.append(f'animation-content-fit violation; scene {sid} semanticRelation references unknown actor') ; continue
        scoped=[str(x) for x in (rel.get('whenSteps') or [])]
        valid_actions={str(x.get('semanticAction','')) for x in steps if isinstance(x,dict) and x.get('semanticAction')}
        if scoped and (not all(scoped) or any(x not in valid_actions for x in scoped)): fails.append(f'animation-content-fit violation; scene {sid} semanticRelation has unknown whenSteps action')
        stype=(amap.get(src) or {}).get('type')
        if rel.get('type')=='passes-through' and stype not in {'line','secant-line','track','vector'}: fails.append(f'animation-content-fit violation; scene {sid} passes-through source {src} must be line-like')
        if rel.get('type')=='contains' and stype!='zone': fails.append(f'animation-content-fit violation; scene {sid} contains source {src} must be a zone')
        if rel.get('type')=='points-to' and stype not in {'pointer','vector'}: fails.append(f'animation-content-fit violation; scene {sid} points-to source {src} must be pointer/vector')
       if len(sem.get('stepLogic') or [])!=len(steps): fails.append(f'animation-content-fit violation; scene {sid} stepLogic length must equal animation step count')
       if apol.get('requireMisleadingBoundary') and len(sem.get('mustNotMislead') or [])<1: fails.append(f'animation-content-fit violation; scene {sid} needs at least one mustNotMislead boundary')
       audit=sem.get('contentFitAudit') or {}
       if audit.get('entitySpecificity') not in {'high','medium'}: fails.append(f'animation-content-fit violation; scene {sid} entitySpecificity must be high/medium')
       if audit.get('motionNaturalness') not in {'high','medium'}: fails.append(f'animation-content-fit violation; scene {sid} motionNaturalness must be high/medium')
       if audit.get('misleadingRisk') not in {'low','controlled'}: fails.append(f'animation-content-fit violation; scene {sid} misleadingRisk must be low/controlled')
       if not str(audit.get('visualStory','')).strip(): fails.append(f'animation-content-fit violation; scene {sid} needs contentFitAudit.visualStory')
       if apol.get('requireDomainPrimitiveWhenAvailable') and domain_primitives.get(pack):
        types={a.get('type') for a in actors if isinstance(a,dict)}
        if not (types & domain_primitives[pack]): fails.append(f'animation-content-fit violation; scene {sid} uses only generic actors for {pack}; use a discipline-native primitive')
       if apol.get('requireKeyStep') and not any((st or {}).get('emphasis')=='key' for st in steps): fails.append(f'animation-content-fit violation; scene {sid} needs at least one key emphasis step')
       for i,st in enumerate(steps,1):
        if apol.get('requireStepWhy') and (not str((st or {}).get('semanticAction','')).strip() or not str((st or {}).get('whyItMatters','')).strip()): fails.append(f'animation-content-fit violation; scene {sid} step {i} needs semanticAction and whyItMatters')
        ms=(st or {}).get('motionMs')
        if ms is not None:
         try:
          if float(ms)<300 or float(ms)>2600: fails.append(f'animation-content-fit violation; scene {sid} step {i} motionMs should be 300–2600 ms')
         except Exception: fails.append(f'animation-content-fit violation; scene {sid} step {i} motionMs must be numeric')
    # Animation and adjustable-experiment contracts.
    if True:
     course_meta=course_data.get('meta') or {}; experiment_policy=course_meta.get('experimentPolicy'); dedup_policy=course_meta.get('experimentDedupPolicy'); experiment_keys={}; experiment_prompts={}
     if dedup_policy not in {None,'stable-key'}: fails.append('experiment-dedup violation; experimentDedupPolicy must be stable-key when declared')
     for sc in course_data.get('scenes',[]):
      c=sc.get('content') or {}; wt=c.get('widgetType'); cfg=c.get('widgetConfig') or {}; sid=sc.get('id','?')
      entries=_experiment_entries(cfg)
      for entry in entries:
       key=entry.get('key'); prompt=_normalized_prompt(entry.get('prompt'))
       if dedup_policy=='stable-key' and entry.get('source')=='item' and (not key or not entry.get('role')): fails.append(f'experiment-dedup violation; scene {sid} experiment entries need experimentKey and experimentRole')
       if key:
        if key in experiment_keys: fails.append(f'experiment-dedup violation; duplicate experimentKey {key} in scenes {experiment_keys[key]} and {sid}')
        else: experiment_keys[key]=sid
       if prompt:
        if prompt in experiment_prompts: fails.append(f'experiment-dedup violation; duplicate experiment prompt in scenes {experiment_prompts[prompt]} and {sid}')
        else: experiment_prompts[prompt]=sid
      if wt=='diagram' and (cfg.get('animation') or {}).get('enabled'):
       steps=[int(x.get('step',1)) for x in (cfg.get('nodes') or [])+(cfg.get('edges') or []) if isinstance(x,dict)]
       if len(set(steps))<2: fails.append(f'animation violation; diagram scene {sid} enables animation but has fewer than two reveal steps')
       if 'diagram-play' not in text or 'prefers-reduced-motion' not in text: fails.append(f'animation violation; diagram scene {sid} lacks play/reduced-motion runtime')
      if wt=='simulation':
       if experiment_policy=='adjustable-when-applicable' and not (cfg.get('parameters') or []): fails.append(f'experiment violation; simulation scene {sid} has no adjustable parameters')
       if not (cfg.get('experiments') or []): warns.append(f'simulation scene {sid} has controls but no guided experiment prompts')
      if wt=='data-lab' and (cfg.get('experimentRequired') or experiment_policy=='adjustable-when-applicable'):
       if not (cfg.get('parameters') or []): fails.append(f'experiment violation; data-lab scene {sid} needs learner-adjustable parameters')
       if (cfg.get('model') or {}).get('kind') not in {'linear-regression'}: warns.append(f'data-lab scene {sid} adjustable model is not in the canonical local registry')
      if wt=='quantity-lab' and (cfg.get('experimentRequired') or experiment_policy=='adjustable-when-applicable'):
       if not any(isinstance(q,dict) and q.get('adjustable') for q in (cfg.get('quantities') or [])): fails.append(f'experiment violation; quantity-lab scene {sid} needs at least one adjustable quantity')
       if not (cfg.get('model') or {}).get('kind'): fails.append(f'experiment violation; quantity-lab scene {sid} needs a deterministic local model for recalculation')
      if wt=='chemistry' and (cfg.get('experimentRequired') or experiment_policy=='adjustable-when-applicable'):
       if not cfg.get('adjustableCoefficients'): fails.append(f'experiment violation; chemistry scene {sid} should let learners adjust stoichiometric coefficients')
      if wt=='motion-lab' and (cfg.get('experimentRequired') or experiment_policy=='adjustable-when-applicable'):
       if len(cfg.get('parameters') or [])<3: fails.append(f'experiment violation; motion-lab scene {sid} needs learner-adjustable motion parameters')
       if not cfg.get('trialLogging'): fails.append(f'experiment violation; motion-lab scene {sid} should let learners record/compare trials')
    if not modern_runtime:
     if 'lessonToc' not in text or 'data-toc-title' not in text:
      fails.append('reader missing current-page knowledge outline')
     if re.search(r'window\.scrollTo\(\{top\s*:\s*0',text):
      fails.append('scroll regression: scene rendering resets document to top')
     if "renderScene(mode='preserve')" not in text:
      warns.append('scroll-state contract not detected in renderer')
   except Exception as exc:
    msg=f'could not parse embedded course JSON: {exc}'
    if strict: fails.append(msg)
    else: warns.append(msg)
  elif not re.search(r'\"knowledge\"\s*:', text):
   fails.append('embedded course data not found or course data contains no authored knowledge blocks; core HTML must explain knowledge')
 print(f'Validating: {path}')
 for w in dict.fromkeys(warns): print('WARN:',w)
 for f in dict.fromkeys(fails): print('FAIL:',f)
 nf=len(set(fails)); nw=len(set(warns))
 if nf:
  print(f'RESULT: FAIL ({nf} failure(s), {nw} warning(s))'); return 1
 print(f'RESULT: PASS ({nw} warning(s))'); return 0

def main()->int:
 ap=argparse.ArgumentParser(); ap.add_argument('html',type=Path); ap.add_argument('--strict',action='store_true'); args=ap.parse_args()
 if not args.html.is_file(): print(f'FAIL: file not found: {args.html}'); return 2
 return validate(args.html,args.strict)
if __name__=='__main__': sys.exit(main())
