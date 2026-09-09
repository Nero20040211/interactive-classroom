#!/usr/bin/env python3
"""Static checks for the optional React/Tailwind/Motion authoring runtime."""
from __future__ import annotations
import json, re, sys
from pathlib import Path

EXPECTED={"react":"19.2.8","react-dom":"19.2.8","motion":"13.1.1","tailwindcss":"4.3.3","@tailwindcss/cli":"4.3.3","esbuild":"0.28.2"}
REQUIRED=[
 "references/frontend-runtime.md","assets/modern-runtime/package.json","assets/modern-runtime/package-lock.json","assets/modern-runtime/build.mjs",
 "assets/modern-runtime/template.html","assets/modern-runtime/src/main.jsx","assets/modern-runtime/src/App.jsx","assets/modern-runtime/src/builtin-widgets.jsx",
 "assets/modern-runtime/src/styles.css","assets/modern-runtime/src/course.generated.json","assets/modern-runtime/src/runtime-capabilities.json","assets/modern-runtime/src/animation-contract.js","assets/modern-runtime/src/model-contract.js","assets/modern-runtime/src/animation-widgets.jsx",
 "assets/modern-runtime/src/widget-registry.jsx","assets/modern-runtime/src/widget-manifest.json","scripts/test_modern_runtime.py",
]

def main(root:Path)->int:
 root=root.resolve(); fails=[]
 for rel in REQUIRED:
  if not (root/rel).is_file(): fails.append(f"missing {rel}")
 pkgp=root/"assets/modern-runtime/package.json"; lockp=root/"assets/modern-runtime/package-lock.json"
 if pkgp.is_file():
  try:
   pkg=json.loads(pkgp.read_text(encoding="utf-8")); merged={**(pkg.get("dependencies") or {}),**(pkg.get("devDependencies") or {})}
   if pkg.get("private") is not True:fails.append("modern runtime package must be private")
   if "version" in pkg:fails.append("modern runtime package must not declare a Skill/package release version")
   for name,pin in EXPECTED.items():
    if merged.get(name)!=pin:fails.append(f"{name} dependency pin mismatch")
   if any("latest" in str(v).lower() for v in merged.values()):fails.append("modern runtime dependencies must not use latest")
  except Exception as e:fails.append(f"invalid modern runtime package.json: {e}")
 if lockp.is_file():
  try:
   lock=json.loads(lockp.read_text(encoding="utf-8")); rootpkg=(lock.get("packages") or {}).get("") or {}; merged={**(rootpkg.get("dependencies") or {}),**(rootpkg.get("devDependencies") or {})}
   if lock.get("lockfileVersion")!=3:fails.append("modern runtime package-lock must use lockfileVersion 3")
   for name,pin in EXPECTED.items():
    if merged.get(name)!=pin:fails.append(f"package-lock direct pin mismatch: {name}")
   if pkgp.is_file():
    package=json.loads(pkgp.read_text(encoding="utf-8"))
    for kind in ("dependencies","devDependencies"):
     if (rootpkg.get(kind) or {})!=(package.get(kind) or {}):
      fails.append(f"package-lock {kind} must match package.json exactly")
  except Exception as e:fails.append(f"invalid modern runtime package-lock.json: {e}")
 files=[root/r for r in REQUIRED if (root/r).is_file() and not r.endswith("package-lock.json")]
 blob="\n".join(p.read_text(encoding="utf-8",errors="replace") for p in files)
 for tok in ["modern-react","React.StrictMode","createRoot","MotionConfig reducedMotion=\"user\"","LazyMotion","motion/react-m","@import \"tailwindcss\"","format=iife","IC_COURSE_DATA","interactive-classroom-schema","interactive-classroom-runtime","data-runtime-profile","widget-manifest.json","runtime-capabilities.json","builtinWidgetTypes","data-modern-toc","sanitizeMathML","QuizScene","ExplainBackScene","MasterySummary","PedagogicalFigure","WorkedExample","figureRef","motion-components","data-equation-steps","nextStepPrediction","animation-contract.js","model-contract.js","MotionLabWidget","SimulationWidget","requestAnimationFrame","收藏本页","参考资料","学习反馈","interactive-classroom-session-feedback","automaticSkillChange:false","离线学习"]:
  if tok not in blob:fails.append(f"modern runtime scaffold missing token: {tok}")
 runtime_files=[root/r for r in REQUIRED if r.startswith("assets/modern-runtime/") and not r.endswith(("build.mjs","package-lock.json","package.json"))]
 runtime="\n".join(p.read_text(encoding="utf-8",errors="replace") for p in runtime_files if p.is_file())
 for pat,label in [
  (r"https?://","remote URL"),(r"\bfetch\s*\(","fetch"),(r"\bXMLHttpRequest\b","XMLHttpRequest"),(r"\bWebSocket\b","WebSocket"),(r"\bEventSource\b","EventSource"),(r"\bnavigator\.sendBeacon\s*\(","sendBeacon"),
  (r"\bimport\s*\(\s*[\"']https?://","remote dynamic import"),(r"url\(\s*[\"']?https?://","remote CSS url"),
 ]:
  if re.search(pat,runtime,re.I):fails.append(f"modern runtime source contains {label}")
 app=(root/"assets/modern-runtime/src/App.jsx").read_text(encoding="utf-8",errors="replace") if (root/"assets/modern-runtime/src/App.jsx").is_file() else ""
 if re.search(r"(?:bg|text|border)-\$\{",app):fails.append("Tailwind class names must not be dynamically concatenated")
 for tok in ["ic-app","ic-topbar","ic-workbench","ic-scene-rail","ic-reading-column","ic-outline-rail","ic-widget-frame","ic-footer"]:
  if tok not in app:fails.append(f"Modern App missing stable visual class: {tok}")
 build=(root/"assets/modern-runtime/build.mjs").read_text(encoding="utf-8",errors="replace") if (root/"assets/modern-runtime/build.mjs").is_file() else ""
 for tok in ["replace(\"/*IC_CSS*/\"","replace(\"/*IC_COURSE_DATA*/\"","replace(\"/*IC_WIDGETS*/\"","replace(\"/*IC_JS*/\"","interactive-classroom.html","widget-manifest.json","widget-registry.jsx","runtime-capabilities.json","usedWidgets","widgetMarker","customUsed","unregistered"]:
  if tok not in build:fails.append(f"modern build/output contract missing {tok}")
 if "function runNpm(args)" not in build or "process.platform===\"win32\"?\"npm.cmd\":\"npm\"" not in build or "shell:process.platform===\"win32\"" not in build:
  fails.append("modern build must use the cross-platform runNpm wrapper")
 if "runNpm([\"run\",\"build:css\"]);" not in build or "runNpm([\"run\",\"build:js\"]);" not in build:
  fails.append("modern build must invoke CSS and JS builds through runNpm")
 main=(root/"assets/modern-runtime/src/main.jsx").read_text(encoding="utf-8",errors="replace") if (root/"assets/modern-runtime/src/main.jsx").is_file() else ""
 if re.search(r"import\s+[\"']\./styles\.css[\"']\s*;?",main):
  fails.append("modern entrypoint must not import styles.css; build injects CSS once")
 template=(root/"assets/modern-runtime/template.html").read_text(encoding="utf-8",errors="replace") if (root/"assets/modern-runtime/template.html").is_file() else ""
 if template.count("/*IC_CSS*/")!=1:
  fails.append("modern template must expose exactly one CSS injection marker")
 if fails:
  for x in fails:print("FAIL:",x)
  print(f"RESULT: FAIL ({len(fails)} failure(s))");return 1
 print("RESULT: PASS");return 0
if __name__=="__main__":
 raise SystemExit(main(Path(sys.argv[1]) if len(sys.argv)>1 else Path(".")))
