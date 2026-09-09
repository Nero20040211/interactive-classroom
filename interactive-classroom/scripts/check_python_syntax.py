#!/usr/bin/env python3
"""Parse every Python file with ast without creating bytecode caches."""
from __future__ import annotations
import ast, sys
from pathlib import Path
sys.dont_write_bytecode=True
root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('.').resolve();fails=[];count=0
for path in sorted(root.rglob('*.py')):
 if any(part in {'node_modules','dist','.build'} for part in path.parts):continue
 count+=1
 try:ast.parse(path.read_text(encoding='utf-8'),filename=str(path))
 except Exception as e:fails.append(f'{path.relative_to(root)}: {e}')
if fails:
 for x in fails:print('FAIL:',x)
 print(f'PYTHON SYNTAX: FAIL ({len(fails)} failure(s))');raise SystemExit(1)
print(f'PYTHON SYNTAX: PASS ({count} file(s))')
