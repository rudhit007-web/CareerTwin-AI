import { useState, useEffect, useRef } from 'react'
import { chatAPI } from '../api/client'
import ChatBubble from '../components/ChatBubble'
import { MessageSquare, Plus, Send, Trash2, Bot } from 'lucide-react'
import toast from 'react-hot-toast'
import clsx from 'clsx'

export default function Chat() {
  const [sessions,        setSessions]       = useState([])
  const [activeSession,   setActiveSession]  = useState(null)
  const [messages,        setMessages]       = useState([])
  const [input,           setInput]          = useState('')
  const [sending,         setSending]        = useState(false)
  const [loadingSessions, setLoadingSessions]= useState(true)
  const bottomRef = useRef(null)

  // Load all sessions on mount
  useEffect(() => {
    chatAPI.getSessions()
      .then(r => setSessions(r.data.sessions || []))
      .catch(() => {})
      .finally(() => setLoadingSessions(false))
  }, [])

  // Scroll to bottom on new message
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, sending])

  const openSession = async (sessionId) => {
    try {
      const res = await chatAPI.getSession(sessionId)
      setActiveSession(res.data)
      setMessages(res.data.messages || [])
    } catch {
      toast.error('Could not load conversation.')
    }
  }

  const createNewSession = async () => {
    try {
      const res = await chatAPI.createSession({ title: 'New Conversation' })
      const newSession = { id: res.data.session_id, title: 'New Conversation', updated_at: new Date().toISOString() }
      setSessions(s => [newSession, ...s])
      setActiveSession(newSession)
      setMessages([])
    } catch {
      toast.error('Could not create session.')
    }
  }

  const deleteSession = async (id) => {
    await chatAPI.deleteSession(id)
    setSessions(s => s.filter(x => x.id !== id))
    if (activeSession?.id === id) { setActiveSession(null); setMessages([]) }
    toast.success('Conversation archived.')
  }

  const sendMessage = async (e) => {
    e.preventDefault()
    const msg = input.trim()
    if (!msg || !activeSession) return
    if (!msg) { toast.error('Please enter a message.'); return }

    // Optimistically show user message
    const userMsg = { id: Date.now(), role: 'user', content: msg }
    setMessages(m => [...m, userMsg])
    setInput('')
    setSending(true)

    try {
      const res = await chatAPI.sendMessage(activeSession.id, msg)
      setMessages(m => [...m, { id: res.data.message_id, role: 'assistant', content: res.data.reply }])
      // Update session title in sidebar if it was the first message
      setSessions(s => s.map(sess =>
        sess.id === activeSession.id
          ? { ...sess, title: msg.slice(0, 50) + (msg.length > 50 ? '…' : '') }
          : sess
      ))
    } catch {
      toast.error('Failed to get response from AI.')
      setMessages(m => m.filter(x => x.id !== userMsg.id))
    } finally {
      setSending(false)
    }
  }

  return (
    <div className="flex h-[calc(100vh-64px)] -mx-6 -my-8 overflow-hidden">
      {/* Sessions sidebar */}
      <div className="w-64 flex-shrink-0 bg-ibm-gray border-r border-ibm-gray-2 flex flex-col">
        <div className="px-4 py-3 border-b border-ibm-gray-2">
          <button onClick={createNewSession} className="btn-primary w-full flex items-center justify-center gap-2 text-sm py-2">
            <Plus size={15} /> New Chat
          </button>
        </div>
        <div className="flex-1 overflow-y-auto px-2 py-2 space-y-1">
          {loadingSessions && <p className="text-xs text-ibm-gray-4 text-center py-4">Loading…</p>}
          {!loadingSessions && sessions.length === 0 && (
            <p className="text-xs text-ibm-gray-4 text-center py-8">No conversations yet.<br />Start a new chat!</p>
          )}
          {sessions.map(s => (
            <div
              key={s.id}
              className={clsx(
                'flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer group transition-colors duration-150',
                activeSession?.id === s.id ? 'bg-ibm-blue/20 border border-ibm-blue/40' : 'hover:bg-ibm-gray-2'
              )}
              onClick={() => openSession(s.id)}
            >
              <MessageSquare size={13} className="text-ibm-gray-4 flex-shrink-0" />
              <p className="text-xs text-ibm-white truncate flex-1">{s.title}</p>
              <button
                onClick={e => { e.stopPropagation(); deleteSession(s.id) }}
                className="opacity-0 group-hover:opacity-100 text-ibm-gray-4 hover:text-ibm-red transition-all"
              >
                <Trash2 size={12} />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Chat area */}
      <div className="flex-1 flex flex-col bg-ibm-dark">
        {!activeSession ? (
          <div className="flex-1 flex flex-col items-center justify-center text-center px-8">
            <div className="w-16 h-16 rounded-2xl bg-ibm-blue/20 border border-ibm-blue/30 flex items-center justify-center mb-4">
              <Bot size={28} className="text-ibm-blue" />
            </div>
            <h2 className="text-xl font-bold text-ibm-white mb-2">CareerTwin AI Chat</h2>
            <p className="text-ibm-gray-4 text-sm mb-6 max-w-sm">
              Powered by IBM Granite. Ask anything about your career, resume, skills, or job preparation.
            </p>
            <button onClick={createNewSession} className="btn-primary flex items-center gap-2">
              <Plus size={15} /> Start New Conversation
            </button>
          </div>
        ) : (
          <>
            {/* Header */}
            <div className="px-6 py-3 border-b border-ibm-gray-2 flex items-center gap-3">
              <Bot size={18} className="text-ibm-blue" />
              <span className="text-sm font-medium text-ibm-white">{activeSession.title || 'New Conversation'}</span>
              <span className="badge badge-blue ml-auto">IBM Granite</span>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto px-6 py-6 space-y-4">
              {messages.length === 0 && (
                <div className="text-center py-12">
                  <p className="text-ibm-gray-4 text-sm">Start the conversation — ask me anything about your career!</p>
                  <div className="mt-4 flex flex-wrap justify-center gap-2">
                    {['What skills should I learn for AI/ML?', 'Review my career roadmap', 'Prepare me for interviews', 'Suggest IBM certifications'].map(q => (
                      <button
                        key={q}
                        onClick={() => { setInput(q) }}
                        className="text-xs bg-ibm-gray-2 hover:bg-ibm-gray-3 text-ibm-gray-4 hover:text-ibm-white px-3 py-1.5 rounded-full transition-colors"
                      >
                        {q}
                      </button>
                    ))}
                  </div>
                </div>
              )}
              {messages.map(m => <ChatBubble key={m.id} role={m.role} content={m.content} />)}
              {sending && <ChatBubble role="assistant" content="" isTyping />}
              <div ref={bottomRef} />
            </div>

            {/* Input */}
            <form onSubmit={sendMessage} className="px-6 py-4 border-t border-ibm-gray-2">
              <div className="flex gap-3">
                <input
                  className="input flex-1"
                  placeholder="Ask CareerTwin AI anything about your career…"
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  disabled={sending}
                  onKeyDown={e => e.key === 'Enter' && !e.shiftKey && sendMessage(e)}
                />
                <button type="submit" className="btn-primary px-4 flex-shrink-0" disabled={sending || !input.trim()}>
                  <Send size={16} />
                </button>
              </div>
              <p className="text-xs text-ibm-gray-4 mt-2 text-center">IBM Granite via watsonx.ai · Responses may vary</p>
            </form>
          </>
        )}
      </div>
    </div>
  )
}
