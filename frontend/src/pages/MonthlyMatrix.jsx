import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { reports, catalog } from '../api/client'

const currency = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' })

export default function MonthlyMatrix() {
  const navigate = useNavigate()
  const [months, setMonths] = useState(6)
  const [includePending, setIncludePending] = useState(false)
  const [start, setStart] = useState('')
  const [end, setEnd] = useState('')
  const [data, setData] = useState({ months: [], categories: [] })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [filters, setFilters] = useState({ type: 'all' })
  const [categoryColors, setCategoryColors] = useState({})

  useEffect(() => {
    loadCategories()
  }, [])

  useEffect(() => {
    loadData()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [months, includePending])

  const loadCategories = async () => {
    try {
      const res = await catalog.listCategories()
      const items = res.data.items || []
      const map = {}
      items.forEach((c) => {
        if (c.color) map[c.name] = c.color
      })
      setCategoryColors(map)
    } catch (err) {
      console.error('Erro ao carregar cores de categoria', err)
    }
  }

  const resolveDates = () => {
    if (start || end) {
      return { start, end }
    }
    const today = new Date()
    const endDate = today.toISOString().slice(0, 10)
    const startDate = new Date(today.getFullYear(), today.getMonth() - (months - 1), 1)
    return { start: startDate.toISOString().slice(0, 10), end: endDate }
  }

  const loadData = async () => {
    setLoading(true)
    try {
      const baseDates = resolveDates()
      const resp = await reports.monthlyCategories({
        months,
        include_pending: includePending ? 1 : 0,
        start: baseDates.start,
        end: baseDates.end
      })
      setData(resp.data || { months: [], categories: [] })
    } catch (err) {
      console.error(err)
      setError(err.response?.data?.error || 'Erro ao carregar matriz mensal.')
    } finally {
      setLoading(false)
    }
  }

  const filteredCategories = useMemo(() => {
    if (filters.type === 'all') return data.categories
    return data.categories.filter((c) => c.category_type === filters.type)
  }, [data.categories, filters.type])

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-800">📆 Lançamentos Mensais</h1>
          <button
            onClick={() => navigate('/')}
            className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition shadow-sm"
          >
            ← Voltar
          </button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6 space-y-4">
        {error && <div className="bg-red-100 text-red-800 px-4 py-2 rounded border border-red-200">{error}</div>}

        <div className="bg-white rounded-lg shadow-md p-4">
          <div className="grid grid-cols-1 md:grid-cols-6 gap-4 items-end">
            <div>
              <label className="block text-sm text-gray-700 mb-1">Meses</label>
              <select
                value={months}
                onChange={(e) => setMonths(Number(e.target.value))}
                className="w-full border rounded px-3 py-2"
              >
                {[3, 6, 12, 24].map((m) => (
                  <option key={m} value={m}>{m} meses</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm text-gray-700 mb-1">Data início</label>
              <input
                type="date"
                value={start}
                onChange={(e) => setStart(e.target.value)}
                className="w-full border rounded px-3 py-2"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-700 mb-1">Data fim</label>
              <input
                type="date"
                value={end}
                onChange={(e) => setEnd(e.target.value)}
                className="w-full border rounded px-3 py-2"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-700 mb-1">Filtro</label>
              <select
                value={filters.type}
                onChange={(e) => setFilters({ ...filters, type: e.target.value })}
                className="w-full border rounded px-3 py-2"
              >
                <option value="all">Receitas e Despesas</option>
                <option value="income">Só Receitas</option>
                <option value="expense">Só Despesas</option>
              </select>
            </div>
            <div className="flex items-center gap-2">
              <input
                id="include-pending"
                type="checkbox"
                checked={includePending}
                onChange={(e) => setIncludePending(e.target.checked)}
              />
              <label htmlFor="include-pending" className="text-sm text-gray-700">Incluir pendentes</label>
            </div>
            <div className="flex justify-end">
              <button
                onClick={loadData}
                className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
              >
                Atualizar
              </button>
            </div>
          </div>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <p className="mt-4 text-gray-600">Carregando matriz mensal...</p>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-semibold text-gray-600 w-56">Categoria</th>
                  {data.months.map((m) => (
                    <th key={m.key} className="px-4 py-3 text-right text-xs font-semibold text-gray-600">
                      {String(m.month).padStart(2, '0')}/{m.year}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {filteredCategories.map((cat) => (
                  <tr key={cat.name} className="hover:bg-gray-50">
                    <td className="px-4 py-2 font-medium text-gray-800">
                      <span
                        className="inline-block w-3 h-3 rounded-full mr-2 align-middle"
                        style={{ background: categoryColors[cat.name] || '#CBD5E1' }}
                      ></span>
                      {cat.name}
                    </td>
                    {data.months.map((m) => (
                      <td key={`${cat.name}-${m.key}`} className="px-4 py-2 text-right tabular-nums">
                        <div className="flex flex-col items-end leading-tight">
                          {cat.values[m.key]?.planned && cat.values[m.key]?.planned !== 0 ? (
                            <span className={cat.values[m.key].planned >= 0 ? 'text-gray-600' : 'text-gray-600'}>
                              Previsto: {currency.format(cat.values[m.key].planned)}
                            </span>
                          ) : null}
                          {cat.values[m.key]?.actual && cat.values[m.key]?.actual !== 0 ? (
                            <span className={cat.values[m.key].actual >= 0 ? 'text-green-600 font-semibold' : 'text-red-600 font-semibold'}>
                              Real: {currency.format(cat.values[m.key].actual)}
                            </span>
                          ) : cat.values[m.key]?.planned ? (
                            <span className="text-xs text-gray-400">Sem realizado</span>
                          ) : (
                            '—'
                          )}
                        </div>
                      </td>
                    ))}
                  </tr>
                ))}
                {filteredCategories.length === 0 && (
                  <tr>
                    <td colSpan={1 + data.months.length} className="px-4 py-4 text-center text-gray-500">
                      Nenhuma categoria encontrada no período.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </main>
    </div>
  )
}
