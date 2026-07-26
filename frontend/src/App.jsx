import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import {
  AlertCircle, AlertTriangle, ArrowRight, Check, ChevronDown, ChevronRight,
  Code2, Copy, File, FileCode2, FileJson, FileText, FileType, Folder,
  FolderOpen, FolderTree, Info, LoaderCircle, LockKeyhole, RefreshCw,
  Shield, ShieldAlert, ShieldCheck, ShieldX, Sparkles, Terminal, X,
  BarChart2, Layers, Bug,
} from 'lucide-react'
import html2pdf from 'html2pdf.js'

/* ─────────────────────────────────────────────────────────────
   API helpers
───────────────────────────────────────────────────────────── */
const API = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

async function apiFetch(path, options = {}) {
  const res = await fetch(`${API}${path}`, options)
  const data = await res.json()
  if (!res.ok) throw new Error(data.detail || 'Request failed.')
  return data
}

function apiPost(path, body) {
  return apiFetch(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
}

/* ─────────────────────────────────────────────────────────────
   Syntax highlighting  (zero-dependency, regex-based)
───────────────────────────────────────────────────────────── */
const LANGUAGE_MAP = {
  py: 'python', js: 'javascript', jsx: 'javascript', ts: 'typescript',
  tsx: 'typescript', java: 'java', go: 'go', rb: 'ruby', rs: 'rust',
  cpp: 'cpp', c: 'c', cs: 'csharp', php: 'php', swift: 'swift',
  kt: 'kotlin', html: 'html', xml: 'xml', css: 'css', scss: 'css',
  json: 'json', yaml: 'yaml', yml: 'yaml', md: 'markdown',
  sh: 'shell', bash: 'shell', dockerfile: 'dockerfile', sql: 'sql',
  toml: 'toml', env: 'env',
}

const RULES = {
  python: [
    { re: /(#.*)$/gm, cls: 'tok-comment' },
    { re: /("""[\s\S]*?"""|'''[\s\S]*?'''|"(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')/g, cls: 'tok-string' },
    { re: /\b(def|class|import|from|as|return|if|elif|else|for|while|try|except|finally|with|yield|lambda|pass|break|continue|raise|and|or|not|in|is|None|True|False|async|await|global|nonlocal|del)\b/g, cls: 'tok-keyword' },
    { re: /\b([A-Z][a-zA-Z0-9_]*)\b/g, cls: 'tok-class' },
    { re: /\b(\d+\.?\d*)\b/g, cls: 'tok-number' },
    { re: /@\w+/g, cls: 'tok-decorator' },
    { re: /\b(\w+)(?=\s*\()/g, cls: 'tok-function' },
  ],
  javascript: [
    { re: /(\/\/.*$|\/\*[\s\S]*?\*\/)/gm, cls: 'tok-comment' },
    { re: /(`(?:[^`\\]|\\.)*`|"(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')/g, cls: 'tok-string' },
    { re: /\b(const|let|var|function|class|return|import|export|from|as|default|if|else|for|while|do|switch|case|break|continue|new|this|super|extends|async|await|try|catch|finally|throw|typeof|instanceof|in|of|void|delete|null|undefined|true|false)\b/g, cls: 'tok-keyword' },
    { re: /\b([A-Z][a-zA-Z0-9_]*)\b/g, cls: 'tok-class' },
    { re: /\b(\d+\.?\d*)\b/g, cls: 'tok-number' },
    { re: /\b(\w+)(?=\s*[=(])/g, cls: 'tok-function' },
  ],
  java: [
    { re: /(\/\/.*$|\/\*[\s\S]*?\*\/)/gm, cls: 'tok-comment' },
    { re: /("(?:[^"\\]|\\.)*")/g, cls: 'tok-string' },
    { re: /\b(public|private|protected|class|interface|extends|implements|import|package|return|new|this|super|static|final|void|int|long|double|float|boolean|String|char|byte|short|if|else|for|while|do|switch|case|break|continue|try|catch|finally|throw|throws|null|true|false|abstract|synchronized|volatile|enum)\b/g, cls: 'tok-keyword' },
    { re: /\b([A-Z][a-zA-Z0-9_]*)\b/g, cls: 'tok-class' },
    { re: /\b(\d+\.?\d*)\b/g, cls: 'tok-number' },
    { re: /(@\w+)/g, cls: 'tok-decorator' },
  ],
  json: [
    { re: /("(?:[^"\\]|\\.)*")\s*:/g, cls: 'tok-attr' },
    { re: /:\s*("(?:[^"\\]|\\.)*")/g, cls: 'tok-string' },
    { re: /\b(true|false|null)\b/g, cls: 'tok-keyword' },
    { re: /\b(\d+\.?\d*)\b/g, cls: 'tok-number' },
  ],
  html: [
    { re: /(<!--[\s\S]*?-->)/g, cls: 'tok-comment' },
    { re: /(<\/?\w[\w.-]*)/g, cls: 'tok-tag' },
    { re: /(\s[\w-]+)(?=\s*=)/g, cls: 'tok-attr' },
    { re: /("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')/g, cls: 'tok-string' },
  ],
  css: [
    { re: /(\/\*[\s\S]*?\*\/)/g, cls: 'tok-comment' },
    { re: /([.#][\w-]+|:\w[\w-]*)/g, cls: 'tok-class' },
    { re: /([\w-]+)(?=\s*:)/g, cls: 'tok-attr' },
    { re: /("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'|#[0-9a-fA-F]{3,8}|\d+\.?\d*(?:px|em|rem|%|vh|vw|s|ms)?)/g, cls: 'tok-string' },
  ],
  yaml: [
    { re: /(#.*)$/gm, cls: 'tok-comment' },
    { re: /^([\w-]+):/gm, cls: 'tok-attr' },
    { re: /("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')/g, cls: 'tok-string' },
    { re: /\b(true|false|null|yes|no)\b/g, cls: 'tok-keyword' },
    { re: /\b(\d+\.?\d*)\b/g, cls: 'tok-number' },
  ],
  shell: [
    { re: /(#.*)$/gm, cls: 'tok-comment' },
    { re: /("(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*')/g, cls: 'tok-string' },
    { re: /\b(if|then|else|fi|for|do|done|while|case|esac|echo|export|source|cd|ls|grep|awk|sed|rm|cp|mv|mkdir)\b/g, cls: 'tok-keyword' },
    { re: /\$[\w{]+/g, cls: 'tok-decorator' },
  ],
  sql: [
    { re: /(--.*$|\/\*[\s\S]*?\*\/)/gm, cls: 'tok-comment' },
    { re: /('(?:[^'\\]|\\.)*')/g, cls: 'tok-string' },
    { re: /\b(SELECT|FROM|WHERE|JOIN|LEFT|RIGHT|INNER|OUTER|ON|INSERT|INTO|VALUES|UPDATE|SET|DELETE|CREATE|TABLE|DATABASE|INDEX|DROP|ALTER|ADD|COLUMN|PRIMARY|KEY|FOREIGN|REFERENCES|UNIQUE|NOT|NULL|AND|OR|IN|LIKE|ORDER|BY|GROUP|HAVING|LIMIT|OFFSET|AS|DISTINCT|COUNT|SUM|AVG|MAX|MIN)\b/gi, cls: 'tok-keyword' },
    { re: /\b(\d+\.?\d*)\b/g, cls: 'tok-number' },
  ],
  markdown: [
    { re: /^(#{1,6}\s.*)$/gm, cls: 'tok-class' },
    { re: /(`[^`]+`)/g, cls: 'tok-string' },
    { re: /(\*\*[^*]+\*\*|__[^_]+__)/g, cls: 'tok-keyword' },
    { re: /(\[.*?\]\(.*?\))/g, cls: 'tok-function' },
  ],
}

// Fallback: no highlighting for unknown languages
function highlight(code, ext) {
  const lang = LANGUAGE_MAP[ext?.toLowerCase()] || null
  const rules = RULES[lang] || []
  if (!rules.length) return escapeHtml(code)

  // We use Unicode Private Use Area (PUA) characters as placeholders
  // so subsequent regexes (like numbers \b\d+\b) don't accidentally match the placeholder index.
  const placeholders = []
  let src = code

  for (const { re, cls } of rules) {
    src = src.replace(re, (match) => {
      const idx = placeholders.length
      placeholders.push(`<span class="${cls}">${escapeHtml(match)}</span>`)
      return String.fromCharCode(0xE000 + idx)
    })
  }

  // Escape remaining characters, then restore placeholders
  src = escapeHtml(src)
  src = src.replace(/[\uE000-\uF8FF]/g, (match) => {
    const idx = match.charCodeAt(0) - 0xE000
    return placeholders[idx] || match
  })
  return src
}

function escapeHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

/* ─────────────────────────────────────────────────────────────
   File icon helpers
───────────────────────────────────────────────────────────── */
function fileExt(name = '') { return name.split('.').pop()?.toLowerCase() || '' }

function FileIcon({ name, size = 14 }) {
  const ext = fileExt(name)
  const iconClass = `flex-shrink-0`
  const map = {
    py: <FileCode2 size={size} className={`${iconClass} text-yellow-400`} />,
    js: <FileCode2 size={size} className={`${iconClass} text-yellow-300`} />,
    jsx: <FileCode2 size={size} className={`${iconClass} text-cyan-400`} />,
    ts: <FileCode2 size={size} className={`${iconClass} text-blue-400`} />,
    tsx: <FileCode2 size={size} className={`${iconClass} text-blue-300`} />,
    json: <FileJson size={size} className={`${iconClass} text-yellow-200`} />,
    html: <FileCode2 size={size} className={`${iconClass} text-orange-400`} />,
    css: <FileType size={size} className={`${iconClass} text-blue-300`} />,
    scss: <FileType size={size} className={`${iconClass} text-pink-400`} />,
    md: <FileText size={size} className={`${iconClass} text-slate-300`} />,
    txt: <FileText size={size} className={`${iconClass} text-slate-400`} />,
    sh: <Terminal size={size} className={`${iconClass} text-green-400`} />,
    bash: <Terminal size={size} className={`${iconClass} text-green-400`} />,
    java: <FileCode2 size={size} className={`${iconClass} text-orange-300`} />,
    go: <FileCode2 size={size} className={`${iconClass} text-cyan-300`} />,
    rs: <FileCode2 size={size} className={`${iconClass} text-orange-500`} />,
    sql: <FileCode2 size={size} className={`${iconClass} text-purple-400`} />,
    yaml: <FileCode2 size={size} className={`${iconClass} text-red-300`} />,
    yml: <FileCode2 size={size} className={`${iconClass} text-red-300`} />,
    toml: <FileCode2 size={size} className={`${iconClass} text-orange-200`} />,
    dockerfile: <FileCode2 size={size} className={`${iconClass} text-blue-400`} />,
    env: <FileText size={size} className={`${iconClass} text-yellow-300`} />,
  }
  return map[ext] || <File size={size} className={`${iconClass} text-slate-400`} />
}

/* ─────────────────────────────────────────────────────────────
   Build tree from flat files dict  {path: content}
   Also accepts the nested tree from /api/output/tree
───────────────────────────────────────────────────────────── */
function buildTreeFromFlat(filesDict) {
  const root = { name: 'output', path: '', type: 'directory', children: [] }
  const dirMap = { '': root }

  const sorted = Object.keys(filesDict).sort()

  for (const filePath of sorted) {
    const parts = filePath.split('/')
    let parent = root

    for (let i = 0; i < parts.length - 1; i++) {
      const dirPath = parts.slice(0, i + 1).join('/')
      if (!dirMap[dirPath]) {
        const node = { name: parts[i], path: dirPath, type: 'directory', children: [] }
        dirMap[dirPath] = node
        parent.children.push(node)
      }
      parent = dirMap[dirPath]
    }

    parent.children.push({
      name: parts[parts.length - 1],
      path: filePath,
      type: 'file',
    })
  }

  // Sort: dirs first, then files, alphabetical within each
  function sortChildren(node) {
    if (node.children) {
      node.children.sort((a, b) => {
        if (a.type !== b.type) return a.type === 'directory' ? -1 : 1
        return a.name.localeCompare(b.name)
      })
      node.children.forEach(sortChildren)
    }
  }
  sortChildren(root)
  return root
}

/* ─────────────────────────────────────────────────────────────
   Copy button
───────────────────────────────────────────────────────────── */
function CopyButton({ value, size = 13 }) {
  const [copied, setCopied] = useState(false)
  const copy = async () => {
    await navigator.clipboard.writeText(value)
    setCopied(true)
    setTimeout(() => setCopied(false), 1500)
  }
  return (
    <button
      onClick={copy}
      title="Copy"
      className="flex items-center gap-1 rounded-md px-2 py-1 text-xs text-slate-400 hover:bg-white/10 hover:text-white transition-colors"
    >
      {copied ? <><Check size={size} /> Copied</> : <><Copy size={size} /> Copy</>}
    </button>
  )
}

/* ─────────────────────────────────────────────────────────────
   FileTree node (recursive)
───────────────────────────────────────────────────────────── */
function TreeNode({ node, depth = 0, activeFile, onFileClick }) {
  const [open, setOpen] = useState(true)
  const isDir = node.type === 'directory'
  const isActive = !isDir && node.path === activeFile
  const indent = depth * 12

  if (isDir && node.name === 'output' && depth === 0) {
    // Root: just render children
    return (
      <div>
        {(node.children || []).map(child => (
          <TreeNode
            key={child.path}
            node={child}
            depth={depth}
            activeFile={activeFile}
            onFileClick={onFileClick}
          />
        ))}
      </div>
    )
  }

  if (isDir) {
    return (
      <div>
        <button
          className={`tree-node folder w-full`}
          style={{ paddingLeft: `${8 + indent}px` }}
          onClick={() => setOpen(o => !o)}
        >
          <span className="flex-shrink-0 text-slate-500">
            {open ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
          </span>
          {open
            ? <FolderOpen size={14} className="flex-shrink-0 text-yellow-400/80" />
            : <Folder size={14} className="flex-shrink-0 text-yellow-400/80" />}
          <span className="truncate">{node.name}</span>
        </button>
        {open && (
          <div className="animate-fade-in">
            {(node.children || []).map(child => (
              <TreeNode
                key={child.path}
                node={child}
                depth={depth + 1}
                activeFile={activeFile}
                onFileClick={onFileClick}
              />
            ))}
          </div>
        )}
      </div>
    )
  }

  return (
    <button
      className={`tree-node ${isActive ? 'active' : ''}`}
      style={{ paddingLeft: `${20 + indent}px` }}
      onClick={() => onFileClick(node.path)}
    >
      <FileIcon name={node.name} size={13} />
      <span className="truncate">{node.name}</span>
    </button>
  )
}

/* ─────────────────────────────────────────────────────────────
   Code Viewer with line numbers + syntax highlighting
───────────────────────────────────────────────────────────── */
function CodeViewer({ content, filePath }) {
  const ext = fileExt(filePath)
  const lines = useMemo(() => (content || '').split('\n'), [content])

  const highlightedLines = useMemo(() => {
    return lines.map(line => highlight(line, ext))
  }, [lines, ext])

  if (!content && content !== '') {
    return (
      <div className="vscode-empty">
        <LoaderCircle size={32} className="animate-spin text-mint/40" />
        <span className="text-sm">Loading file…</span>
      </div>
    )
  }

  return (
    <div className="vscode-code">
      {highlightedLines.map((html, i) => (
        <div key={i} className="code-line">
          <span className="code-gutter">{i + 1}</span>
          <span
            className="code-content"
            dangerouslySetInnerHTML={{ __html: html || ' ' }}
          />
        </div>
      ))}
    </div>
  )
}

/* ─────────────────────────────────────────────────────────────
   Breadcrumb
───────────────────────────────────────────────────────────── */
function Breadcrumb({ path }) {
  if (!path) return <div className="vscode-breadcrumb"><span className="text-slate-600">No file selected</span></div>
  const parts = path.split('/')
  return (
    <div className="vscode-breadcrumb">
      <span className="text-slate-600">output</span>
      {parts.map((part, i) => (
        <span key={i} className="flex items-center gap-1">
          <ChevronRight size={10} className="text-slate-700" />
          <span className={i === parts.length - 1 ? 'text-slate-300' : 'text-slate-500'}>
            {part}
          </span>
        </span>
      ))}
    </div>
  )
}

/* ─────────────────────────────────────────────────────────────
   Security score ring
───────────────────────────────────────────────────────────── */
function ScoreRing({ score }) {
  const r = 36
  const circ = 2 * Math.PI * r
  const dash = ((score ?? 0) / 100) * circ
  const color = score >= 90 ? '#8ce7b3' : score >= 70 ? '#fbbf24' : '#f87171'

  return (
    <div className="relative flex items-center justify-center">
      <svg width={92} height={92} className="-rotate-90">
        <circle cx={46} cy={46} r={r} fill="none" stroke="#1a2e25" strokeWidth={7} />
        <circle
          cx={46} cy={46} r={r} fill="none"
          stroke={color} strokeWidth={7}
          strokeDasharray={`${dash} ${circ}`}
          strokeLinecap="round"
          style={{ transition: 'stroke-dasharray 0.6s ease' }}
        />
      </svg>
      <div className="absolute text-center">
        <div className="text-xl font-bold" style={{ color }}>{score ?? '—'}</div>
        <div className="text-[9px] text-slate-500 uppercase tracking-wide">/ 100</div>
      </div>
    </div>
  )
}

/* ─────────────────────────────────────────────────────────────
   Security Dashboard
───────────────────────────────────────────────────────────── */
function SecurityDashboard({ report }) {
  if (!report) return null

  const { owasp_domains, mitre_atlas, final_security_score, initial_security_score,
    security_improvement, status, final_vulnerabilities = [], technology_stack = {} } = report

  const sevMap = { HIGH: 'sev-high', MEDIUM: 'sev-medium', LOW: 'sev-low', INFO: 'sev-info' }

  return (
    <div className="mt-6 space-y-4 animate-fade-in">
      {/* Score + Status row */}
      <div className="grid gap-4 sm:grid-cols-3">
        <div className="panel p-5 flex items-center gap-5">
          <ScoreRing score={final_security_score} />
          <div>
            <div className="text-xs text-slate-500 uppercase tracking-wide mb-1">Security Score</div>
            <div className={`text-sm font-semibold ${status === 'SECURE' ? 'text-mint' : 'text-yellow-400'}`}>{status}</div>
            <div className="text-xs text-slate-500 mt-1">
              {initial_security_score} → {final_security_score}
              <span className="ml-1 text-mint">(+{security_improvement})</span>
            </div>
          </div>
        </div>

        <div className="panel p-5">
          <div className="flex items-center justify-between mb-3">
            <div className="text-xs font-semibold uppercase tracking-wide text-slate-400">OWASP Domains</div>
            <ShieldCheck size={15} className="text-mint" />
          </div>
          <div className="flex flex-wrap gap-1.5">
            {owasp_domains?.length
              ? owasp_domains.map(d => <span key={d} className="tag text-[10px] py-0.5">{d}</span>)
              : <span className="text-xs text-slate-600">None detected</span>}
          </div>
        </div>

        <div className="panel p-5">
          <div className="flex items-center justify-between mb-3">
            <div className="text-xs font-semibold uppercase tracking-wide text-slate-400">MITRE ATLAS</div>
            <ShieldAlert size={15} className="text-lime" />
          </div>
          <div className="flex flex-wrap gap-1.5">
            {mitre_atlas?.length
              ? mitre_atlas.map(t => <span key={t} className="inline-flex items-center rounded-full border border-lime/20 bg-lime/10 px-2.5 py-1 text-[10px] font-medium text-lime">{t}</span>)
              : <span className="text-xs text-slate-600">None detected</span>}
          </div>
        </div>
      </div>

      {/* Technology stack */}
      {Object.keys(technology_stack).length > 0 && (
        <div className="panel p-5">
          <div className="flex items-center gap-2 mb-3">
            <Layers size={14} className="text-mint" />
            <span className="text-xs font-semibold uppercase tracking-wide text-slate-400">Technology Stack</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {Object.entries(technology_stack).map(([k, v]) => (
              <div key={k} className="rounded-lg border border-white/[.08] bg-white/[.04] px-3 py-1.5 text-xs">
                <span className="text-slate-500">{k}: </span>
                <span className="text-slate-200 font-medium">{v}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Vulnerabilities table */}
      {final_vulnerabilities?.length > 0 && (
        <div className="panel overflow-hidden">
          <div className="flex items-center justify-between px-5 py-3 border-b border-white/[.08]">
            <div className="flex items-center gap-2">
              <Bug size={14} className="text-red-400" />
              <span className="text-sm font-semibold">Final Vulnerabilities</span>
            </div>
            <span className="tag-danger text-[10px]">{final_vulnerabilities.length} issues</span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-white/[.06] text-slate-500">
                  <th className="px-4 py-2.5 text-left font-medium">Severity</th>
                  <th className="px-4 py-2.5 text-left font-medium">Tool</th>
                  <th className="px-4 py-2.5 text-left font-medium">Rule</th>
                  <th className="px-4 py-2.5 text-left font-medium">Message</th>
                </tr>
              </thead>
              <tbody>
                {final_vulnerabilities.map((issue, i) => (
                  <tr key={i} className="border-b border-white/[.04] hover:bg-white/[.03] transition-colors">
                    <td className="px-4 py-2">
                      <span className={sevMap[issue.severity] || 'sev-info'}>{issue.severity}</span>
                    </td>
                    <td className="px-4 py-2 text-slate-400">{issue.tool || '—'}</td>
                    <td className="px-4 py-2 font-mono text-slate-400">{issue.rule || '—'}</td>
                    <td className="px-4 py-2 text-slate-300 max-w-[300px] truncate">{issue.message || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}

/* ─────────────────────────────────────────────────────────────
   VS Code Explorer
───────────────────────────────────────────────────────────── */
function OutputExplorer({ filesDict, report, onRefresh, refreshing }) {
  const [activeFile, setActiveFile] = useState(null)
  const [openTabs, setOpenTabs] = useState([])           // [{path, content}]
  const [fileContents, setFileContents] = useState({})   // {path: content}
  const [loadingFile, setLoadingFile] = useState(null)
  const [activePanel, setActivePanel] = useState('explorer') // 'explorer' | 'security'

  // Build tree from filesDict (inline content) or from tree API
  const tree = useMemo(() => {
    if (!filesDict || Object.keys(filesDict).length === 0) return null
    return buildTreeFromFlat(filesDict)
  }, [filesDict])

  // Seed fileContents from the generation response
  useEffect(() => {
    if (filesDict) setFileContents(prev => ({ ...prev, ...filesDict }))
  }, [filesDict])

  // Auto-select first file
  useEffect(() => {
    if (filesDict && !activeFile) {
      const first = Object.keys(filesDict)[0]
      if (first) handleFileClick(first)
    }
  }, [filesDict])

  const handleFileClick = useCallback(async (path) => {
    setActiveFile(path)

    // Open tab if not already
    setOpenTabs(prev => {
      if (prev.find(t => t.path === path)) return prev
      return [...prev, { path }]
    })

    // If we already have content from generation response, use it
    if (fileContents[path] !== undefined && fileContents[path] !== null) return

    // Otherwise fetch from API
    setLoadingFile(path)
    try {
      const data = await apiFetch(`/api/output/file?path=${encodeURIComponent(path)}`)
      setFileContents(prev => ({ ...prev, [path]: data.content }))
    } catch {
      setFileContents(prev => ({ ...prev, [path]: '// Could not load file content.' }))
    } finally {
      setLoadingFile(null)
    }
  }, [fileContents])

  const closeTab = (path, e) => {
    e.stopPropagation()
    setOpenTabs(prev => {
      const next = prev.filter(t => t.path !== path)
      if (activeFile === path) {
        setActiveFile(next.length > 0 ? next[next.length - 1].path : null)
      }
      return next
    })
  }

  const activeContent = activeFile !== undefined ? fileContents[activeFile] : undefined
  const isLoading = loadingFile === activeFile

  return (
    <div className="vscode-shell">
      {/* Title bar */}
      <div className="vscode-titlebar">
        <div className="vscode-titlebar-dot bg-[#ff5f57]" />
        <div className="vscode-titlebar-dot bg-[#febc2e]" />
        <div className="vscode-titlebar-dot bg-[#28c840]" />
        <span className="mx-auto text-xs text-slate-500 font-medium select-none">
          AISAF — Output Explorer
        </span>
        <button
          onClick={onRefresh}
          disabled={refreshing}
          title="Refresh tree from server"
          className="ml-auto flex items-center gap-1.5 rounded-md px-2 py-1 text-xs text-slate-500 hover:bg-white/[.08] hover:text-slate-200 transition-colors disabled:opacity-40"
        >
          <RefreshCw size={12} className={refreshing ? 'animate-spin' : ''} />
          Refresh
        </button>
      </div>

      {/* Main body */}
      <div className="vscode-body">
        {/* Activity bar */}
        <div className="vscode-activity">
          <button
            title="Explorer"
            className={`vscode-activity-btn ${activePanel === 'explorer' ? 'active' : ''}`}
            onClick={() => setActivePanel('explorer')}
          >
            <FolderTree size={18} />
          </button>
          <button
            title="Security Report"
            className={`vscode-activity-btn ${activePanel === 'security' ? 'active' : ''}`}
            onClick={() => setActivePanel('security')}
          >
            <Shield size={18} />
          </button>
          <button
            title="Stats"
            className="vscode-activity-btn"
            onClick={() => setActivePanel('security')}
          >
            <BarChart2 size={18} />
          </button>
        </div>

        {/* Sidebar */}
        <div className="vscode-sidebar">
          <div className="vscode-sidebar-header">
            <span>{activePanel === 'explorer' ? 'Explorer' : 'Security'}</span>
            <span className="text-slate-600 font-normal normal-case tracking-normal">
              {tree ? `${Object.keys(filesDict || {}).length} files` : ''}
            </span>
          </div>
          <div className="vscode-sidebar-body py-1">
            {activePanel === 'explorer' ? (
              tree
                ? <TreeNode node={tree} depth={0} activeFile={activeFile} onFileClick={handleFileClick} />
                : (
                  <div className="px-4 py-8 text-center text-xs text-slate-600">
                    <FolderTree size={28} className="mx-auto mb-3 text-slate-700" />
                    No files yet.<br />Generate a project first.
                  </div>
                )
            ) : (
              <div className="p-3 space-y-2 text-xs">
                {report ? (
                  <>
                    <div className="rounded-lg border border-white/[.08] bg-white/[.04] p-3">
                      <div className="text-slate-500 mb-1">Final Score</div>
                      <div className={`text-lg font-bold ${report.final_security_score >= 90 ? 'text-mint' : 'text-yellow-400'}`}>
                        {report.final_security_score}/100
                      </div>
                    </div>
                    <div className="rounded-lg border border-white/[.08] bg-white/[.04] p-3">
                      <div className="text-slate-500 mb-1">Status</div>
                      <div className={report.status === 'SECURE' ? 'text-mint font-semibold' : 'text-yellow-400 font-semibold'}>
                        {report.status}
                      </div>
                    </div>
                    <div className="rounded-lg border border-white/[.08] bg-white/[.04] p-3">
                      <div className="text-slate-500 mb-1">Iterations</div>
                      <div className="text-slate-200 font-semibold">{report.iterations}</div>
                    </div>
                    <div className="rounded-lg border border-white/[.08] bg-white/[.04] p-3">
                      <div className="text-slate-500 mb-1">Vulnerabilities</div>
                      <div className="text-red-400 font-semibold">{report.final_vulnerabilities?.length ?? 0} issues</div>
                    </div>
                  </>
                ) : (
                  <div className="px-2 py-6 text-center text-slate-600">
                    <Shield size={24} className="mx-auto mb-2 text-slate-700" />
                    No report yet.
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Editor */}
        <div className="vscode-editor">
          {/* Tab bar */}
          {openTabs.length > 0 && (
            <div className="vscode-tabbar">
              {openTabs.map(tab => (
                <div
                  key={tab.path}
                  className={`vscode-tab ${activeFile === tab.path ? 'active' : ''}`}
                  onClick={() => handleFileClick(tab.path)}
                >
                  <FileIcon name={tab.path.split('/').pop()} size={12} />
                  <span>{tab.path.split('/').pop()}</span>
                  <span
                    className="vscode-tab-close"
                    onClick={(e) => closeTab(tab.path, e)}
                  >
                    <X size={10} />
                  </span>
                </div>
              ))}
            </div>
          )}

          {activeFile ? (
            <>
              <Breadcrumb path={activeFile} />
              {/* Toolbar */}
              <div className="flex items-center justify-between border-b border-white/[.06] px-4 py-1.5 bg-editor">
                <div className="flex items-center gap-2 text-xs text-slate-500">
                  <FileIcon name={activeFile.split('/').pop()} size={12} />
                  <span className="font-mono">{fileExt(activeFile) || 'txt'}</span>
                  {activeContent && (
                    <span className="text-slate-600">
                      · {activeContent.split('\n').length} lines
                    </span>
                  )}
                </div>
                {activeContent && <CopyButton value={activeContent} />}
              </div>

              {isLoading ? (
                <div className="vscode-empty">
                  <LoaderCircle size={24} className="animate-spin text-mint/40" />
                  <span className="text-xs">Loading…</span>
                </div>
              ) : (
                <CodeViewer content={activeContent ?? ''} filePath={activeFile} />
              )}
            </>
          ) : (
            <div className="vscode-empty">
              <Code2 size={40} className="text-slate-700" />
              <p className="text-sm">Select a file from the explorer</p>
              <p className="text-xs text-slate-600">Generated files will appear in the sidebar</p>
            </div>
          )}
        </div>
      </div>

      {/* Status bar */}
      <div className="vscode-statusbar">
        <div className="flex items-center gap-3">
          <span className="flex items-center gap-1">
            <span className="h-1.5 w-1.5 rounded-full bg-mint animate-pulse-soft" />
            AISAF
          </span>
          {activeFile && (
            <span className="text-green-300/50">{activeFile.split('/').pop()}</span>
          )}
        </div>
        <div className="flex items-center gap-4 text-green-300/50">
          {tree && <span>{Object.keys(filesDict || {}).length} files</span>}
          {report && <span>Score: {report.final_security_score}/100</span>}
          <span>AISAF v1.0</span>
        </div>
      </div>
    </div>
  )
}

/* ─────────────────────────────────────────────────────────────
   Reports View (PDF Generation)
───────────────────────────────────────────────────────────── */
function ReportsView({ onBack }) {
  const [reports, setReports] = useState([])
  const [selectedReport, setSelectedReport] = useState(null)
  const [reportData, setReportData] = useState(null)
  const [loading, setLoading] = useState(true)
  const reportRef = useRef()

  useEffect(() => {
    apiFetch('/api/reports/list').then(data => {
      setReports(data)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  const loadReport = async (filename) => {
    setSelectedReport(filename)
    setReportData(null)
    try {
      const data = await apiFetch(`/api/reports/file?filename=${encodeURIComponent(filename)}`)
      if (filename.endsWith('.json')) {
        setReportData(JSON.parse(data.content))
      } else {
        setReportData({ raw: data.content })
      }
    } catch (e) {
      console.error(e)
    }
  }

  const downloadPDF = () => {
    if (!reportRef.current) return
    const opt = {
      margin: 10,
      filename: selectedReport.replace('.json', '.pdf'),
      image: { type: 'jpeg', quality: 0.98 },
      html2canvas: { scale: 2, useCORS: true },
      jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
    }
    html2pdf().set(opt).from(reportRef.current).save()
  }

  return (
    <div className="flex-1 w-full px-4 pb-4 flex flex-col animate-fade-in max-w-[100vw]">
      <div className="mb-4 flex items-center justify-between">
        <button onClick={onBack} className="btn-secondary text-xs py-1.5 px-3">
          &larr; Back to Home
        </button>
      </div>

      <div className="flex flex-1 gap-4 overflow-hidden h-[calc(100vh-8rem)]">
        {/* Sidebar */}
        <div className="w-64 flex flex-col panel p-4 overflow-y-auto">
          <h3 className="font-semibold text-sm mb-4 text-slate-300">Generated Reports</h3>
          {loading ? (
            <div className="text-xs text-slate-500">Loading...</div>
          ) : reports.length === 0 ? (
            <div className="text-xs text-slate-500">No reports found.</div>
          ) : (
            <div className="space-y-1">
              {reports.map(r => (
                <button
                  key={r.name}
                  onClick={() => loadReport(r.name)}
                  className={`w-full text-left px-3 py-2 rounded-lg text-xs transition-colors ${selectedReport === r.name ? 'bg-mint/10 text-mint font-medium' : 'text-slate-400 hover:bg-white/5'}`}
                >
                  <FileText size={14} className="inline-block mr-2 opacity-70" />
                  {r.name}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Content Viewer */}
        <div className="flex-1 panel p-6 overflow-y-auto bg-slate-900 flex justify-center">
          {selectedReport && reportData ? (
            <div className="w-full max-w-[210mm] flex flex-col items-center">
              <div className="w-full flex justify-end mb-4">
                <button onClick={downloadPDF} className="btn-primary text-xs py-1.5 px-4 shadow-lg shadow-mint/20">
                  Download as PDF
                </button>
              </div>

              {/* A4 Report Container */}
              <div ref={reportRef} className="bg-white text-slate-900 p-[20mm] shadow-xl min-h-[297mm] w-[210mm] rounded-sm text-left">
                {selectedReport.endsWith('.json') && reportData.status ? (
                  <div>
                    <div className="border-b-2 border-slate-200 pb-6 mb-8 flex justify-between items-end">
                      <div>
                        <h1 className="text-4xl font-bold text-slate-900 mb-2">AISAF Security Audit</h1>
                        <p className="text-slate-500">Generated on {reportData.timestamp}</p>
                      </div>
                      <div className="text-right">
                        <div className="text-sm font-semibold uppercase text-slate-400 tracking-wider">Overall Score</div>
                        <div className={`text-4xl font-black ${reportData.final_security_score >= 90 ? 'text-green-600' : 'text-yellow-600'}`}>
                          {reportData.final_security_score}/100
                        </div>
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-8 mb-8">
                      <div>
                        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-400 mb-3 border-b border-slate-100 pb-2">Tech Stack</h3>
                        <table className="w-full text-sm">
                          <tbody>
                            {Object.entries(reportData.technology_stack || {}).map(([k, v]) => v && (
                              <tr key={k} className="border-b border-slate-50">
                                <td className="py-2 text-slate-500 capitalize">{k.replace('_', ' ')}</td>
                                <td className="py-2 font-medium text-slate-800 text-right">{v}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>

                      <div>
                        <h3 className="text-sm font-bold uppercase tracking-wider text-slate-400 mb-3 border-b border-slate-100 pb-2">Framework Info</h3>
                        <table className="w-full text-sm">
                          <tbody>
                            <tr className="border-b border-slate-50">
                              <td className="py-2 text-slate-500">Status</td>
                              <td className={`py-2 font-bold text-right ${reportData.status === 'SECURE' ? 'text-green-600' : 'text-red-600'}`}>{reportData.status}</td>
                            </tr>
                            <tr className="border-b border-slate-50">
                              <td className="py-2 text-slate-500">Iterations</td>
                              <td className="py-2 font-medium text-right text-slate-800">{reportData.iterations}</td>
                            </tr>
                            <tr className="border-b border-slate-50">
                              <td className="py-2 text-slate-500">Init. Score</td>
                              <td className="py-2 font-medium text-right text-slate-800">{reportData.initial_security_score}</td>
                            </tr>
                          </tbody>
                        </table>
                      </div>
                    </div>

                    <div className="mb-8">
                      <h3 className="text-sm font-bold uppercase tracking-wider text-slate-400 mb-3 border-b border-slate-100 pb-2">Threat Models</h3>
                      <div className="flex gap-6">
                        <div className="flex-1">
                          <h4 className="text-xs font-semibold text-slate-500 mb-2">OWASP Domains</h4>
                          <ul className="list-disc pl-4 text-sm text-slate-700 space-y-1">
                            {reportData.owasp_domains?.map(d => <li key={d}>{d}</li>)}
                          </ul>
                        </div>
                        <div className="flex-1">
                          <h4 className="text-xs font-semibold text-slate-500 mb-2">MITRE ATLAS</h4>
                          <ul className="list-disc pl-4 text-sm text-slate-700 space-y-1">
                            {reportData.mitre_atlas?.map(d => <li key={d}>{d}</li>)}
                          </ul>
                        </div>
                      </div>
                    </div>
                  </div>
                ) : selectedReport.endsWith('.html') ? (
                  <iframe
                    title="HTML Report"
                    srcDoc={reportData.raw}
                    className="w-full min-h-[297mm] border-0 bg-white"
                  />
                ) : (
                  <pre className="text-xs font-mono whitespace-pre-wrap text-slate-700">{reportData.raw}</pre>
                )}
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center text-slate-500 h-full">
              <FileText size={48} className="mb-4 opacity-20" />
              <p className="text-sm">Select a report to view and download</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

/* ─────────────────────────────────────────────────────────────
   Main App
───────────────────────────────────────────────────────────── */
const SAMPLE = 'Build a FastAPI service for a team task manager with JWT authentication, roles, PostgreSQL, and a React dashboard.'

export default function App() {
  const [requirement, setRequirement] = useState(SAMPLE)
  const [report, setReport] = useState(null)
  const [filesDict, setFilesDict] = useState(null) // {path: content}
  const [loading, setLoading] = useState('')       // '' | 'generate'
  const [error, setError] = useState('')
  const [apiStatus, setApiStatus] = useState('checking') // 'ok' | 'error' | 'checking'
  const [refreshing, setRefreshing] = useState(false)
  const [viewMode, setViewMode] = useState('home') // 'home' | 'explorer'

  // Health check
  useEffect(() => {
    apiFetch('/api/health')
      .then(() => setApiStatus('ok'))
      .catch(() => setApiStatus('error'))
  }, [])

  const fetchTree = useCallback(async () => {
    setRefreshing(true)
    try {
      const tree = await apiFetch('/api/output/tree')
      // Flatten tree to {path: ''} stubs so the explorer shows the structure
      // actual content loaded on click
      const flat = {}
      function walk(node) {
        if (node.type === 'file') { flat[node.path] = null } // null = not yet loaded
        if (node.children) node.children.forEach(walk)
      }
      walk(tree)
      if (Object.keys(flat).length > 0) setFilesDict(prev => {
        // Merge: keep existing content, add new paths
        const merged = { ...flat }
        if (prev) Object.entries(prev).forEach(([k, v]) => { if (v !== null) merged[k] = v })
        return merged
      })
    } catch { /* silent */ } finally {
      setRefreshing(false)
    }
  }, [])

  const generate = async () => {
    if (requirement.trim().length < 3) {
      setError('Describe the software to build (at least 3 characters).')
      return
    }
    setError('')
    setLoading('generate')
    try {
      const data = await apiPost('/api/generate', { requirement })
      setReport(data)
      // data.files may not exist in the report — the pipeline saves files to disk
      // If the report has a `files` key we use it, otherwise fetch tree from server
      if (data.files && Object.keys(data.files).length > 0) {
        setFilesDict(data.files)
      } else {
        await fetchTree()
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading('')
    }
  }

  return (
    <main className={`min-h-screen ${viewMode === 'explorer' ? 'flex flex-col' : ''}`}>
      {/* ── Navbar ──────────────────────────────────────── */}
      <nav className="mx-auto flex max-w-7xl items-center justify-between w-full px-6 py-5 lg:px-8">
        <div className="flex items-center gap-3">
          <div className="grid h-10 w-10 place-items-center rounded-xl bg-mint text-ink shadow-glow">
            <ShieldCheck size={22} strokeWidth={2.5} />
          </div>
          <div>
            <div className="font-semibold tracking-tight">AISAF</div>
            <div className="text-xs text-slate-500">Secure Architecture Framework</div>
          </div>
        </div>

        <div className="absolute left-1/2 -translate-x-1/2 flex items-center gap-6">
          <button onClick={() => setViewMode('home')} className={`text-sm font-medium transition-colors ${viewMode === 'home' ? 'text-mint' : 'text-slate-400 hover:text-slate-200'}`}>Home</button>
          <button onClick={() => setViewMode('explorer')} className={`text-sm font-medium transition-colors ${viewMode === 'explorer' ? 'text-mint' : 'text-slate-400 hover:text-slate-200'}`}>Explorer</button>
          <button onClick={() => setViewMode('reports')} className={`text-sm font-medium transition-colors ${viewMode === 'reports' ? 'text-mint' : 'text-slate-400 hover:text-slate-200'}`}>Security Reports</button>
        </div>

        <div className="flex items-center gap-4">
          <div className={`hidden items-center gap-2 text-xs sm:flex ${apiStatus === 'ok' ? 'text-slate-400' : 'text-red-400'}`}>
            <span className={`h-2 w-2 rounded-full ${apiStatus === 'ok' ? 'bg-mint shadow-[0_0_8px_#8ce7b3]' :
                apiStatus === 'error' ? 'bg-red-400' : 'bg-yellow-400 animate-pulse'
              }`} />
            {apiStatus === 'ok' ? 'Backend online' : apiStatus === 'error' ? 'Backend offline' : 'Connecting…'}
          </div>
        </div>
      </nav>

      {viewMode === 'reports' ? (
        <ReportsView onBack={() => setViewMode('home')} />
      ) : viewMode === 'home' ? (
        <div className="mx-auto max-w-7xl px-6 pb-20 lg:px-8 w-full">
          {/* ── Hero ──────────────────────────────────────── */}
          <div className="mx-auto max-w-3xl text-center mb-10">
            <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-mint/20 bg-mint/10 px-3 py-1.5 text-xs font-medium text-mint">
              <Sparkles size={13} />
              OWASP + MITRE ATLAS — security-first code generation
            </div>
            <h1 className="text-4xl font-semibold tracking-[-0.04em] text-white sm:text-5xl">
              Design software with{' '}
              <span className="text-mint">security built in.</span>
            </h1>
            <p className="mx-auto mt-4 max-w-2xl text-sm leading-7 text-slate-400">
              Describe your application. AISAF maps OWASP and MITRE ATLAS risks,
              generates a full multi-file project, scans for vulnerabilities,
              and auto-remediates — all before you write a line of code.
            </p>
          </div>

          {/* ── Generation panel ──────────────────────────── */}
          <div className="panel p-5 sm:p-7 mb-6">
            <div className="mb-4 flex items-center justify-between">
              <label htmlFor="requirement" className="flex items-center gap-2 text-sm font-medium">
                <Code2 size={16} className="text-mint" />
                What are you building?
              </label>
              <button
                onClick={() => setRequirement(SAMPLE)}
                className="text-xs text-mint/70 hover:text-mint transition-colors"
              >
                Use example
              </button>
            </div>

            <textarea
              id="requirement"
              value={requirement}
              onChange={e => setRequirement(e.target.value)}
              rows={5}
              placeholder="Describe your application, users, and technical requirements…"
              className="w-full resize-none rounded-xl border border-white/[.08] bg-black/20 p-4 font-mono text-sm leading-6 text-slate-200 outline-none placeholder:text-slate-600 focus:border-mint/40 focus:ring-2 focus:ring-mint/10 transition-all"
            />

            <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <p className="flex items-center gap-1.5 text-xs text-slate-500">
                <LockKeyhole size={13} />
                Requirements are analyzed for applicable security controls before generation.
              </p>
              <div className="flex items-center gap-3">
                <button
                  disabled={!!loading}
                  onClick={generate}
                  className="btn-primary min-w-[160px]"
                >
                  {loading === 'generate'
                    ? <><LoaderCircle className="animate-spin" size={16} /> Generating…</>
                    : <>Generate project <ArrowRight size={15} /></>}
                </button>
              </div>
            </div>

            {error && (
              <div className="mt-4 flex gap-2 rounded-lg border border-red-400/25 bg-red-400/10 p-3 text-sm text-red-200 animate-fade-in">
                <AlertCircle size={17} className="shrink-0 mt-0.5" />
                {error}
              </div>
            )}
          </div>

          {/* ── Security dashboard ──────────────────────────── */}
          <SecurityDashboard report={report} />

          {/* ── Button to Open Dashboard ───────────────────────────── */}
          {(filesDict || report) && (
            <div className="mt-8 flex justify-center animate-fade-in">
              <button
                onClick={() => setViewMode('explorer')}
                className="btn-primary py-3 px-8 text-base shadow-lg shadow-mint/20 flex items-center gap-2"
              >
                <FolderTree size={18} />
                Go to Dashboard
              </button>
            </div>
          )}

          {/* ── Empty state when no generation yet ─────────── */}
          {!filesDict && !report && !loading && (
            <div className="mt-16 flex flex-col items-center gap-4 text-slate-600">
              <div className="grid h-20 w-20 place-items-center rounded-2xl border border-white/[.06] bg-white/[.03]">
                <FolderTree size={36} />
              </div>
              <p className="text-sm">Your generated project will appear here</p>
              <p className="text-xs">Enter a requirement above and click <span className="text-mint">Generate project</span></p>
            </div>
          )}
        </div>
      ) : (
        <div className="flex-1 w-full px-4 pb-4 flex flex-col animate-fade-in max-w-[100vw]">
          <div className="mb-4">
            <button onClick={() => setViewMode('home')} className="btn-secondary text-xs py-1.5 px-3">
              &larr; Back to Home
            </button>
          </div>
          <OutputExplorer
            filesDict={filesDict}
            report={report}
            onRefresh={fetchTree}
            refreshing={refreshing}
          />
        </div>
      )}
    </main>
  )
}
