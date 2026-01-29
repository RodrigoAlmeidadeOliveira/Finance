import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { imports, catalog } from '../api/client'
import { format } from 'date-fns'

export default function BatchDetails() {
  const { batchId } = useParams()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [batch, setBatch] = useState(null)
  const [transactions, setTransactions] = useState([])
  const [categories, setCategories] = useState([])
  const [selectedCategories, setSelectedCategories] = useState({})
  const [error, setError] = useState('')
  const [filterStatus, setFilterStatus] = useState('all') // all, pending, approved, rejected
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    loadBatchDetails()
  }, [batchId])

  const loadBatchDetails = async () => {
    try {
      setLoading(true)
      const [batchRes, transactionsRes, categoriesRes] = await Promise.all([
        imports.getBatch(batchId),
        imports.getTransactions(batchId),
        catalog.listCategories()
      ])
      setBatch(batchRes.data)
      const loadedTransactions = transactionsRes.data.transactions || []
      setTransactions(loadedTransactions)
      setCategories(categoriesRes.data.items || [])

      // Initialize selected categories with predicted or user categories
      const initialCategories = {}
      loadedTransactions.forEach(t => {
        initialCategories[t.id] = t.user_category || t.predicted_category
      })
      setSelectedCategories(initialCategories)
    } catch (err) {
      setError(err.response?.data?.error || 'Erro ao carregar detalhes do lote.')
    } finally {
      setLoading(false)
    }
  }

  const handleCategoryChange = (transactionId, category) => {
    setSelectedCategories(prev => ({
      ...prev,
      [transactionId]: category
    }))
  }

  const handleReviewTransaction = async (transactionId, status) => {
    const category = selectedCategories[transactionId]
    if (!category) {
      alert('Selecione uma categoria antes de aprovar/rejeitar')
      return
    }

    try {
      await imports.reviewTransaction(batchId, transactionId, category, status, null)
      // Recarrega as transações
      const res = await imports.getTransactions(batchId)
      const loadedTransactions = res.data.transactions || []
      setTransactions(loadedTransactions)

      // Update selected categories
      const updatedCategories = {}
      loadedTransactions.forEach(t => {
        updatedCategories[t.id] = t.user_category || t.predicted_category
      })
      setSelectedCategories(updatedCategories)
    } catch (err) {
      console.error('Erro ao revisar transação:', err)
      alert('Erro ao revisar transação')
    }
  }

  const handleDeleteTransaction = async (transactionId) => {
    if (!confirm('Tem certeza que deseja excluir esta transação?')) {
      return
    }

    try {
      await imports.deleteTransaction(batchId, transactionId)
      setTransactions(transactions.filter(t => t.id !== transactionId))
    } catch (err) {
      alert(err.response?.data?.error || 'Erro ao excluir transação')
    }
  }

  const filteredTransactions = transactions.filter(t => {
    const matchesStatus = filterStatus === 'all' || t.review_status === filterStatus
    const matchesSearch = !searchTerm ||
      t.description.toLowerCase().includes(searchTerm.toLowerCase())
    return matchesStatus && matchesSearch
  })

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value)
  }

  const getStatusBadge = (status) => {
    const colors = {
      pending: 'bg-yellow-100 text-yellow-800',
      approved: 'bg-green-100 text-green-800',
      rejected: 'bg-red-100 text-red-800'
    }
    const labels = {
      pending: 'Pendente',
      approved: 'Aprovado',
      rejected: 'Rejeitado'
    }
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${colors[status] || 'bg-gray-100 text-gray-800'}`}>
        {labels[status] || status}
      </span>
    )
  }

  const getConfidenceClass = (level) => {
    if (level === 'high') return 'bg-green-100 text-green-800'
    if (level === 'medium') return 'bg-yellow-100 text-yellow-800'
    return 'bg-red-100 text-red-800'
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">Carregando detalhes do lote...</p>
        </div>
      </div>
    )
  }

  if (error || !batch) {
    return (
      <div className="min-h-screen bg-gray-50">
        <header className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-800">Detalhes do Lote</h1>
            <button
              onClick={() => navigate('/manage-imports')}
              className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition"
            >
              ← Voltar
            </button>
          </div>
        </header>
        <main className="max-w-7xl mx-auto px-4 py-8">
          <div className="bg-red-100 text-red-800 px-4 py-3 rounded border border-red-200">
            {error}
          </div>
        </main>
      </div>
    )
  }

  const stats = {
    total: transactions.length,
    pending: transactions.filter(t => t.review_status === 'pending').length,
    approved: transactions.filter(t => t.review_status === 'approved').length,
    rejected: transactions.filter(t => t.review_status === 'rejected').length
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <span className="text-3xl">📂</span>
            <div>
              <h1 className="text-xl font-bold text-gray-800">Lote #{batch.id}: {batch.filename}</h1>
              <p className="text-xs text-gray-500">
                {batch.institution_name} · {batch.account_id}
              </p>
            </div>
          </div>
          <button
            onClick={() => navigate('/manage-imports')}
            className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition shadow-sm"
          >
            ← Voltar
          </button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6 space-y-6">
        {/* Informações do Lote */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-4">Informações do Lote</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-xs text-gray-500 mb-1">Período</p>
              <p className="text-sm font-medium text-gray-900">
                {batch.period_start && batch.period_end ? (
                  <>
                    {format(new Date(batch.period_start), 'dd/MM/yyyy')} -{' '}
                    {format(new Date(batch.period_end), 'dd/MM/yyyy')}
                  </>
                ) : '—'}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500 mb-1">Saldo</p>
              <p className="text-sm font-medium text-gray-900">{formatCurrency(batch.balance || 0)}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500 mb-1">Transações</p>
              <p className="text-sm font-medium text-gray-900">
                {batch.processed_transactions || 0} / {batch.total_transactions || 0}
              </p>
            </div>
            <div>
              <p className="text-xs text-gray-500 mb-1">Importado em</p>
              <p className="text-sm font-medium text-gray-900">
                {format(new Date(batch.created_at), 'dd/MM/yyyy HH:mm')}
              </p>
            </div>
          </div>
        </div>

        {/* Estatísticas */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg shadow-md p-4 border-l-4 border-blue-500">
            <p className="text-xs text-gray-500 mb-1">Total</p>
            <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
          </div>
          <div className="bg-white rounded-lg shadow-md p-4 border-l-4 border-yellow-500">
            <p className="text-xs text-gray-500 mb-1">Pendentes</p>
            <p className="text-2xl font-bold text-yellow-600">{stats.pending}</p>
          </div>
          <div className="bg-white rounded-lg shadow-md p-4 border-l-4 border-green-500">
            <p className="text-xs text-gray-500 mb-1">Aprovados</p>
            <p className="text-2xl font-bold text-green-600">{stats.approved}</p>
          </div>
          <div className="bg-white rounded-lg shadow-md p-4 border-l-4 border-red-500">
            <p className="text-xs text-gray-500 mb-1">Rejeitados</p>
            <p className="text-2xl font-bold text-red-600">{stats.rejected}</p>
          </div>
        </div>

        {/* Filtros */}
        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="flex flex-wrap gap-4 items-center">
            <div className="flex gap-2">
              <button
                onClick={() => setFilterStatus('all')}
                className={`px-3 py-1 rounded-lg text-sm font-medium transition ${
                  filterStatus === 'all'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Todas
              </button>
              <button
                onClick={() => setFilterStatus('pending')}
                className={`px-3 py-1 rounded-lg text-sm font-medium transition ${
                  filterStatus === 'pending'
                    ? 'bg-yellow-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Pendentes
              </button>
              <button
                onClick={() => setFilterStatus('approved')}
                className={`px-3 py-1 rounded-lg text-sm font-medium transition ${
                  filterStatus === 'approved'
                    ? 'bg-green-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Aprovados
              </button>
              <button
                onClick={() => setFilterStatus('rejected')}
                className={`px-3 py-1 rounded-lg text-sm font-medium transition ${
                  filterStatus === 'rejected'
                    ? 'bg-red-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Rejeitados
              </button>
            </div>
            <div className="flex-1 min-w-[200px]">
              <input
                type="text"
                placeholder="Buscar por descrição..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full px-3 py-1 border rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>

        {/* Lista de Transações */}
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <div className="p-4 border-b bg-gray-50">
            <h2 className="text-lg font-semibold text-gray-800">
              Transações ({filteredTransactions.length})
            </h2>
          </div>

          {filteredTransactions.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              Nenhuma transação encontrada com os filtros aplicados.
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {filteredTransactions.map((tx) => (
                <div key={tx.id} className="p-4 hover:bg-gray-50 transition">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h3 className="font-medium text-gray-900">{tx.description}</h3>
                        {getStatusBadge(tx.review_status)}
                      </div>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                        <div>
                          <p className="text-xs text-gray-500">Data</p>
                          <p className="text-gray-900">{format(new Date(tx.date), 'dd/MM/yyyy')}</p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500">Valor</p>
                          <p className={`font-medium ${tx.amount < 0 ? 'text-red-600' : 'text-green-600'}`}>
                            {formatCurrency(tx.amount)}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500">Categoria ML</p>
                          <div className="flex items-center gap-1">
                            <p className="text-gray-900">{tx.predicted_category || '—'}</p>
                            {tx.confidence_level && (
                              <span className={`px-1 py-0.5 rounded text-xs ${getConfidenceClass(tx.confidence_level)}`}>
                                {tx.confidence_score ? `${(tx.confidence_score * 100).toFixed(0)}%` : '—'}
                              </span>
                            )}
                          </div>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500">Selecionar Categoria</p>
                          {tx.review_status === 'pending' ? (
                            <select
                              value={selectedCategories[tx.id] || tx.predicted_category}
                              onChange={(e) => handleCategoryChange(tx.id, e.target.value)}
                              className="w-full px-2 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                            >
                              {categories
                                .sort((a, b) => a.name.localeCompare(b.name))
                                .map(cat => (
                                  <option key={cat.id} value={cat.name}>{cat.name}</option>
                                ))}
                            </select>
                          ) : (
                            <p className="text-gray-900">{tx.user_category || tx.predicted_category || '—'}</p>
                          )}
                        </div>
                      </div>
                    </div>

                    <div className="flex flex-col gap-2">
                      {tx.review_status === 'pending' && (
                        <>
                          <button
                            onClick={() => handleReviewTransaction(tx.id, 'approved')}
                            className="px-3 py-1 bg-green-600 text-white text-sm rounded hover:bg-green-700 transition"
                          >
                            ✓ Aprovar
                          </button>
                          <button
                            onClick={() => handleReviewTransaction(tx.id, 'rejected')}
                            className="px-3 py-1 bg-red-600 text-white text-sm rounded hover:bg-red-700 transition"
                          >
                            ✕ Rejeitar
                          </button>
                        </>
                      )}
                      <button
                        onClick={() => handleDeleteTransaction(tx.id)}
                        className="px-3 py-1 bg-gray-600 text-white text-sm rounded hover:bg-gray-700 transition"
                      >
                        Excluir
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
