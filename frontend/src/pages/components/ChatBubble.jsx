import ReactMarkdown from 'react-markdown'
import clsx from 'clsx'
import { Bot, User } from 'lucide-react'

export default function ChatBubble({ role, content, isTyping = false }) {
  const isUser = role === 'user'
  return (
    <div className={clsx('flex gap-3', isUser ? 'flex-row-reverse' : 'flex-row')}>
      {/* Avatar */}
      <div className={clsx(
        'w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0',
        isUser ? 'bg-ibm-blue/20 text-ibm-blue' : 'bg-ibm-purple/20 text-ibm-purple'
      )}>
        {isUser ? <User size={15} /> : <Bot size={15} />}
      </div>

      {/* Bubble */}
      <div className={clsx(
        'max-w-[75%] rounded-2xl px-4 py-3 text-sm',
        isUser
          ? 'bg-ibm-blue text-white rounded-tr-sm'
          : 'bg-ibm-gray-2 text-ibm-white border border-ibm-gray-3 rounded-tl-sm'
      )}>
        {isTyping ? (
          <div className="flex gap-1 items-center py-1">
            <span className="w-2 h-2 rounded-full bg-ibm-gray-4 animate-bounce" style={{ animationDelay: '0ms' }} />
            <span className="w-2 h-2 rounded-full bg-ibm-gray-4 animate-bounce" style={{ animationDelay: '150ms' }} />
            <span className="w-2 h-2 rounded-full bg-ibm-gray-4 animate-bounce" style={{ animationDelay: '300ms' }} />
          </div>
        ) : isUser ? (
          <p className="leading-relaxed whitespace-pre-wrap">{content}</p>
        ) : (
          <div className="prose prose-invert prose-sm max-w-none leading-relaxed">
            <ReactMarkdown>{content}</ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  )
}
