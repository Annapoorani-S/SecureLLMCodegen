import { useMemo, useState } from 'react'
import { AlertCircle, ArrowRight, Check, ChevronDown, Code2, Copy, FileCode2, FolderTree, LoaderCircle, LockKeyhole, ShieldCheck, Sparkles } from 'lucide-react'

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

function CopyButton({ value }) {
  const [copied, setCopied] = useState(false)
  const copy = async () => { await navigator.clipboard.writeText(value); setCopied(true); setTimeout(() => setCopied(false), 1500) }
  return <button onClick={copy} className="rounded-md p-1.5 text-slate-400 hover:bg-white/10 hover:text-white" title="Copy"><>{copied ? <Check size={15} /> : <Copy size={15} />}</></button>
}

function App() {
  const [requirement, setRequirement] = useState(sample)
  const [analysis, setAnalysis] = useState(null)
  const [result, setResult] = useState(null)
  const [activeFile, setActiveFile] = useState(null)
  const [loading, setLoading] = useState('')
  const [error, setError] = useState('')

  const files = useMemo(() => Object.entries(result?.files || {}), [result])
  const run = async (mode) => {
    if (requirement.trim().length < 3) return setError('Describe the software you want to build (at least 3 characters).')
    setError(''); setLoading(mode)
    try {
      const data = await api(mode === 'analyze' ? '/api/analyze' : '/api/generate', { requirement })
      setAnalysis(data)
      if (mode === 'generate') { setResult(data); setActiveFile(Object.keys(data.files)[0] || null) }
    } catch (err) { setError(err.message) } finally { setLoading('') }
  }
  const security = result || analysis

  return <main className="min-h-screen overflow-hidden bg-[radial-gradient(circle_at_12%_0%,rgba(75,178,123,.16),transparent_30%),radial-gradient(circle_at_95%_20%,rgba(198,244,107,.1),transparent_28%)]">
    <nav className="mx-auto flex max-w-7xl items-center justify-between px-6 py-6 lg:px-8">
      <div className="flex items-center gap-3"><div className="grid h-10 w-10 place-items-center rounded-xl bg-mint text-ink"><ShieldCheck size={23} strokeWidth={2.5} /></div><div><div className="font-semibold tracking-tight">AISAF</div><div className="text-xs text-slate-400">Secure Architecture Framework</div></div></div>
      <div className="hidden items-center gap-2 text-sm text-slate-400 sm:flex"><span className="h-2 w-2 rounded-full bg-mint shadow-[0_0_12px_#8ce7b3]" />Security context online</div>
    </nav>

    <section className="mx-auto max-w-7xl px-6 pb-16 pt-8 lg:px-8 lg:pt-14">
      <div className="mx-auto max-w-3xl text-center"><div className="mb-4 inline-flex items-center gap-2 rounded-full border border-mint/20 bg-mint/10 px-3 py-1.5 text-xs font-medium text-mint"><Sparkles size={14} />OWASP + MITRE ATLAS aware</div><h1 className="text-4xl font-semibold tracking-[-0.04em] text-white sm:text-6xl">Design software with <span className="text-mint">security built in.</span></h1><p className="mx-auto mt-5 max-w-2xl text-base leading-7 text-slate-400">Turn a product requirement into a secure, multi-file project. AISAF maps risks before generation so the architecture starts on solid ground.</p></div>

      <div className="mx-auto mt-12 max-w-5xl panel p-5 sm:p-7"><div className="mb-4 flex items-center justify-between"><label htmlFor="requirement" className="flex items-center gap-2 text-sm font-medium"><Code2 size={17} className="text-mint" />What are you building?</label><button onClick={() => setRequirement(sample)} className="text-xs text-mint hover:text-lime">Use example</button></div><textarea id="requirement" value={requirement} onChange={(e) => setRequirement(e.target.value)} rows="5" placeholder="Describe your application, users, and technical requirements..." className="w-full resize-none rounded-xl border bg-black/20 p-4 font-mono text-sm leading-6 text-slate-200 outline-none placeholder:text-slate-600 focus:border-mint/50 focus:ring-2 focus:ring-mint/10" />
        <div className="mt-5 flex flex-col gap-3 sm:flex-row sm:justify-between"><p className="flex items-center gap-2 text-xs text-slate-500"><LockKeyhole size={14} />Requirements are analyzed for applicable security controls.</p><div className="flex gap-3"><button disabled={!!loading} onClick={() => run('analyze')} className="rounded-lg border border-white/15 px-4 py-2.5 text-sm font-medium hover:border-mint/50 hover:text-mint disabled:opacity-50">{loading === 'analyze' ? <LoaderCircle className="animate-spin" size={17} /> : 'Analyze security'}</button><button disabled={!!loading} onClick={() => run('generate')} className="inline-flex items-center justify-center gap-2 rounded-lg bg-mint px-4 py-2.5 text-sm font-semibold text-ink hover:bg-lime disabled:opacity-50">{loading === 'generate' ? <><LoaderCircle className="animate-spin" size={17} />Generating</> : <>Generate project <ArrowRight size={16} /></>}</button></div></div>
        {error && <div className="mt-4 flex gap-2 rounded-lg border border-red-400/25 bg-red-400/10 p-3 text-sm text-red-200"><AlertCircle size={18} className="shrink-0" />{error}</div>}
      </div>

      {security && <section className="mx-auto mt-8 grid max-w-5xl gap-5 lg:grid-cols-2"><SecurityCard title="OWASP domains" subtitle="Secure coding controls applied" items={security.owasp_domains} accent="mint" /><SecurityCard title="MITRE ATLAS threats" subtitle="AI-specific threat mitigations detected" items={security.mitre_threats} accent="lime" /></section>}
      {result && <section className="mx-auto mt-5 max-w-5xl panel overflow-hidden"><div className="flex items-center justify-between border-b px-5 py-4"><div><h2 className="flex items-center gap-2 font-semibold"><FolderTree size={18} className="text-mint" />Generated project</h2><p className="mt-1 text-xs text-slate-500">{files.length} files generated and saved by the API.</p></div><span className="tag"><Check size={13} className="mr-1" />Complete</span></div><div className="grid min-h-[360px] md:grid-cols-[210px_1fr]"><aside className="border-b bg-black/10 p-2 md:border-b-0 md:border-r">{files.map(([name]) => <button key={name} onClick={() => setActiveFile(name)} className={`flex w-full items-center gap-2 rounded-lg px-3 py-2 text-left text-sm ${activeFile === name ? 'bg-mint/10 text-mint' : 'text-slate-400 hover:bg-white/5 hover:text-white'}`}><FileCode2 size={15} /> <span className="truncate">{name}</span></button>)}</aside><div className="min-w-0"><div className="flex items-center justify-between border-b px-4 py-2 text-xs text-slate-400"><span className="font-mono">{activeFile}</span><CopyButton value={result.files[activeFile] || ''} /></div><pre className="max-h-[440px] overflow-auto p-5 font-mono text-xs leading-6 text-slate-300">{result.files[activeFile]}</pre></div></div></section>}
    </section>
  </main>
}

function SecurityCard({ title, subtitle, items, accent }) {
  const color = accent === 'lime' ? 'text-lime border-lime/20 bg-lime/10' : 'text-mint border-mint/20 bg-mint/10'
  return <div className="panel p-5"><div className="flex items-start justify-between"><div><h2 className="font-semibold">{title}</h2><p className="mt-1 text-xs text-slate-500">{subtitle}</p></div><ShieldCheck size={19} className={accent === 'lime' ? 'text-lime' : 'text-mint'} /></div><div className="mt-5 flex flex-wrap gap-2">{items.length ? items.map((item) => <span key={item} className={`tag ${color}`}>{item}</span>) : <span className="text-sm text-slate-500">No specific AI threats detected.</span>}</div></div>
}

export default App
