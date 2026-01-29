import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { imports, catalog } from '../api/client'

export default function ImportOFX() {
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [categories, setCategories] = useState([])
  const [selectedCategories, setSelectedCategories] = useState({})
  const navigate = useNavigate()

  useEffect(() => {
    loadCategories()
  }, [])

  const loadCategories = async () => {
    try {
      const response = await catalog.listCategories()
      setCategories(response.data.items || [])
    } catch (err) {
      console.error('Erro ao carregar categorias:', err)
    }
  }

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile && selectedFile.name.endsWith('.ofx')) {
      setFile(selectedFile)
      setError('')
    } else {
      setError('Por favor, selecione um arquivo .ofx')
      setFile(null)
    }
  }

  const handleUpload = async () => {
    if (!file) {
      setError('Selecione um arquivo OFX')
      return
    }

    setLoading(true)
    setError('')

    try {
      const response = await imports.upload(file)
      setResult(response.data)

      // Initialize selected categories with predicted categories
      const initialCategories = {}
      response.data.pending_transactions.forEach(t => {
        initialCategories[t.id] = t.predicted_category
      })
      setSelectedCategories(initialCategories)
    } catch (err) {
      setError(err.response && err.response.data && err.response.data.error ? err.response.data.error : 'Erro ao importar arquivo')
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

  const handleReviewTransaction = async (transactionId) => {
    const category = selectedCategories[transactionId]
    if (!category) {
      alert('Selecione uma categoria antes de aprovar')
      return
    }

    try {
      await imports.reviewTransaction(
        result.batch.id,
        transactionId,
        category,
        'approved',
        null
      )

      setResult({
        ...result,
        pending_transactions: result.pending_transactions.map(t =>
          t.id === transactionId
            ? { ...t, review_status: 'approved', user_category: category }
            : t
        )
      })
    } catch (err) {
      console.error('Erro ao revisar transação:', err)
    }
  }

  const getConfidenceClass = (level) => {
    if (level === 'high') return 'bg-green-100 text-green-800'
    if (level === 'medium') return 'bg-yellow-100 text-yellow-800'
    return 'bg-red-100 text-red-800'
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-800">📁 Importar OFX</h1>
          <button
            onClick={() => navigate('/')}
            className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition shadow-sm"
          >
            ← Voltar
          </button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {!result && (
          <div className="bg-white rounded-lg shadow-md p-8 max-w-2xl mx-auto">
            <h2 className="text-xl font-bold mb-6 text-gray-800">Selecione um arquivo OFX</h2>

            {error && (
              <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                {error}
              </div>
            )}

            <div className="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center mb-6 hover:border-blue-400 transition">
              <input
                type="file"
                accept=".ofx"
                onChange={handleFileChange}
                className="hidden"
                id="file-upload"
              />
              <label htmlFor="file-upload" className="cursor-pointer">
                {file ? (
                  <div>
                    <div className="text-6xl mb-4">✅</div>
                    <p className="font-medium text-lg text-gray-800">{file.name}</p>
                    <p className="text-sm text-gray-500 mt-2">
                      {(file.size / 1024).toFixed(2)} KB
                    </p>
                    <p className="text-sm text-blue-600 mt-4">
                      Clique para selecionar outro arquivo
                    </p>
                  </div>
                ) : (
                  <div>
                    <div className="text-6xl mb-4">📁</div>
                    <p className="font-medium text-lg text-gray-800">
                      Clique para selecionar arquivo
                    </p>
                    <p className="text-sm text-gray-500 mt-2">
                      Apenas arquivos .ofx do seu banco
                    </p>
                  </div>
                )}
              </label>
            </div>

            <button
              onClick={handleUpload}
              disabled={!file || loading}
              className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 disabled:bg-gray-400 transition font-medium shadow-md hover:shadow-lg"
            >
              {loading ? '⏳ Processando com ML...' : '🤖 Importar e Classificar com ML'}
            </button>
          </div>
        )}

        {result && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-bold mb-4 text-gray-800">✅ Resumo da Importação</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-blue-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-600 mb-1">Total de Transações</p>
                  <p className="text-3xl font-bold text-blue-600">
                    {result.summary.transactions.total}
                  </p>
                </div>
                <div className="bg-red-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-600 mb-1">Débitos</p>
                  <p className="text-3xl font-bold text-red-600">
                    {result.summary.transactions.debits.count}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    R$ {Math.abs(result.summary.transactions.debits.total).toFixed(2)}
                  </p>
                </div>
                <div className="bg-green-50 p-4 rounded-lg">
                  <p className="text-sm text-gray-600 mb-1">Créditos</p>
                  <p className="text-3xl font-bold text-green-600">
                    {result.summary.transactions.credits.count}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    R$ {result.summary.transactions.credits.total.toFixed(2)}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-md overflow-hidden">
              <div className="px-6 py-4 border-b bg-gray-50">
                <h2 className="text-xl font-bold text-gray-800">
                  🤖 Transações Classificadas por ML
                </h2>
                <p className="text-sm text-gray-600 mt-1">
                  Revise e aprove as classificações sugeridas
                </p>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Data
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Descrição
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Valor
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Categoria ML
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Confiança
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Selecionar Categoria
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                        Ação
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {result.pending_transactions.map((transaction) => (
                      <tr key={transaction.id} className="hover:bg-gray-50 transition">
                        <td className="px-6 py-4 text-sm whitespace-nowrap text-gray-900">
                          {new Date(transaction.date).toLocaleDateString('pt-BR')}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-900">
                          <div className="max-w-xs truncate" title={transaction.description}>
                            {transaction.description}
                          </div>
                        </td>
                        <td className={'px-6 py-4 text-sm font-semibold whitespace-nowrap ' + (transaction.amount < 0 ? 'text-red-600' : 'text-green-600')}>
                          R$ {Math.abs(transaction.amount).toFixed(2)}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-900">
                          <span className="font-medium">{transaction.predicted_category}</span>
                        </td>
                        <td className="px-6 py-4 text-sm">
                          <span className={'px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ' + getConfidenceClass(transaction.confidence_level)}>
                            {(transaction.confidence_score * 100).toFixed(0)}%
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm">
                          {transaction.review_status === 'approved' ? (
                            <span className="text-green-600 font-medium">{transaction.user_category}</span>
                          ) : (
                            <select
                              value={selectedCategories[transaction.id] || transaction.predicted_category}
                              onChange={(e) => handleCategoryChange(transaction.id, e.target.value)}
                              className="w-full px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                            >
                              {categories
                                .sort((a, b) => a.name.localeCompare(b.name))
                                .map(cat => (
                                  <option key={cat.id} value={cat.name}>{cat.name}</option>
                                ))}
                            </select>
                          )}
                        </td>
                        <td className="px-6 py-4 text-sm whitespace-nowrap">
                          {transaction.review_status === 'approved' ? (
                            <span className="text-green-600 font-medium">✓ Aprovado</span>
                          ) : (
                            <button
                              onClick={() => handleReviewTransaction(transaction.id)}
                              className="bg-blue-600 text-white px-4 py-1 rounded hover:bg-blue-700 transition shadow-sm"
                            >
                              ✓ Aprovar
                            </button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="flex gap-4">
              <button
                onClick={() => setResult(null)}
                className="flex-1 bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 transition shadow-md"
              >
                📁 Nova Importação
              </button>
              <button
                onClick={() => navigate('/')}
                className="flex-1 bg-gray-600 text-white py-3 px-4 rounded-lg hover:bg-gray-700 transition shadow-md"
              >
                ← Voltar ao Dashboard
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
