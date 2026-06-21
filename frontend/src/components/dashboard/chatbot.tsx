import { useState, useRef, useEffect } from 'react';
import { sendChatMessage } from '@/lib/api';
import { useTheme } from '@/contexts/ThemeContext';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

const QUICK_PROMPTS = [
  'Analyze AAPL risk',
  'Summarize crypto news',
  'Market sentiment today',
  'Top movers alert',
  'What are the highest impact events?',
  'Compare NVDA vs AMD sentiment',
];

function renderMarkdown(text: string) {
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code class="px-1 py-0.5 rounded bg-[var(--bg-elevated)] text-cyan-500 text-xs">$1</code>')
    .replace(/^### (.*$)/gm, '<h3 class="text-sm font-bold text-[var(--text-primary)] mt-2 mb-1">$1</h3>')
    .replace(/^## (.*$)/gm, '<h2 class="text-base font-bold text-[var(--text-primary)] mt-2 mb-1">$1</h2>')
    .replace(/^# (.*$)/gm, '<h1 class="text-lg font-bold text-[var(--text-primary)] mt-2 mb-1">$1</h1>')
    .replace(/^- (.*$)/gm, '<li class="ml-3 list-disc text-[var(--text-secondary)]">$1</li>')
    .replace(/^(\d+)\. (.*$)/gm, '<li class="ml-3 list-decimal text-[var(--text-secondary)]">$2</li>')
    .replace(/\n/g, '<br/>');
}

export default function Chatbot() {
  const { theme } = useTheme();
  const light = theme === 'light';
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>(() => {
    try {
      const saved = localStorage.getItem('chat-history');
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo(0, scrollRef.current.scrollHeight);
  }, [messages]);

  useEffect(() => {
    localStorage.setItem('chat-history', JSON.stringify(messages.slice(-50)));
  }, [messages]);

  const handleSend = async (text?: string) => {
    const msg = text || input.trim();
    if (!msg) return;

    setMessages((prev) => [...prev, { role: 'user', content: msg }]);
    setInput('');
    setLoading(true);

    const reply = await sendChatMessage(msg);
    setMessages((prev) => [...prev, { role: 'assistant', content: reply }]);
    setLoading(false);
  };

  const clearChat = () => {
    setMessages([]);
    localStorage.removeItem('chat-history');
  };

  return (
    <>
      {/* Floating Toggle Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 z-50 w-14 h-14 rounded-full flex items-center justify-center transition-all duration-300 hover:scale-110"
        style={{
          background: 'linear-gradient(135deg, #00f0ff 0%, #8b5cf6 100%)',
          boxShadow: light
            ? '0 4px 20px rgba(0,240,255,0.3)'
            : '0 0 25px rgba(0,240,255,0.5), 0 0 50px rgba(139,92,246,0.3)',
        }}
      >
        <svg xmlns="http://www.w3.org/2000/svg" className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
          {isOpen ? (
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
          ) : (
            <path strokeLinecap="round" strokeLinejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          )}
        </svg>
      </button>

      {/* Chat Panel */}
      {isOpen && (
        <div
          className="fixed bottom-24 right-6 z-50 w-[380px] h-[520px] rounded-2xl flex flex-col overflow-hidden"
          style={{
            background: light ? 'rgba(255,255,255,0.92)' : 'rgba(10,10,20,0.85)',
            backdropFilter: 'blur(24px)',
            border: light ? '1px solid rgba(0,0,0,0.08)' : '1px solid rgba(0,240,255,0.2)',
            boxShadow: light
              ? '0 8px 40px rgba(0,0,0,0.12)'
              : '0 0 30px rgba(0,240,255,0.15), 0 0 60px rgba(139,92,246,0.1)',
          }}
        >
          {/* Header */}
          <div
            className="px-4 py-3 flex items-center gap-3"
            style={{
              background: light
                ? 'linear-gradient(90deg, rgba(6,182,212,0.08) 0%, rgba(139,92,210,0.08) 100%)'
                : 'linear-gradient(90deg, rgba(0,240,255,0.15) 0%, rgba(139,92,246,0.15) 100%)',
              borderBottom: light ? '1px solid rgba(0,0,0,0.06)' : '1px solid rgba(0,240,255,0.2)',
            }}
          >
            <div
              className="w-9 h-9 rounded-full flex items-center justify-center text-white font-bold text-sm"
              style={{ background: 'linear-gradient(135deg, #00f0ff 0%, #8b5cf6 100%)' }}
            >
              N
            </div>
            <div className="flex-1">
              <div className={`font-semibold text-sm ${light ? 'text-slate-800' : 'text-white'}`}>Neural Engine AI</div>
              <div className={`text-[10px] flex items-center gap-1 ${light ? 'text-cyan-600' : 'text-cyan-400/70'}`}>
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                Online
              </div>
            </div>
            {messages.length > 0 && (
              <button
                onClick={clearChat}
                className="text-[var(--text-muted)] hover:text-red-400 transition-colors text-xs px-2 py-1 rounded-lg hover:bg-red-500/10"
                title="Clear chat"
              >
                🗑️
              </button>
            )}
          </div>

          {/* Messages */}
          <div ref={scrollRef} className="flex-1 overflow-y-auto px-4 py-3 space-y-3 scrollbar-premium">
            {messages.length === 0 && (
              <div className={`text-center text-xs mt-8 ${light ? 'text-slate-500' : 'text-gray-500'}`}>
                <p className="mb-4">Ask me anything about the market</p>
                <div className="flex flex-wrap gap-2 justify-center">
                  {QUICK_PROMPTS.map((p) => (
                    <button
                      key={p}
                      onClick={() => handleSend(p)}
                      className="px-3 py-1.5 rounded-full text-[11px] font-medium transition-all duration-200 hover:scale-105"
                      style={{
                        background: light ? 'rgba(6,182,212,0.08)' : 'rgba(0,240,255,0.1)',
                        border: light ? '1px solid rgba(6,182,212,0.2)' : '1px solid rgba(0,240,255,0.25)',
                        color: light ? '#0891b2' : '#00f0ff',
                      }}
                    >
                      {p}
                    </button>
                  ))}
                </div>
              </div>
            )}
            {messages.map((m, i) => (
              <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div
                  className={`max-w-[80%] px-3 py-2 rounded-xl text-sm leading-relaxed ${
                    m.role === 'user' ? 'text-white' : ''
                  }`}
                  style={
                    m.role === 'user'
                      ? { background: 'linear-gradient(135deg, #00f0ff 0%, #8b5cf6 100%)' }
                      : {
                          background: light ? 'rgba(0,0,0,0.04)' : 'rgba(255,255,255,0.05)',
                          border: light ? '1px solid rgba(0,0,0,0.06)' : '1px solid rgba(255,255,255,0.08)',
                          color: light ? '#0f172a' : '#e2e8f0',
                        }
                  }
                  dangerouslySetInnerHTML={{ __html: renderMarkdown(m.content) }}
                />
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div
                  className="px-3 py-2 rounded-xl text-sm flex items-center gap-1"
                  style={{
                    background: light ? 'rgba(0,0,0,0.04)' : 'rgba(255,255,255,0.05)',
                    color: light ? '#64748b' : '#9ca3af',
                  }}
                >
                  <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-bounce" />
                  <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-bounce [animation-delay:0.1s]" />
                  <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-bounce [animation-delay:0.2s]" />
                </div>
              </div>
            )}
          </div>

          {/* Input */}
          <div
            className="px-3 py-3"
            style={{
              borderTop: light ? '1px solid rgba(0,0,0,0.06)' : '1px solid rgba(0,240,255,0.15)',
              background: light ? 'rgba(255,255,255,0.5)' : 'rgba(0,0,0,0.3)',
            }}
          >
            <form
              onSubmit={(e) => { e.preventDefault(); handleSend(); }}
              className="flex gap-2"
            >
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask about AAPL, BTC, sentiment..."
                className={`flex-1 rounded-xl px-3 py-2 text-sm focus:outline-none transition-colors ${
                  light
                    ? 'bg-white border border-slate-200 text-slate-800 placeholder-slate-400 focus:border-cyan-400'
                    : 'bg-white/5 border border-white/10 text-white placeholder-gray-500 focus:border-cyan-400/50'
                }`}
              />
              <button
                type="submit"
                disabled={loading}
                className="w-9 h-9 rounded-xl flex items-center justify-center transition-all duration-200 hover:scale-105 disabled:opacity-50"
                style={{ background: 'linear-gradient(135deg, #00f0ff 0%, #8b5cf6 100%)' }}
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              </button>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
