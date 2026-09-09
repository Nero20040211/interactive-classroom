import { execFileSync } from "node:child_process";
import { mkdirSync, readFileSync, readdirSync, rmSync, statSync, writeFileSync } from "node:fs";
import { resolve, join } from "node:path";

const here=process.cwd();
const buildDir=resolve(here,".build");
const distDir=resolve(here,"dist");
const srcDir=resolve(here,"src");

function walk(dir){
 return readdirSync(dir).flatMap(name=>{const p=join(dir,name);return statSync(p).isDirectory()?walk(p):[p];});
}

function runNpm(args){
 const command=process.platform==="win32"?"npm.cmd":"npm";
 execFileSync(command,args,{stdio:"inherit",shell:process.platform==="win32"});
}

const authoredCode=walk(srcDir).filter(p=>/\.(?:jsx?|css)$/i.test(p)).map(p=>readFileSync(p,"utf8")).join("\n");
const forbiddenRuntime=[
 /\b(?:fetch|XMLHttpRequest|WebSocket|EventSource)\b/,
 /\bnavigator\.sendBeacon\s*\(/,
 /\bimport\s*\(\s*["']https?:\/\//i,
 /\bserviceWorker\.register\s*\(\s*["']https?:\/\//i,
 /\bwindow\.open\s*\(\s*["']https?:\/\//i,
 /\.(?:src|href)\s*=\s*["']https?:\/\//i,
 /\.setAttribute\s*\(\s*["'](?:src|href|srcset|data|poster)["']\s*,\s*["']https?:\/\//i,
 /url\(\s*["']?https?:\/\//i,
 /@import\s+(?:url\()?\s*["']?https?:\/\//i,
];
if(forbiddenRuntime.some(rx=>rx.test(authoredCode))){
 throw new Error("Modern runtime authored source contains a learner-runtime network dependency.");
}

const coursePath=resolve(srcDir,"course.generated.json");
const manifestPath=resolve(srcDir,"widget-manifest.json");
const capabilitiesPath=resolve(srcDir,"runtime-capabilities.json");
const courseObj=JSON.parse(readFileSync(coursePath,"utf8"));
const manifest=JSON.parse(readFileSync(manifestPath,"utf8"));
const capabilities=JSON.parse(readFileSync(capabilitiesPath,"utf8"));
const meta=courseObj.meta||{};
if(meta.id==="replace-me"||!meta.id||!meta.title||!meta.disciplinePack||!Array.isArray(courseObj.scenes)||!courseObj.scenes.length){
 throw new Error("Replace scaffold course metadata and generate real scenes before building.");
}
if(meta.runtimeProfile!=="modern-react") throw new Error("Modern course must declare runtimeProfile=modern-react.");

const usedWidgets=[...new Set(courseObj.scenes.map(s=>s?.content?.widgetType).filter(Boolean))];
const builtins=new Set(capabilities.builtinWidgetTypes||[]);
const generated=new Set(manifest.widgetTypes||[]);
const missing=usedWidgets.filter(x=>!builtins.has(x)&&!generated.has(x));
if(missing.length) throw new Error(`widget-manifest.json missing generated components for: ${missing.join(", ")}`);
const registryCode=readFileSync(resolve(srcDir,"widget-registry.jsx"),"utf8");
const escapeRegex=s=>String(s).replace(/[.*+?^${}()|[\]\\]/g,"\\$&");
const customUsed=usedWidgets.filter(x=>!builtins.has(x));
const unregistered=customUsed.filter(type=>!(new RegExp(`["']${escapeRegex(type)}["']\\s*:`)).test(registryCode));
if(unregistered.length) throw new Error(`widget-registry.jsx does not register generated components for: ${unregistered.join(", ")}`);

rmSync(buildDir,{recursive:true,force:true});rmSync(distDir,{recursive:true,force:true});mkdirSync(buildDir,{recursive:true});mkdirSync(distDir,{recursive:true});
runNpm(["run","build:css"]);
runNpm(["run","build:js"]);

const template=readFileSync(resolve(here,"template.html"),"utf8");const css=readFileSync(resolve(buildDir,"styles.css"),"utf8");const js=readFileSync(resolve(buildDir,"app.js"),"utf8");const course=JSON.stringify(courseObj).replaceAll("<","\\u003c");
const widgetMarker=usedWidgets.join(",");
let output=template.replace("/*IC_CSS*/",css).replace("/*IC_COURSE_DATA*/",course).replace("/*IC_WIDGETS*/",widgetMarker).replace("/*IC_JS*/",js);
const builtForbidden=[
 /<script[^>]+src\s*=\s*["']https?:\/\//i,/<link[^>]+href\s*=\s*["']https?:\/\//i,/<(?:img|audio|video|source|iframe)[^>]+src\s*=\s*["']https?:\/\//i,
 /(?:url\(|sendBeacon|fetch\s*\(|XMLHttpRequest|WebSocket|EventSource)[^\n]{0,120}https?:\/\//i,
 /api\.(?:openai|anthropic)\.com|generativelanguage\.googleapis\.com/i,
];
if(builtForbidden.some(rx=>rx.test(output))) throw new Error("Built learner HTML contains a remote runtime resource or model endpoint.");
writeFileSync(resolve(distDir,"interactive-classroom.html"),output);
console.log("Built dist/interactive-classroom.html (offline, inlined React/Tailwind/Motion bundle)");
