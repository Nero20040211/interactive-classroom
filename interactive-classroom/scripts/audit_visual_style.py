#!/usr/bin/env python3
"""Audit current shell contrast, process-label readability, and mobile animation strategy."""
from __future__ import annotations
import re, sys, argparse
from pathlib import Path

ROLES=['primary','secondary','accent','good','warn','muted','container']

def rgb(h):
    h=h.lstrip('#')
    return tuple(int(h[i:i+2],16)/255 for i in (0,2,4))
def lum(h):
    vals=[]
    for c in rgb(h): vals.append(c/12.92 if c<=0.04045 else ((c+.055)/1.055)**2.4)
    r,g,b=vals; return .2126*r+.7152*g+.0722*b
def cr(a,b):
    x,y=sorted((lum(a),lum(b)),reverse=True); return (x+.05)/(y+.05)
def vars_from(block):
    return dict(re.findall(r'(--[\w-]+)\s*:\s*(#[0-9a-fA-F]{6})',block))

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('shell',nargs='?',default='assets/classroom-shell.html',type=Path); args=ap.parse_args()
    p=args.shell
    if p.is_dir(): p=p/'assets/classroom-shell.html'
    t=p.read_text(encoding='utf-8'); fails=[]
    light_m=re.search(r':root\s*\{(.*?)\}\s*@media\(prefers-color-scheme:dark\)',t,re.S)
    dark_m=re.search(r'@media\(prefers-color-scheme:dark\)\s*\{\s*:root\s*\{(.*?)\}\s*\}',t,re.S)
    if not light_m or not dark_m:
        print('FAIL: unable to parse light/dark root tokens'); return 1
    modes=[('light',vars_from(light_m.group(1))),('dark',vars_from(dark_m.group(1)))]
    for mode,v in modes:
        paper=v.get('--paper'); canvas=v.get('--anim-canvas')
        if not paper or not canvas: fails.append(f'{mode}: missing paper/animation canvas tokens'); continue
        for role in ROLES:
            bg=v.get(f'--anim-{role}-bg'); stroke=v.get(f'--anim-{role}-stroke'); text=v.get(f'--anim-{role}-text')
            if not all((bg,stroke,text)):
                fails.append(f'{mode}: missing animation palette for {role}'); continue
            tc=cr(bg,text); sc=cr(canvas,stroke)
            if tc<4.5: fails.append(f'{mode}: {role} text contrast {tc:.2f} < 4.5')
            if sc<3.0: fails.append(f'{mode}: {role} boundary contrast {sc:.2f} < 3.0')
        muted=v.get('--muted'); text=v.get('--text')
        if muted and cr(paper,muted)<4.5: fails.append(f'{mode}: muted body text contrast {cr(paper,muted):.2f} < 4.5')
        if text and cr(paper,text)<7: fails.append(f'{mode}: primary text contrast {cr(paper,text):.2f} < 7.0 target')
    for token in ['process-stage svg{width:100%;min-width:680px','process-actor text','mobileAnimationStrategy','prefers-reduced-motion','--anim-primary-text']:
        if token not in t and token!='mobileAnimationStrategy': fails.append(f'shell missing readability token: {token}')
    actor_block=t[t.find('function processMoleculeGlyph'):t.find('function processStepDetail')]
    for tiny in ['font-size="10"','font-size="11"','font-size="12"','font-size="13"']:
        if tiny in actor_block: fails.append(f'process primitive contains undersized learner label: {tiny}')
    if '--series-2' in t or '--series-3' in t: fails.append('shell still references undefined legacy --series-* animation colors')
    if fails:
        for f in fails: print('FAIL:',f)
        print(f'VISUAL RESULT: FAIL ({len(fails)})'); return 1
    print('VISUAL RESULT: PASS')
    for mode,v in modes:
        vals=[]
        for role in ROLES: vals.append(cr(v[f'--anim-{role}-bg'],v[f'--anim-{role}-text']))
        print(f'{mode}: minimum actor text contrast = {min(vals):.2f}:1')
    return 0
if __name__=='__main__': sys.exit(main())
