import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { imports } from '../api/client'
import { format } from 'date-fns'

export default function ManageImports() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [batches, setBatches] = useState([])
  const [duplicates, setDuplicates] = useState([])
  const [selectedDuplicates, setSelectedDuplicates] = useState({})
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [activeTab, setActiveTab] = useState('batches') // 'batches' or 'duplicates'
  const [thresholdDays, setThresholdDays] = useState(3)

  useEffect(() => {
    loadBatches()
  }, [])

  const loadBatches = async () => {
    try {
      setLoading(true)
      const response = await imports.listBatches()
      setBatches(response.data.batches || [])
    } catch (err) {
      showError(err.response?.data?.error || 'Erro ao carregar lotes de importação.')
    } finally {
      setLoading(false)
    }
  }

  const loadDuplicates = async () => {
    try {
      setLoading(true)
      const response = await imports.findDuplicates(thresholdDays)
      setDuplicates(response.data.duplicates || [])
      setSelectedDuplicates({})
    } catch (err) {
      showError(err.response?.data?.error || 'Erro ao buscar duplicatas.')
    } finally {
      setLoading(false)
    }
  }

  const deleteBatch = async (batchId) => {
    if (!confirm('Tem certeza que deseja excluir este lote e todas as suas transações?')) {
      return
    }

    try {
      await imports.deleteBatch(batchId)
      showMessage('Lote removido com sucesso.')
      loadBatches()
    } catch (err) {
      showError(err.response?.data?.error || 'Erro ao remover lote.')
    }
  }

  const deleteTransaction = async (batchId, transactionId) => {
    if (!confirm('Tem certeza que deseja excluir esta transação?')) {
      return
    }

    try {
      await imports.deleteTransaction(batchId, transactionId)
      showMessage('Transação removida com sucesso.')
      loadDuplicates() // Reload duplicates
    } catch (err) {
      showError(err.response?.data?.error || 'Erro ao remover transação.')
    }
  }

  const handleSelectDuplicate = (groupIndex, transactionId) => {
    setSelectedDuplicates(prev => ({
      ...prev,
      [groupIndex]: transactionId
    }))
  }

  const mergeDuplicateGroup = async (groupIndex, transactions) => {
    const keepId = selectedDuplicates[groupIndex]
    if (!keepId) {
      showError('Selecione qual transação manter.')
      return
    }

    const removeIds = transactions
      .filter(t => t.id !== keepId)
      .map(t => t.id)

    if (removeIds.length === 0) {
      showError('Nenhuma duplicata para remover.')
      return
    }

    try {
      await imports.mergeDuplicates(keepId, removeIds)
      showMessage(`Duplicatas mescladas com sucesso. ${removeIds.length} transação(ões) removida(s).`)
      loadDuplicates()
    } catch (err) {
      showError(err.response?.data?.error || 'Erro ao mesclar duplicatas.')
    }
  }

  const showMessage = (text) => {
    setMessage(text)
    setTimeout(() => setMessage(''), 4000)
  }

  const showError = (text) => {
    setError(text)
    setTimeout(() => setError(''), 5000)
  }

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value)
  }

  const getStatusBadge = (status) => {
    const colors = {
      processing: 'bg-yellow-100 text-yellow-800',
      review: 'bg-blue-100 text-blue-800',
      completed: 'bg-green-100 text-green-800',
      failed: 'bg-red-100 text-red-800'
    }
    const labels = {
      processing: 'Processando',
      review: 'Em Revisão',
      completed: 'Concluído',
      failed: 'Falhou'
    }
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${colors[status] || 'bg-gray-100 text-gray-800'}`}>
        {labels[status] || status}
      </span>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <span className="text-3xl">📂</span>
            <div>
              <h1 className="text-xl font-bold text-gray-800">Gerenciar Importações</h1>
              <p className="text-xs text-gray-500">Edite e remova lotes, detecte duplicatas</p>
            </div>
          </div>
          <button
            onClick={() => navigate('/')}
            className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition shadow-sm"
          >
            ← Voltar
          </button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6">
        {message && (
          <div className="bg-green-100 text-green-800 px-4 py-2 rounded border border-green-200 mb-4">
            {message}
          </div>
        )}
        {error && (
          <div className="bg-red-100 text-red-800 px-4 py-2 rounded border border-red-200 mb-4">
            {error}
          </div>
        )}

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow-md mb-6">
          <div className="flex border-b">
            <button
              onClick={() => setActiveTab('batches')}
              className={`px-6 py-3 font-medium transition ${
                activeTab === 'batches'
                  ? 'border-b-2 border-blue-600 text-blue-600'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              Lotes de Importação ({batches.length})
            </button>
            <button
              onClick={() => {
                setActiveTab('duplicates')
                if (duplicates.length === 0) loadDuplicates()
              }}
              className={`px-6 py-3 font-medium transition ${
                activeTab === 'duplicates'
                  ? 'border-b-2 border-blue-600 text-blue-600'
                  : 'text-gray-600 hover:text-gray-800'
              }`}
            >
              Duplicatas ({duplicates.length})
            </button>
          </div>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <p className="mt-4 text-gray-600">Carregando...</p>
          </div>
        ) : (
          <>
            {/* Batches Tab */}
            {activeTab === 'batches' && (
              <div className="bg-white rounded-lg shadow-md overflow-hidden">
                <div className="p-4 border-b bg-gray-50">
                  <h2 className="text-lg font-semibold text-gray-800">Lotes de Importação</h2>
                  <p className="text-sm text-gray-600">Gerencie seus arquivos OFX importados</p>
                </div>

                {batches.length === 0 ? (
                  <div className="p-8 text-center text-gray-500">
                    <p>Nenhum lote importado ainda.</p>
                    <button
                      onClick={() => navigate('/import')}
                      className="mt-4 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
                    >
                      Importar Arquivo OFX
                    </button>
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead className="bg-gray-50 border-b">
                        <tr>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Arquivo</th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Instituição</th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Período</th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Transações</th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Ações</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-200">
                        {batches.map((batch) => (
                          <tr key={batch.id} className="hover:bg-gray-50 transition">
                            <td className="px-4 py-3 text-sm text-gray-900">#{batch.id}</td>
                            <td className="px-4 py-3 text-sm text-gray-900">{batch.filename}</td>
                            <td className="px-4 py-3 text-sm text-gray-600">{batch.institution_name || '—'}</td>
                            <td className="px-4 py-3 text-sm text-gray-600">
                              {batch.period_start && batch.period_end ? (
                                <>
                                  {format(new Date(batch.period_start), 'dd/MM/yyyy')} -{' '}
                                  {format(new Date(batch.period_end), 'dd/MM/yyyy')}
                                </>
                              ) : '—'}
                            </td>
                            <td className="px-4 py-3 text-sm text-gray-900">
                              {batch.processed_transactions || 0} / {batch.total_transactions || 0}
                            </td>
                            <td className="px-4 py-3">{getStatusBadge(batch.status)}</td>
                            <td className="px-4 py-3 text-sm space-x-2">
                              <button
                                onClick={() => navigate(`/batch/${batch.id}`)}
                                className="text-blue-600 hover:underline"
                              >
                                Ver
                              </button>
                              <button
                                onClick={() => deleteBatch(batch.id)}
                                className="text-red-600 hover:underline"
                              >
                                Excluir
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            )}

            {/* Duplicates Tab */}
            {activeTab === 'duplicates' && (
              <div className="space-y-4">
                <div className="bg-white rounded-lg shadow-md p-4">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h2 className="text-lg font-semibold text-gray-800">Detector de Duplicatas</h2>
                      <p className="text-sm text-gray-600">
                        Encontra transações com mesmo valor e descrição similar em datas próximas
                      </p>
                    </div>
                    <div className="flex items-center gap-3">
                      <label className="text-sm text-gray-700">
                        Dias de diferença:
                        <input
                          type="number"
                          min="1"
                          max="30"
                          value={thresholdDays}
                          onChange={(e) => setThresholdDays(parseInt(e.target.value) || 3)}
                          className="ml-2 w-16 px-2 py-1 border rounded focus:ring-2 focus:ring-blue-500"
                        />
                      </label>
                      <button
                        onClick={loadDuplicates}
                        className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
                      >
                        Buscar Duplicatas
                      </button>
                    </div>
                  </div>
                </div>

                {duplicates.length === 0 ? (
                  <div className="bg-white rounded-lg shadow-md p-8 text-center text-gray-500">
                    <p>Nenhuma duplicata encontrada.</p>
                    <p className="text-sm mt-2">Clique em "Buscar Duplicatas" para procurar transações duplicadas.</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {duplicates.map((group, groupIndex) => (
                      <div key={groupIndex} className="bg-white rounded-lg shadow-md overflow-hidden">
                        <div className="p-4 bg-yellow-50 border-b border-yellow-200">
                          <div className="flex items-center justify-between">
                            <div>
                              <h3 className="font-semibold text-gray-800">
                                Grupo {groupIndex + 1}: {group.count} transações duplicadas
                              </h3>
                              <p className="text-sm text-gray-600 mt-1">
                                {formatCurrency(group.amount)} · {group.description}
                              </p>
                            </div>
                            <button
                              onClick={() => mergeDuplicateGroup(groupIndex, group.transactions)}
                              className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition text-sm"
                            >
                              Mesclar Selecionada
                            </button>
                          </div>
                        </div>
                        <div className="divide-y divide-gray-200">
                          {group.transactions.map((tx) => (
                            <div
                              key={tx.id}
                              className={`p-4 flex items-center gap-4 hover:bg-gray-50 transition ${
                                selectedDuplicates[groupIndex] === tx.id ? 'bg-blue-50' : ''
                              }`}
                            >
                              <input
                                type="radio"
                                name={`duplicate-group-${groupIndex}`}
                                checked={selectedDuplicates[groupIndex] === tx.id}
                                onChange={() => handleSelectDuplicate(groupIndex, tx.id)}
                                className="w-4 h-4 text-blue-600"
                              />
                              <div className="flex-1 grid grid-cols-4 gap-4">
                                <div>
                                  <p className="text-xs text-gray-500">ID</p>
                                  <p className="text-sm font-medium text-gray-900">#{tx.id}</p>
                                </div>
                                <div>
                                  <p className="text-xs text-gray-500">Data</p>
                                  <p className="text-sm text-gray-900">
                                    {format(new Date(tx.date), 'dd/MM/yyyy')}
                                  </p>
                                </div>
                                <div>
                                  <p className="text-xs text-gray-500">Descrição</p>
                                  <p className="text-sm text-gray-900">{tx.description}</p>
                                </div>
                                <div>
                                  <p className="text-xs text-gray-500">Valor</p>
                                  <p className={`text-sm font-medium ${tx.amount < 0 ? 'text-red-600' : 'text-green-600'}`}>
                                    {formatCurrency(tx.amount)}
                                  </p>
                                </div>
                              </div>
                              <button
                                onClick={() => deleteTransaction(tx.import_batch_id, tx.id)}
                                className="text-red-600 hover:underline text-sm"
                              >
                                Excluir
                              </button>
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </>
        )}
      </main>
    </div>
  )
}
