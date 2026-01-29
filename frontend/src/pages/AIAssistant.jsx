import React, { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { ai, reports } from '../api/client'
import '../App.css'

export default function AIAssistant() {
  const navigate = useNavigate()
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')
  const [loading, setLoading] = useState(false)
  const [aiHealth, setAiHealth] = useState(null)
  const [financialContext, setFinancialContext] = useState(null)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    checkAIHealth()
    loadFinancialContext()

    // Mensagem de boas-vindas
    setMessages([{
      role: 'assistant',
      content: 'Olá! Sou seu assistente financeiro inteligente. Como posso ajudá-lo a melhorar suas finanças hoje?',
      timestamp: new Date()
    }])
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const checkAIHealth = async () => {
    try {
      const response = await ai.health()
      setAiHealth(response.data)
    } catch (err) {
      console.error('Erro ao verificar status da IA:', err)
      setAiHealth({ configured: false, healthy: false })
    }
  }

  const loadFinancialContext = async () => {
    try {
      const response = await reports.summary()
      setFinancialContext(response.data)
    } catch (err) {
      console.error('Erro ao carregar contexto financeiro:', err)
    }
  }

  const sendMessage = async (message = inputMessage) => {
    if (!message.trim() || loading) return

    // Adicionar mensagem do usuário
    const userMessage = {
      role: 'user',
      content: message,
      timestamp: new Date()
    }
    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setLoading(true)

    try {
      // Preparar contexto financeiro
      const context = financialContext ? {
        current_balance: financialContext.balance || 0,
        monthly_income: financialContext.total_income || 0,
        monthly_expense: financialContext.total_expense || 0,
        categories: financialContext.categories || []
      } : {}

      // Enviar para IA
      const response = await ai.chat(message, context)

      // Adicionar resposta da IA
      const aiMessage = {
        role: 'assistant',
        content: response.data.response,
        timestamp: new Date()
      }
      setMessages(prev => [...prev, aiMessage])
    } catch (err) {
      const errorMessage = {
        role: 'assistant',
        content: `❌ Erro: ${err.response?.data?.error || 'Não foi possível processar sua mensagem'}`,
        timestamp: new Date(),
        isError: true
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const quickActions = [
    {
      label: '📊 Analise meus gastos do mês',
      action: async () => {
        if (!financialContext) {
          alert('Carregando dados financeiros...')
          return
        }

        const userMsg = 'Analise meus gastos do mês'
        setMessages(prev => [...prev, { role: 'user', content: userMsg, timestamp: new Date() }])
        setLoading(true)

        try {
          const summary = {
            total_income: financialContext.total_income || 0,
            total_expense: financialContext.total_expense || 0,
            balance: financialContext.balance || 0,
            top_categories: financialContext.categories?.slice(0, 5).map(c => ({
              name: c.name,
              total: c.total
            })) || []
          }

          const response = await ai.analyze(summary, 'last_month')
          setMessages(prev => [...prev, {
            role: 'assistant',
            content: response.data.analysis,
            timestamp: new Date()
          }])
        } catch (err) {
          setMessages(prev => [...prev, {
            role: 'assistant',
            content: `❌ Erro: ${err.response?.data?.error || 'Não foi possível analisar'}`,
            timestamp: new Date(),
            isError: true
          }])
        } finally {
          setLoading(false)
        }
      }
    },
    {
      label: '💰 Como economizar mais?',
      action: () => sendMessage('Como posso economizar mais dinheiro com base nos meus gastos atuais?')
    },
    {
      label: '🎯 Criar meta de economia',
      action: () => sendMessage('Me ajude a criar uma meta de economia realista baseada na minha situação financeira atual')
    },
    {
      label: '💡 Insights sobre categorização',
      action: async () => {
        const userMsg = 'Me dê insights sobre meus padrões de categorização'
        setMessages(prev => [...prev, { role: 'user', content: userMsg, timestamp: new Date() }])
        setLoading(true)

        try {
          const response = await ai.insights()
          setMessages(prev => [...prev, {
            role: 'assistant',
            content: response.data.insights || 'Não há dados suficientes para gerar insights',
            timestamp: new Date()
          }])
        } catch (err) {
          setMessages(prev => [...prev, {
            role: 'assistant',
            content: `❌ Erro: ${err.response?.data?.error || 'Não foi possível gerar insights'}`,
            timestamp: new Date(),
            isError: true
          }])
        } finally {
          setLoading(false)
        }
      }
    }
  ]

  const clearChat = () => {
    if (confirm('Limpar toda a conversa?')) {
      setMessages([{
        role: 'assistant',
        content: 'Conversa limpa. Como posso ajudá-lo?',
        timestamp: new Date()
      }])
    }
  }

  if (aiHealth && !aiHealth.configured) {
    return (
      <div className="container">
        <div className="header" style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          <button
            onClick={() => navigate('/')}
            className="button"
            style={{
              padding: '8px 16px',
              backgroundColor: '#666',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}
          >
            ← Voltar
          </button>
          <div>
            <h1>🤖 Assistente Financeiro IA</h1>
          </div>
        </div>
        <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
          <p style={{ fontSize: '64px', margin: '0' }}>⚠️</p>
          <h2 style={{ marginTop: '20px' }}>API OpenAI não configurada</h2>
          <p style={{ color: '#666', marginTop: '10px' }}>
            Configure a chave da API OpenAI no arquivo <code>.env</code>:
          </p>
          <pre style={{ backgroundColor: '#f5f5f5', padding: '12px', borderRadius: '4px', marginTop: '20px' }}>
            OPENAI_API_KEY=sua_chave_aqui
          </pre>
        </div>
      </div>
    )
  }

  return (
    <div className="container">
      <div className="header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          <button
            onClick={() => navigate('/')}
            className="button"
            style={{
              padding: '8px 16px',
              backgroundColor: '#666',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}
          >
            ← Voltar
          </button>
          <div>
            <h1>🤖 Assistente Financeiro IA</h1>
            <p>Consultoria personalizada com ChatGPT</p>
          </div>
        </div>
        <button onClick={clearChat} className="button" style={{ padding: '8px 16px' }}>
          🗑️ Limpar Chat
        </button>
      </div>

      {/* Quick Actions */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', marginBottom: '20px' }}>
        {quickActions.map((action, idx) => (
          <button
            key={idx}
            onClick={action.action}
            disabled={loading}
            style={{
              padding: '10px 16px',
              border: '1px solid #ddd',
              borderRadius: '20px',
              backgroundColor: 'white',
              cursor: 'pointer',
              fontSize: '14px',
              transition: 'all 0.2s'
            }}
            onMouseEnter={(e) => {
              e.target.style.backgroundColor = '#f5f5f5'
              e.target.style.borderColor = '#4CAF50'
            }}
            onMouseLeave={(e) => {
              e.target.style.backgroundColor = 'white'
              e.target.style.borderColor = '#ddd'
            }}
          >
            {action.label}
          </button>
        ))}
      </div>

      {/* Chat Messages */}
      <div className="card" style={{
        minHeight: '500px',
        maxHeight: '500px',
        overflowY: 'auto',
        padding: '20px',
        backgroundColor: '#fafafa',
        marginBottom: '20px'
      }}>
        {messages.map((msg, idx) => (
          <div
            key={idx}
            style={{
              display: 'flex',
              justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
              marginBottom: '16px'
            }}
          >
            <div style={{
              maxWidth: '70%',
              padding: '12px 16px',
              borderRadius: '12px',
              backgroundColor: msg.role === 'user' ? '#4CAF50' : msg.isError ? '#f44336' : 'white',
              color: msg.role === 'user' || msg.isError ? 'white' : '#333',
              boxShadow: '0 1px 2px rgba(0,0,0,0.1)',
              wordWrap: 'break-word'
            }}>
              <div style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</div>
              <div style={{
                fontSize: '11px',
                marginTop: '6px',
                opacity: 0.7,
                textAlign: 'right'
              }}>
                {msg.timestamp.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}
              </div>
            </div>
          </div>
        ))}

        {loading && (
          <div style={{ display: 'flex', justifyContent: 'flex-start', marginBottom: '16px' }}>
            <div style={{
              padding: '12px 16px',
              borderRadius: '12px',
              backgroundColor: 'white',
              boxShadow: '0 1px 2px rgba(0,0,0,0.1)'
            }}>
              <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
                <div className="typing-dot" style={{ animation: 'typing 1.4s infinite' }}></div>
                <div className="typing-dot" style={{ animation: 'typing 1.4s infinite 0.2s' }}></div>
                <div className="typing-dot" style={{ animation: 'typing 1.4s infinite 0.4s' }}></div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div style={{ display: 'flex', gap: '10px', alignItems: 'flex-end' }}>
        <textarea
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Digite sua pergunta sobre finanças... (Enter para enviar, Shift+Enter para nova linha)"
          disabled={loading}
          style={{
            flex: 1,
            padding: '12px',
            border: '1px solid #ddd',
            borderRadius: '8px',
            fontSize: '14px',
            resize: 'none',
            minHeight: '50px',
            maxHeight: '120px',
            fontFamily: 'inherit'
          }}
        />
        <button
          onClick={() => sendMessage()}
          disabled={loading || !inputMessage.trim()}
          className="button"
          style={{
            padding: '12px 24px',
            minWidth: '100px',
            height: '50px'
          }}
        >
          {loading ? '⏳' : '📤 Enviar'}
        </button>
      </div>

      {/* Typing animation styles */}
      <style>{`
        @keyframes typing {
          0%, 60%, 100% {
            opacity: 0.3;
            transform: translateY(0);
          }
          30% {
            opacity: 1;
            transform: translateY(-8px);
          }
        }
        .typing-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background-color: #999;
        }
      `}</style>
    </div>
  )
}
