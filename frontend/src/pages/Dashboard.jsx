import { useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { auth, imports, ml } from '../api/client'

export default function Dashboard({ setAuth }) {
  const [user, setUser] = useState(null)
  const [batches, setBatches] = useState([])
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState({
    totalBatches: 0,
    totalTransactions: 0,
    pendingReview: 0
  })
  const [mlStats, setMlStats] = useState({ is_loaded: false, accuracy: 0, n_categories: 0 })
  const navigate = useNavigate()

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const userResponse = await auth.me()
      setUser(userResponse.data.user)

      const batchesResponse = await imports.listBatches()
      const loadedBatches = batchesResponse.data.batches || []
      setBatches(loadedBatches)

      const calculatedStats = {
        totalBatches: loadedBatches.length,
        totalTransactions: loadedBatches.reduce((sum, b) => sum + (b.total_transactions || 0), 0),
        pendingReview: loadedBatches.filter(b => b.status === 'review').length
      }
      setStats(calculatedStats)

      // Carregar estatísticas ML
      try {
        const mlResponse = await ml.stats()
        setMlStats(mlResponse.data)
      } catch (mlError) {
        console.error('Erro ao carregar stats ML:', mlError)
      }
    } catch (error) {
      console.error('Erro ao carregar dados:', error)
      if (error.response && error.response.status === 401) {
        handleLogout()
      }
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    localStorage.clear()
    setAuth(false)
    navigate('/login')
  }

  const getStatusDisplay = (status) => {
    if (status === 'completed') return '✓ Completo'
    if (status === 'review') return '⏳ Revisão'
    return status
  }

  const getStatusClass = (status) => {
    if (status === 'completed') return 'bg-green-100 text-green-800'
    if (status === 'review') return 'bg-yellow-100 text-yellow-800'
    return 'bg-gray-100 text-gray-800'
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <span className="text-3xl">💰</span>
            <div>
              <h1 className="text-xl font-bold text-gray-800">Planner Financeiro</h1>
              <p className="text-xs text-gray-500">Sistema de Gestão com ML</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-right">
              <p className="text-sm font-medium text-gray-800">{user && user.full_name}</p>
              <p className="text-xs text-gray-500">{user && user.email}</p>
            </div>
            <button
              onClick={handleLogout}
              className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition shadow-sm"
            >
              🚪 Sair
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div
            onClick={() => navigate('/import')}
            className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg cursor-pointer transition border-l-4 border-blue-500 transform hover:-translate-y-1"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="text-4xl">📁</div>
              <div className="bg-blue-100 text-blue-600 text-xs px-2 py-1 rounded font-semibold">
                Ação
              </div>
            </div>
            <h2 className="text-lg font-bold mb-2 text-gray-800">Importar OFX</h2>
            <p className="text-sm text-gray-600">Faça upload de arquivos do banco</p>
          </div>

          <div
            onClick={() => navigate('/transactions')}
            className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg cursor-pointer transition border-l-4 border-purple-500 transform hover:-translate-y-1"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="text-4xl">💳</div>
              <div className="bg-purple-100 text-purple-600 text-xs px-2 py-1 rounded font-semibold">
                Ver
              </div>
            </div>
            <h2 className="text-lg font-bold mb-2 text-gray-800">Transações</h2>
            <p className="text-sm text-gray-600">Ver e filtrar todas as transações</p>
          </div>

          <div
            onClick={() => navigate('/reports')}
            className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg cursor-pointer transition border-l-4 border-green-500 transform hover:-translate-y-1"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="text-4xl">📊</div>
              <div className="bg-green-100 text-green-600 text-xs px-2 py-1 rounded font-semibold">
                Análise
              </div>
            </div>
            <h2 className="text-lg font-bold mb-2 text-gray-800">Relatórios</h2>
            <p className="text-sm text-gray-600">Gráficos e análises financeiras</p>
          </div>

          <div
            onClick={() => navigate('/planning')}
            className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg cursor-pointer transition border-l-4 border-emerald-500 transform hover:-translate-y-1"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="text-4xl">🎯</div>
              <div className="bg-emerald-100 text-emerald-600 text-xs px-2 py-1 rounded font-semibold">
                Planejar
              </div>
            </div>
            <h2 className="text-lg font-bold mb-2 text-gray-800">Planejamento</h2>
            <p className="text-sm text-gray-600">Planos financeiros e projeções de receita</p>
          </div>

          <div
            onClick={() => navigate('/investments')}
            className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg cursor-pointer transition border-l-4 border-sky-500 transform hover:-translate-y-1"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="text-4xl">📈</div>
              <div className="bg-sky-100 text-sky-600 text-xs px-2 py-1 rounded font-semibold">
                Investir
              </div>
            </div>
            <h2 className="text-lg font-bold mb-2 text-gray-800">Investimentos</h2>
            <p className="text-sm text-gray-600">Carteira, proventos e resgates</p>
          </div>

          <div
            onClick={() => navigate('/monthly-matrix')}
            className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg cursor-pointer transition border-l-4 border-indigo-500 transform hover:-translate-y-1"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="text-4xl">📆</div>
              <div className="bg-indigo-100 text-indigo-600 text-xs px-2 py-1 rounded font-semibold">
                Matriz
              </div>
            </div>
            <h2 className="text-lg font-bold mb-2 text-gray-800">Matriz Mensal</h2>
            <p className="text-sm text-gray-600">Lançamentos por categoria e mês</p>
          </div>

          <div
            onClick={() => navigate('/simulators')}
            className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg cursor-pointer transition border-l-4 border-orange-500 transform hover:-translate-y-1"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="text-4xl">🧮</div>
              <div className="bg-orange-100 text-orange-600 text-xs px-2 py-1 rounded font-semibold">
                Simular
              </div>
            </div>
            <h2 className="text-lg font-bold mb-2 text-gray-800">Simuladores</h2>
            <p className="text-sm text-gray-600">Objetivo, tempo e montante futuro</p>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-orange-500">
            <div className="flex items-center justify-between mb-4">
              <div className="text-4xl">🤖</div>
            </div>
            <h2 className="text-lg font-bold mb-2 text-gray-800">ML Classifier</h2>
            <p className="text-sm text-orange-600 font-semibold">
              {mlStats.is_loaded
                ? `${Math.round(mlStats.accuracy * 100)}% acurácia, ${mlStats.n_categories} categorias`
                : 'Modelo não carregado'}
            </p>
          </div>

          <div
            onClick={() => navigate('/catalogs')}
            className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg cursor-pointer transition border-l-4 border-amber-500 transform hover:-translate-y-1"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="text-4xl">🗂️</div>
              <div className="bg-amber-100 text-amber-600 text-xs px-2 py-1 rounded font-semibold">
                CRUD
              </div>
            </div>
            <h2 className="text-lg font-bold mb-2 text-gray-800">Cadastros Base</h2>
            <p className="text-sm text-gray-600">Categorias, instituições, cartões e tipos</p>
          </div>

          <div
            onClick={() => navigate('/manage-imports')}
            className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg cursor-pointer transition border-l-4 border-red-500 transform hover:-translate-y-1"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="text-4xl">📂</div>
              <div className="bg-red-100 text-red-600 text-xs px-2 py-1 rounded font-semibold">
                Gerenciar
              </div>
            </div>
            <h2 className="text-lg font-bold mb-2 text-gray-800">Gerenciar Importações</h2>
            <p className="text-sm text-gray-600">Edite lotes e detecte duplicatas</p>
          </div>

          <div
            onClick={() => navigate('/ai-assistant')}
            className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg cursor-pointer transition border-l-4 border-violet-500 transform hover:-translate-y-1"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="text-4xl">🤖</div>
              <div className="bg-violet-100 text-violet-600 text-xs px-2 py-1 rounded font-semibold">
                IA
              </div>
            </div>
            <h2 className="text-lg font-bold mb-2 text-gray-800">Assistente IA</h2>
            <p className="text-sm text-gray-600">Consultoria financeira com ChatGPT</p>
          </div>

          <div
            onClick={() => navigate('/training')}
            className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg cursor-pointer transition border-l-4 border-pink-500 transform hover:-translate-y-1"
          >
            <div className="flex items-center justify-between mb-4">
              <div className="text-4xl">🎓</div>
              <div className="bg-pink-100 text-pink-600 text-xs px-2 py-1 rounded font-semibold">
                ML
              </div>
            </div>
            <h2 className="text-lg font-bold mb-2 text-gray-800">Treinar Modelo</h2>
            <p className="text-sm text-gray-600">Upload de dados e treinamento ML</p>
          </div>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <p className="mt-4 text-gray-600">Carregando lotes...</p>
          </div>
        ) : batches.length > 0 ? (
          <div className="bg-white rounded-lg shadow-md overflow-hidden">
            <div className="px-6 py-4 border-b bg-gray-50">
              <h2 className="text-xl font-bold text-gray-800">📋 Lotes Recentes</h2>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Arquivo
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Data
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Transações
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {batches.slice(0, 10).map((batch) => (
                    <tr key={batch.id} className="hover:bg-gray-50 transition">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {batch.filename}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                        {new Date(batch.created_at).toLocaleDateString('pt-BR')}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {batch.total_transactions}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={'px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ' + getStatusClass(batch.status)}>
                          {getStatusDisplay(batch.status)}
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
            <div className="text-6xl mb-4">📭</div>
            <h3 className="text-xl font-bold text-gray-800 mb-2">Nenhum lote importado</h3>
            <p className="text-gray-600 mb-6">Comece importando um arquivo OFX do seu banco</p>
            <button
              onClick={() => navigate('/import')}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition shadow-md"
            >
              📁 Importar Primeiro OFX
            </button>
          </div>
        )}
      </main>
    </div>
  )
}
