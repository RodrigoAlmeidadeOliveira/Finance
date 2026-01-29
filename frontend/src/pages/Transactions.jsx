import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { imports, catalog } from '../api/client'
import { format } from 'date-fns'

const currency = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' })

export default function Transactions() {
  const [transactions, setTransactions] = useState([])
  const [batches, setBatches] = useState([])
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedBatch, setSelectedBatch] = useState('all')
  const [searchTerm, setSearchTerm] = useState('')
  const [categoryFilter, setCategoryFilter] = useState('all')
  const [typeFilter, setTypeFilter] = useState('all')
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [batchesResponse, categoriesResponse] = await Promise.all([
        imports.listBatches(),
        catalog.listCategories()
      ])

      const loadedBatches = batchesResponse.data.batches || []
      setBatches(loadedBatches)

      const loadedCategories = categoriesResponse.data.items || []
      setCategories(loadedCategories)

      const allTransactions = []
      for (const batch of loadedBatches) {
        try {
          const transResponse = await imports.getTransactions(batch.id)
          const batchTransactions = (transResponse.data.transactions || []).map(t => ({
            ...t,
            batchFilename: batch.filename,
            batchId: batch.id
          }))
          allTransactions.push(...batchTransactions)
        } catch (err) {
          console.error('Erro ao carregar transações do lote', batch.id, err)
        }
      }

      setTransactions(allTransactions)
    } catch (error) {
      console.error('Erro ao carregar dados:', error)
    } finally {
      setLoading(false)
    }
  }

  const filteredTransactions = transactions.filter(t => {
    const matchesBatch = selectedBatch === 'all' || t.batchId === parseInt(selectedBatch)
    const matchesSearch = !searchTerm || t.description.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesCategory = categoryFilter === 'all' || t.predicted_category === categoryFilter || t.user_category === categoryFilter
    const matchesType = typeFilter === 'all' || 
      (typeFilter === 'debit' && t.amount < 0) ||
      (typeFilter === 'credit' && t.amount > 0)
    const txDate = t.date ? new Date(t.date) : null
    const matchesStart = !startDate || (txDate && txDate >= new Date(`${startDate}T00:00:00`))
    const matchesEnd = !endDate || (txDate && txDate <= new Date(`${endDate}T23:59:59`))
    
    return matchesBatch && matchesSearch && matchesCategory && matchesType && matchesStart && matchesEnd
  })

  const totals = filteredTransactions.reduce((acc, t) => {
    if (t.amount < 0) {
      acc.debits += Math.abs(t.amount)
      acc.debitsCount++
    } else {
      acc.credits += t.amount
      acc.creditsCount++
    }
    return acc
  }, { debits: 0, credits: 0, debitsCount: 0, creditsCount: 0 })

  const getStatusBadge = (status) => {
    const badges = {
      pending: 'bg-yellow-100 text-yellow-800',
      approved: 'bg-green-100 text-green-800',
      rejected: 'bg-red-100 text-red-800'
    }
    return badges[status] || 'bg-gray-100 text-gray-800'
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-800">💳 Transações</h1>
          <button
            onClick={() => navigate('/')}
            className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition shadow-sm"
          >
            ← Voltar
          </button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-blue-500">
            <p className="text-sm text-gray-600 mb-1">Total de Transações</p>
            <p className="text-3xl font-bold text-blue-600">{filteredTransactions.length}</p>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-red-500">
            <p className="text-sm text-gray-600 mb-1">Débitos</p>
            <p className="text-2xl font-bold text-red-600">{currency.format(totals.debits)}</p>
            <p className="text-xs text-gray-500 mt-1">{totals.debitsCount} transações</p>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-green-500">
            <p className="text-sm text-gray-600 mb-1">Créditos</p>
            <p className="text-2xl font-bold text-green-600">{currency.format(totals.credits)}</p>
            <p className="text-xs text-gray-500 mt-1">{totals.creditsCount} transações</p>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-purple-500">
            <p className="text-sm text-gray-600 mb-1">Saldo</p>
            <p className={'text-2xl font-bold ' + (totals.credits - totals.debits >= 0 ? 'text-green-600' : 'text-red-600')}>
              {currency.format(totals.credits - totals.debits)}
            </p>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-lg font-bold mb-4 text-gray-800">🔍 Filtros</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Lote</label>
              <select
                value={selectedBatch}
                onChange={(e) => setSelectedBatch(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">Todos os lotes</option>
                {batches.map(batch => (
                  <option key={batch.id} value={batch.id}>{batch.filename}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Buscar</label>
              <input
                type="text"
                placeholder="Descrição da transação..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Categoria</label>
              <select
                value={categoryFilter}
                onChange={(e) => setCategoryFilter(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">Todas as categorias</option>
                {categories
                  .sort((a, b) => a.name.localeCompare(b.name))
                  .map(cat => (
                    <option key={cat.id} value={cat.name}>{cat.name}</option>
                  ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Tipo</label>
              <select
                value={typeFilter}
                onChange={(e) => setTypeFilter(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="all">Todos</option>
                <option value="debit">Apenas Débitos</option>
                <option value="credit">Apenas Créditos</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Data início</label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Data fim</label>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <p className="mt-4 text-gray-600">Carregando transações...</p>
          </div>
        ) : filteredTransactions.length > 0 ? (
          <div className="bg-white rounded-lg shadow-md overflow-hidden">
            <div className="px-6 py-4 border-b bg-gray-50">
              <h2 className="text-xl font-bold text-gray-800">
                📋 {filteredTransactions.length} Transações
              </h2>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Data</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Descrição</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Categoria</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Valor</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Lote</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {filteredTransactions.map((transaction, idx) => (
                    <tr key={idx} className="hover:bg-gray-50 transition">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {format(new Date(transaction.date), 'dd/MM/yyyy')}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900">
                        <div className="max-w-md" title={transaction.description}>
                          {transaction.description}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900">
                        <span className="font-medium">
                          {transaction.user_category || transaction.predicted_category}
                        </span>
                      </td>
                    <td className={'px-6 py-4 text-sm font-semibold whitespace-nowrap ' + (transaction.amount < 0 ? 'text-red-600' : 'text-green-600')}>
                        {transaction.amount < 0 ? '-' : '+'} {currency.format(Math.abs(transaction.amount))}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600">
                        {transaction.batchFilename}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={'px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ' + getStatusBadge(transaction.review_status)}>
                          {transaction.review_status || 'pending'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow-md p-12 text-center">
            <div className="text-6xl mb-4">🔍</div>
            <h3 className="text-xl font-bold text-gray-800 mb-2">Nenhuma transação encontrada</h3>
            <p className="text-gray-600">Tente ajustar os filtros ou importe novos arquivos OFX</p>
          </div>
        )}
      </main>
    </div>
  )
}
