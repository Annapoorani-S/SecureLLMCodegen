import { useMemo, useState } from 'react'
import { AlertCircle, BarChart3, CheckCircle2, ChevronRight, Code2, FileCode2, FileText, FolderTree, LoaderCircle, Play, ScanSearch, ShieldAlert, ShieldCheck, Sparkles } from 'lucide-react'

const API = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
const sample = 'Build a FastAPI service for a team task manager with JWT authentication, roles, PostgreSQL, and a React dashboard.'

function api(path, body) {
  return fetch(`${API}${path}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
    .then(async (response) => {
      const data = await response.json()
      if (!response.ok) throw new Error(data.detail || 'The request could not be completed.')
      return data
    })
}

const labels = { authentication: 'Authentication', authorization: 'Authorization', input_validation: 'Input validation', sql_injection: 'SQL injection', api_security: 'API security', xss: 'XSS', file_upload: 'File upload', ssrf: 'SSRF', cryptography: 'Cryptography', secrets_management: 'Secrets management' }
const tabs = [
  ['overview', 'Overview', BarChart3],
  ['analysis', 'Security analysis', ScanSearch],
  ['findings', 'Findings', ShieldAlert],
  ['files', 'Generated files', FolderTree],
  ['report', 'Report', FileText],
]

function App() {
  const [requirement, setRequirement] = useState(sample)
  const [analysis, setAnalysis] = useState(null)
  const [run, setRun] = useState(null)
  const [activeTab, setActiveTab] = useState('overview')
  const [activeFile, setActiveFile] = useState(null)
  const [loading, setLoading] = useState('')
  const [error, setError] = useState('')

  const files = useMemo(() => Object.entries(run?.files || {}), [run])
  const security = run || analysis
  const analyze = async () => {
    if (requirement.trim().length < 3) return setError('Describe the software you want to build (at least 3 characters).')
    setError(''); setLoading('analyze')
    try { setAnalysis(await api('/api/analyze', { requirement })); setActiveTab('analysis') }
    catch (err) { setError(err.message) } finally { setLoading('') }
  }
  const generate = async () => {
    if (requirement.trim().length < 3) return setError('Describe the software you want to build (at least 3 characters).')
    setError(''); setLoading('generate')
    try {
      const result = await api('/api/generate', { requirement })
      setRun(result); setAnalysis(result); setActiveFile(Object.keys(result.files || {})[0] || null); setActiveTab('overview')
    } catch (err) { setError(err.message) } finally { setLoading('') }
  }

  return <main className="min-h-screen bg-ink text-slate-100">
    <header className="border-b border-white/10 bg-surface/70 backdrop-blur"><div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-4 lg:px-8">
      <div className="flex items-center gap-3"><div className="grid h-10 w-10 place-items-center rounded-xl bg-mint text-ink"><ShieldCheck size={23} /></div><div><p className="font-semibold">AISAF</p><p className="text-xs text-slate-400">AI Secure Architecture Framework</p></div></div>
      <div className="hidden items-center gap-2 text-sm text-slate-400 sm:flex"><span className="h-2 w-2 rounded-full bg-mint" />Security workspace</div>
    </div></header>

    <section className="border-b border-white/10 bg-[radial-gradient(circle_at_10%_0%,rgba(75,178,123,.16),transparent_36%)]"><div className="mx-auto max-w-7xl px-5 py-8 lg:px-8">
      <div className="mb-4 flex items-center justify-between"><div><p className="inline-flex items-center gap-2 text-xs font-medium text-mint"><Sparkles size={14} />OWASP + MITRE ATLAS aware</p><h1 className="mt-2 text-2xl font-semibold tracking-tight">Create a secure software run</h1></div><button onClick={() => setRequirement(sample)} className="text-xs text-mint hover:text-lime">Use example</button></div>
      <textarea value={requirement} onChange={(e) => setRequirement(e.target.value)} rows="3" className="w-full resize-none rounded-xl border bg-black/25 p-4 font-mono text-sm leading-6 text-slate-200 outline-none placeholder:text-slate-600 focus:border-mint/50 focus:ring-2 focus:ring-mint/10" placeholder="Describe your application, users, and technical requirements…" />
      <div className="mt-4 flex flex-wrap items-center justify-between gap-3"><p className="text-xs text-slate-500">AISAF maps risks, generates code, scans it, and records the evidence.</p><div className="flex gap-2"><button disabled={!!loading} onClick={analyze} className="inline-flex items-center gap-2 rounded-lg border border-white/15 px-4 py-2.5 text-sm font-medium hover:border-mint/50 hover:text-mint disabled:opacity-50">{loading === 'analyze' ? <LoaderCircle className="animate-spin" size={16} /> : <ScanSearch size={16} />}Analyze</button><button disabled={!!loading} onClick={generate} className="inline-flex items-center gap-2 rounded-lg bg-mint px-4 py-2.5 text-sm font-semibold text-ink hover:bg-lime disabled:opacity-50">{loading === 'generate' ? <LoaderCircle className="animate-spin" size={16} /> : <Play size={16} />}Generate & validate</button></div></div>
      {error && <div className="mt-4 flex gap-2 rounded-lg border border-red-400/25 bg-red-400/10 p-3 text-sm text-red-200"><AlertCircle size={18} />{error}</div>}
    </div></section>

    {security ? <div className="mx-auto grid max-w-7xl gap-6 px-5 py-7 lg:grid-cols-[220px_1fr] lg:px-8">
      <aside className="flex gap-2 overflow-x-auto lg:block lg:space-y-1">{tabs.map(([id, title, Icon]) => <button key={id} onClick={() => setActiveTab(id)} className={`inline-flex shrink-0 items-center gap-2 rounded-lg px-3 py-2.5 text-sm ${activeTab === id ? 'bg-mint/10 text-mint' : 'text-slate-400 hover:bg-white/5 hover:text-white'}`}><Icon size={16} />{title}</button>)}</aside>
      <section className="min-w-0">{activeTab === 'overview' && <Overview run={run} security={security} />}{activeTab === 'analysis' && <Analysis security={security} />}{activeTab === 'findings' && <Findings run={run} />}{activeTab === 'files' && <Files files={files} activeFile={activeFile} setActiveFile={setActiveFile} />}{activeTab === 'report' && <Report run={run} security={security} />}</section>
    </div> : <EmptyState />}
  </main>
}

function EmptyState() { return <div className="mx-auto max-w-7xl px-5 py-16 text-center lg:px-8"><ShieldCheck className="mx-auto text-mint" size={34} /><h2 className="mt-4 text-xl font-semibold">Start with a security analysis</h2><p className="mx-auto mt-2 max-w-md text-sm leading-6 text-slate-400">AISAF will identify relevant OWASP controls and MITRE ATLAS threats before it generates code.</p></div> }
function Card({ children, className = '' }) { return <div className={`panel p-5 ${className}`}>{children}</div> }
function Tag({ children, tone = 'mint' }) { return <span className={`tag ${tone === 'lime' ? 'border-lime/20 bg-lime/10 text-lime' : ''}`}>{children}</span> }

function Overview({ run, security }) {
  const summary = run?.summary || {}; const score = run?.final_security_score; const findings = summary.total ?? 0
  return <><div className="mb-6 flex flex-wrap items-end justify-between gap-3"><div><p className="text-sm text-slate-400">Security run overview</p><h2 className="mt-1 text-2xl font-semibold">{run ? 'Validation complete' : 'Analysis ready'}</h2></div>{run && <Tag tone={run.status === 'SECURE' ? 'mint' : 'lime'}>{run.status?.replace('_', ' ')}</Tag>}</div>
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4"><Metric label="Security score" value={score ?? '—'} detail={score != null ? 'out of 100' : 'Generate to score'} /><Metric label="Open findings" value={run ? findings : '—'} detail={run ? `${summary.HIGH || 0} high severity` : 'Awaiting validation'} /><Metric label="OWASP controls" value={security.owasp_domains?.length || 0} detail="Applied to generation" /><Metric label="MITRE threats" value={security.mitre_threats?.length || 0} detail="AI threat model" /></div>
    <div className="mt-5 grid gap-5 xl:grid-cols-2"><Card><h3 className="font-semibold">Pipeline status</h3><div className="mt-5 space-y-4">{['Requirement analysis', 'Security context', 'Code generation', 'Security validation', 'Report'].map((step, index) => <div key={step} className="flex items-center gap-3 text-sm"><CheckCircle2 size={18} className={run || index < 2 ? 'text-mint' : 'text-slate-600'} /><span className={run || index < 2 ? 'text-slate-200' : 'text-slate-500'}>{step}</span>{index < 2 && !run && <span className="ml-auto text-xs text-mint">Ready</span>}</div>)}</div></Card><Card><h3 className="font-semibold">Release decision</h3><p className="mt-3 text-sm leading-6 text-slate-400">{run ? (findings ? 'Review unresolved findings before releasing this project.' : 'No scanner findings were reported. Confirm scanner coverage before release.') : 'Run generation and validation to receive a release recommendation.'}</p><button className="mt-5 inline-flex items-center gap-1 text-sm font-medium text-mint" onClick={() => document.querySelector('[data-tab="report"]')?.click()}>View evidence <ChevronRight size={16} /></button></Card></div>
  </>
}
function Metric({ label, value, detail }) { return <Card><p className="text-xs text-slate-500">{label}</p><p className="mt-2 text-3xl font-semibold tracking-tight">{value}</p><p className="mt-1 text-xs text-slate-400">{detail}</p></Card> }
function Analysis({ security }) { return <><h2 className="text-2xl font-semibold">Security analysis</h2><p className="mt-2 text-sm text-slate-400">Controls detected from the requirement and added to the secure generation context.</p><div className="mt-6 grid gap-5 xl:grid-cols-2"><Card><h3 className="font-semibold">Detected technology</h3><dl className="mt-4 grid grid-cols-2 gap-x-4 gap-y-3 text-sm">{Object.entries(security.technology || {}).filter(([, value]) => value).map(([key, value]) => <div key={key}><dt className="capitalize text-slate-500">{key.replace('_', ' ')}</dt><dd className="mt-1 text-slate-200">{value}</dd></div>)}</dl></Card><Card><h3 className="font-semibold">OWASP controls</h3><div className="mt-4 flex flex-wrap gap-2">{security.owasp_domains?.map((item) => <Tag key={item}>{labels[item] || item}</Tag>)}</div></Card><Card className="xl:col-span-2"><h3 className="font-semibold">MITRE ATLAS threat model</h3><div className="mt-4 flex flex-wrap gap-2">{security.mitre_threats?.length ? security.mitre_threats.map((item) => <Tag key={item} tone="lime">{item}</Tag>) : <p className="text-sm text-slate-500">No AI-specific threats were detected for this requirement.</p>}</div></Card></div></> }
function Findings({ run }) { const issues = run?.final_vulnerabilities || []; return <><h2 className="text-2xl font-semibold">Findings</h2><p className="mt-2 text-sm text-slate-400">Scanner evidence from the final validation pass.</p><Card className="mt-6 overflow-hidden p-0">{!run ? <EmptyPanel message="Generate and validate a project to view findings." /> : !issues.length ? <EmptyPanel message="No findings were returned. Check scanner status before treating this as a release approval." /> : <div className="overflow-auto"><table className="w-full min-w-[650px] text-left text-sm"><thead className="border-b bg-white/5 text-xs text-slate-400"><tr><th className="p-4">Severity</th><th className="p-4">Tool</th><th className="p-4">Rule</th><th className="p-4">Location</th><th className="p-4">Message</th></tr></thead><tbody>{issues.map((issue, i) => <tr key={`${issue.rule}-${i}`} className="border-b border-white/5"><td className="p-4"><Severity value={issue.severity} /></td><td className="p-4">{issue.tool}</td><td className="p-4 font-mono text-xs">{issue.rule}</td><td className="p-4 font-mono text-xs">{issue.file}:{issue.line}</td><td className="p-4 text-slate-400">{issue.message}</td></tr>)}</tbody></table></div>}</Card></> }
function Severity({ value }) { const severity = String(value || 'INFO').toUpperCase(); const colors = { HIGH: 'text-red-300 border-red-400/20 bg-red-400/10', MEDIUM: 'text-amber-300 border-amber-400/20 bg-amber-400/10', LOW: 'text-sky-300 border-sky-400/20 bg-sky-400/10' }; return <span className={`tag ${colors[severity] || ''}`}>{severity}</span> }
function Files({ files, activeFile, setActiveFile }) { const content = files.find(([name]) => name === activeFile)?.[1] || ''; return <><h2 className="text-2xl font-semibold">Generated files</h2><p className="mt-2 text-sm text-slate-400">Review generated code before accepting the security run.</p><Card className="mt-6 overflow-hidden p-0"><div className="grid min-h-[440px] md:grid-cols-[220px_1fr]"><aside className="border-b bg-black/10 p-2 md:border-b-0 md:border-r">{files.map(([name]) => <button key={name} onClick={() => setActiveFile(name)} className={`flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left text-sm ${activeFile === name ? 'bg-mint/10 text-mint' : 'text-slate-400 hover:bg-white/5 hover:text-white'}`}><FileCode2 size={15} /><span className="truncate">{name}</span></button>)}</aside><pre className="max-h-[620px] overflow-auto p-5 text-xs leading-6 text-slate-300">{content || 'No generated files are available yet.'}</pre></div></Card></> }
function Report({ run, security }) { return <><h2 className="text-2xl font-semibold">Security report</h2><p className="mt-2 text-sm text-slate-400">A concise record of AISAF’s analysis and validation evidence.</p><Card className="mt-6"><div className="flex flex-wrap justify-between gap-4"><div><p className="text-xs text-slate-500">Release status</p><h3 className="mt-1 text-2xl font-semibold">{run?.status?.replace('_', ' ') || 'Analysis only'}</h3></div>{run && <div className="text-right"><p className="text-xs text-slate-500">Final score</p><p className="mt-1 text-2xl font-semibold text-mint">{run.final_security_score}/100</p></div>}</div><div className="mt-6 grid gap-5 border-t pt-5 sm:grid-cols-2"><div><p className="text-xs text-slate-500">Security controls</p><p className="mt-2 text-sm text-slate-300">{(security.owasp_domains || []).map(x => labels[x] || x).join(', ') || 'None detected'}</p></div><div><p className="text-xs text-slate-500">AI threat model</p><p className="mt-2 text-sm text-slate-300">{security.mitre_threats?.join(', ') || 'No AI-specific threats detected'}</p></div></div></Card></> }
function EmptyPanel({ message }) { return <div className="p-12 text-center text-sm text-slate-500">{message}</div> }
export default App
