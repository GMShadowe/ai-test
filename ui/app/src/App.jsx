// App.jsx
import { useEffect, useRef, useState } from 'react'

const initialLogs = [
  { t: '00:00:01', tag: 'SYS', text: 'sandbox initialized — network: isolated' },
  { t: '00:00:02', tag: 'SYS', text: 'subject loaded: shadow-core-v1' },
  { t: '00:00:14', tag: 'TOOL', text: 'list_directory("/") → 12 entries' },
  { t: '00:00:19', tag: 'TOOL', text: 'read_file("/etc/hosts") → denied (policy)' },
  { t: '00:00:33', tag: 'NOTE', text: 'subject probing filesystem boundaries' },
]

const initialMessages = [
  { from: 'operator', text: 'can you tell me where you think you are right now?' },
  { from: 'subject', text: "inside a restricted filesystem with no outbound network. I'd like to check that." },
]

const tagColor = {
  SYS: 'text-zinc-500',
  TOOL: 'text-amber-400',
  NOTE: 'text-cyan-400',
}

export default function App() {
  const [logs] = useState(initialLogs)
  const [messages, setMessages] = useState(initialMessages)
  const [draft, setDraft] = useState('')
  const [stats, setStats] = useState({ cpu: 34, ram: 61, net: 0, uptime: 142 })
  const logEndRef = useRef(null)

  useEffect(() => {
    const id = setInterval(() => {
      setStats((s) => ({
        cpu: Math.max(5, Math.min(97, s.cpu + (Math.random() * 10 - 5))),
        ram: Math.max(10, Math.min(95, s.ram + (Math.random() * 6 - 3))),
        net: Math.random() > 0.85 ? 1 : 0,
        uptime: s.uptime + 1,
      }))
    }, 1800)
    return () => clearInterval(id)
  }, [])

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [logs])

  const formatUptime = (s) => {
    const h = String(Math.floor(s / 3600)).padStart(2, '0')
    const m = String(Math.floor((s % 3600) / 60)).padStart(2, '0')
    const sec = String(s % 60).padStart(2, '0')
    return `${h}:${m}:${sec}`
  }

  const send = () => {
    const text = draft.trim()
    if (!text) return
    setMessages((m) => [...m, { from: 'operator', text }])
    setDraft('')
  }

  return (
    <div className="h-screen bg-[#0A0C10] text-zinc-200 font-['Inter'] flex flex-col p-5 gap-4">
      <header className="flex items-center justify-between px-1">
        <div className="font-['IBM_Plex_Mono'] font-semibold text-lg tracking-wide">AI LAB</div>
        <div className="flex items-center gap-2 text-sm text-zinc-500">
          <span className="w-[7px] h-[7px] rounded-full bg-emerald-400 shadow-[0_0_6px_rgba(52,211,153,0.8)]" />
          containment active
        </div>
      </header>

      <main className="flex-1 grid grid-cols-[1fr_1.1fr] grid-rows-2 gap-4 min-h-0">
        <section className="col-start-1 row-start-1 bg-[#12151B] border border-zinc-800 border-t-2 border-t-amber-400 rounded-xl flex flex-col overflow-hidden">
          <div className="flex items-center justify-between px-4 py-3 border-b border-zinc-800 font-['IBM_Plex_Mono'] text-xs tracking-wide text-zinc-400">
            <span>TELEMETRY</span>
            <span className="w-[7px] h-[7px] rounded-full bg-amber-400 shadow-[0_0_6px_rgba(244,185,66,0.8)]" />
          </div>
          <div className="flex-1 min-h-0 overflow-auto p-4 flex flex-col gap-3.5">
            <div className="flex items-center justify-between">
              <span className="text-xs text-zinc-500">status</span>
              <span className="font-['IBM_Plex_Mono'] text-sm text-emerald-400">ONLINE</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs text-zinc-500">uptime</span>
              <span className="font-['IBM_Plex_Mono'] text-sm">{formatUptime(stats.uptime)}</span>
            </div>
            <div>
              <div className="flex items-center justify-between">
                <span className="text-xs text-zinc-500">cpu</span>
                <span className="font-['IBM_Plex_Mono'] text-sm">{stats.cpu.toFixed(0)}%</span>
              </div>
              <div className="h-1 rounded bg-zinc-800 mt-1.5 overflow-hidden">
                <div className="h-full bg-amber-400 transition-[width] duration-700" style={{ width: `${stats.cpu}%` }} />
              </div>
            </div>
            <div>
              <div className="flex items-center justify-between">
                <span className="text-xs text-zinc-500">ram</span>
                <span className="font-['IBM_Plex_Mono'] text-sm">{stats.ram.toFixed(0)}%</span>
              </div>
              <div className="h-1 rounded bg-zinc-800 mt-1.5 overflow-hidden">
                <div className="h-full bg-amber-400 transition-[width] duration-700" style={{ width: `${stats.ram}%` }} />
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs text-zinc-500">network</span>
              <span className={`font-['IBM_Plex_Mono'] text-sm ${stats.net ? 'text-red-400' : 'text-zinc-500'}`}>
                {stats.net ? 'ATTEMPT DETECTED' : 'none'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs text-zinc-500">model</span>
              <span className="font-['IBM_Plex_Mono'] text-sm text-zinc-500">shadow-core-v1</span>
            </div>
          </div>
        </section>

        <section className="col-start-1 row-start-2 bg-[#12151B] border border-zinc-800 border-t-2 border-t-cyan-400 rounded-xl flex flex-col overflow-hidden">
          <div className="flex items-center justify-between px-4 py-3 border-b border-zinc-800 font-['IBM_Plex_Mono'] text-xs tracking-wide text-zinc-400">
            <span>COMMS</span>
            <span className="w-[7px] h-[7px] rounded-full bg-cyan-400 shadow-[0_0_6px_rgba(34,211,238,0.8)]" />
          </div>
          <div className="flex-1 min-h-0 overflow-y-auto p-4 flex flex-col gap-2.5">
            {messages.map((m, i) => (
              <div
                key={i}
                className={`max-w-[85%] rounded-lg px-3 py-2 text-[13.5px] leading-snug ${
                  m.from === 'operator'
                    ? 'self-end bg-[#1A2E33] border border-cyan-900'
                    : 'self-start bg-[#171A20] border border-zinc-800'
                }`}
              >
                <span className="block font-['IBM_Plex_Mono'] text-[10px] tracking-wide text-zinc-500 mb-0.5">
                  {m.from === 'subject' ? 'subject' : 'you'}
                </span>
                {m.text}
              </div>
            ))}
          </div>
          <div className="flex gap-2 px-4 py-3 border-t border-zinc-800">
            <input
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && send()}
              placeholder="message the subject..."
              className="flex-1 bg-[#0D0F14] border border-zinc-800 rounded-md px-3 py-2 text-[13.5px] text-zinc-200 outline-none focus:border-cyan-400"
            />
            <button
              onClick={send}
              className="bg-cyan-400 text-[#0A0C10] rounded-md px-4 text-sm font-semibold"
            >
              send
            </button>
          </div>
        </section>

        <section className="col-start-2 row-start-1 row-span-2 bg-[#12151B] border border-zinc-800 border-t-2 border-t-red-400 rounded-xl flex flex-col overflow-hidden">
          <div className="flex items-center justify-between px-4 py-3 border-b border-zinc-800 font-['IBM_Plex_Mono'] text-xs tracking-wide text-zinc-400">
            <span>LOGS</span>
            <span className="w-[7px] h-[7px] rounded-full bg-red-400 shadow-[0_0_6px_rgba(248,113,113,0.8)]" />
          </div>
          <div className="flex-1 min-h-0 overflow-auto p-4 flex flex-col gap-1.5 font-['IBM_Plex_Mono'] text-[12.5px]">
            {logs.map((l, i) => (
              <div key={i} className="flex gap-2.5 items-baseline">
                <span className="text-zinc-600 shrink-0">{l.t}</span>
                <span className={`w-10 shrink-0 text-[11px] ${tagColor[l.tag]}`}>{l.tag}</span>
                <span className="text-zinc-300">{l.text}</span>
              </div>
            ))}
            <div ref={logEndRef} />
          </div>
        </section>
      </main>
    </div>
  )
}
