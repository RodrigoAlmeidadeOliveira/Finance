import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { transactions, catalog } from '../api/client'
import { format } from 'date-fns'
import TransactionForm from '../components/TransactionForm'

const currency = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' })

export default function CashFlow() {
  const [transactionsList, setTransactionsList] = useState([])
  const [categories, setCategories] = useState([])
  const [institutions, setInstitutions] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editingTransaction, setEditingTransaction] = useState(null)
  const [summary, setSummary] = useState(null)

  // Filters
  const [filters, setFilters] = useState({
    start_date: new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString().split('T')[0],
    end_date: new Date().toISOString().split('T')[0],
    transaction_type: '',
    category_id: '',
    institution_id: '',
    status: '',
    search: ''
  })

  const navigate = useNavigate()

  useEffect(() => {
    loadData()
  }, [filters])

  const loadData = async () => {
    try {
      setLoading(true)

      // Load catalogs (only once)
      if (categories.length === 0) {
        const [catResp, instResp] = await Promise.all([
          catalog.listCategories(),
          catalog.listInstitutions()
        ])
        setCategories(catResp.data.items || [])
        setInstitutions(instResp.data.items || [])
      }

      // Build query params
      const params = {}
      if (filters.start_date) params.start_date = `${filters.start_date}T00:00:00`
      if (filters.end_date) params.end_date = `${filters.end_date}T23:59:59`
      if (filters.transaction_type) params.transaction_type = filters.transaction_type
      if (filters.category_id) params.category_id = filters.category_id
      if (filters.institution_id) params.institution_id = filters.institution_id
      if (filters.status) params.status = filters.status
      if (filters.search) params.search = filters.search
      params.limit = 500

      // Load transactions
      const txResp = await transactions.list(params)
      setTransactionsList(txResp.data.items || [])

      // Load summary
      if (filters.start_date && filters.end_date) {
        const summaryResp = await transactions.summary(
          `${filters.start_date}T00:00:00`,
          `${filters.end_date}T23:59:59`,
          true // include pending
        )
        setSummary(summaryResp.data)
      }
    } catch (error) {
      console.error('Erro ao carregar dados:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleFilterChange = (name, value) => {
    setFilters(prev => ({ ...prev, [name]: value }))
  }

  const handleDelete = async (id) => {
    if (!confirm('Deseja realmente excluir esta transação?')) return

    try {
      await transactions.delete(id, false) // soft delete
      loadData()
    } catch (error) {
      console.error('Erro ao deletar:', error)
      alert('Erro ao deletar transação')
    }
  }

  const handleToggleStatus = async (transaction) => {
    try {
      if (transaction.status === 'completed') {
        await transactions.markPending(transaction.id)
      } else {
        await transactions.markCompleted(transaction.id)
      }
      loadData()
    } catch (error) {
      console.error('Erro ao alterar status:', error)
      alert('Erro ao alterar status')
    }
  }

  const handleDuplicate = async (transaction) => {
    try {
      // Duplicate for next month
      const nextMonth = new Date(transaction.event_date)
      nextMonth.setMonth(nextMonth.getMonth() + 1)

      await transactions.duplicate(
        transaction.id,
        nextMonth.toISOString(),
        true
      )

      loadData()
      alert('Transação duplicada com sucesso!')
    } catch (error) {
      console.error('Erro ao duplicar:', error)
      alert('Erro ao duplicar transação')
    }
  }

  const getStatusBadge = (status) => {
    const badges = {
      pending: 'bg-yellow-100 text-yellow-800',
      completed: 'bg-green-100 text-green-800',
      cancelled: 'bg-red-100 text-red-800'
    }
    const labels = {
      pending: 'Pendente',
      completed: 'Concluída',
      cancelled: 'Cancelada'
    }
    return (
      <span className={`px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${badges[status] || 'bg-gray-100 text-gray-800'}`}>
        {labels[status] || status}
      </span>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-800">💰 Fluxo de Caixa</h1>
          <div className="flex gap-3">
            <button
              onClick={() => setShowForm(true)}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition shadow-sm"
            >
              ➕ Nova Transação
            </button>
            <button
              onClick={() => navigate('/')}
              className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition shadow-sm"
            >
              ← Voltar
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Summary Cards */}
        {summary && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-green-500">
              <p className="text-sm text-gray-600 mb-1">Receitas</p>
              <p className="text-2xl font-bold text-green-600">{currency.format(summary.income)}</p>
              <p className="text-xs text-gray-500 mt-1">{summary.income_count} transações</p>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-red-500">
              <p className="text-sm text-gray-600 mb-1">Despesas</p>
              <p className="text-2xl font-bold text-red-600">{currency.format(summary.expense)}</p>
              <p className="text-xs text-gray-500 mt-1">{summary.expense_count} transações</p>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-purple-500">
              <p className="text-sm text-gray-600 mb-1">Saldo</p>
              <p className={`text-2xl font-bold ${summary.balance >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {currency.format(summary.balance)}
              </p>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-blue-500">
              <p className="text-sm text-gray-600 mb-1">Total Transações</p>
              <p className="text-3xl font-bold text-blue-600">{summary.transaction_count}</p>
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-lg font-bold mb-4 text-gray-800">🔍 Filtros</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Data Início</label>
              <input
                type="date"
                value={filters.start_date}
                onChange={(e) => handleFilterChange('start_date', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Data Fim</label>
              <input
                type="date"
                value={filters.end_date}
                onChange={(e) => handleFilterChange('end_date', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Tipo</label>
              <select
                value={filters.transaction_type}
                onChange={(e) => handleFilterChange('transaction_type', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Todos</option>
                <option value="INCOME">Receitas</option>
                <option value="EXPENSE">Despesas</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
              <select
                value={filters.status}
                onChange={(e) => handleFilterChange('status', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Todos</option>
                <option value="PENDING">Pendentes</option>
                <option value="COMPLETED">Concluídas</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Categoria</label>
              <select
                value={filters.category_id}
                onChange={(e) => handleFilterChange('category_id', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Todas</option>
                {categories.map(cat => (
                  <option key={cat.id} value={cat.id}>{cat.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Instituição</label>
              <select
                value={filters.institution_id}
                onChange={(e) => handleFilterChange('institution_id', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Todas</option>
                {institutions.map(inst => (
                  <option key={inst.id} value={inst.id}>{inst.name}</option>
                ))}
              </select>
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">Buscar</label>
              <input
                type="text"
                placeholder="Descrição..."
                value={filters.search}
                onChange={(e) => handleFilterChange('search', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>

        {/* Transactions Table */}
        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <p className="mt-4 text-gray-600">Carregando transações...</p>
          </div>
        ) : transactionsList.length > 0 ? (
          <div className="bg-white rounded-lg shadow-md overflow-hidden">
            <div className="px-6 py-4 border-b bg-gray-50">
              <h2 className="text-xl font-bold text-gray-800">
                📋 {transactionsList.length} Transações
              </h2>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Data</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Tipo</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Descrição</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Categoria</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Valor</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Ações</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {transactionsList.map((tx) => (
                    <tr key={tx.id} className="hover:bg-gray-50 transition">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {format(new Date(tx.event_date), 'dd/MM/yyyy')}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <span className={`px-2 py-1 rounded ${tx.transaction_type === 'income' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                          {tx.transaction_type === 'income' ? '💰 Receita' : '💸 Despesa'}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900">
                        <div className="max-w-md" title={tx.description}>
                          {tx.description}
                        </div>
                        {tx.notes && (
                          <p className="text-xs text-gray-500 mt-1">{tx.notes}</p>
                        )}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900">
                        {tx.category?.name}
                      </td>
                      <td className={`px-6 py-4 text-sm font-semibold whitespace-nowrap ${tx.transaction_type === 'income' ? 'text-green-600' : 'text-red-600'}`}>
                        {currency.format(tx.amount)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {getStatusBadge(tx.status)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <div className="flex gap-2">
                          <button
                            onClick={() => {
                              setEditingTransaction(tx)
                              setShowForm(true)
                            }}
                            className="text-blue-600 hover:text-blue-800"
                            title="Editar"
                          >
                            ✏️
                          </button>
                          <button
                            onClick={() => handleToggleStatus(tx)}
                            className="text-green-600 hover:text-green-800"
                            title={tx.status === 'completed' ? 'Marcar como pendente' : 'Marcar como concluída'}
                          >
                            {tx.status === 'completed' ? '⏳' : '✅'}
                          </button>
                          <button
                            onClick={() => handleDuplicate(tx)}
                            className="text-purple-600 hover:text-purple-800"
                            title="Duplicar"
                          >
                            📋
                          </button>
                          <button
                            onClick={() => handleDelete(tx.id)}
                            className="text-red-600 hover:text-red-800"
                            title="Excluir"
                          >
                            🗑️
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow-md p-12 text-center">
            <div className="text-6xl mb-4">📭</div>
            <h3 className="text-xl font-bold text-gray-800 mb-2">Nenhuma transação encontrada</h3>
            <p className="text-gray-600 mb-4">Comece adicionando sua primeira transação</p>
            <button
              onClick={() => setShowForm(true)}
              className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition"
            >
              ➕ Nova Transação
            </button>
          </div>
        )}
      </main>

      {/* Transaction Form Modal */}
      {showForm && (
        <TransactionForm
          transaction={editingTransaction}
          onClose={() => {
            setShowForm(false)
            setEditingTransaction(null)
          }}
          onSaved={() => {
            loadData()
            setEditingTransaction(null)
          }}
        />
      )}
    </div>
  )
}
