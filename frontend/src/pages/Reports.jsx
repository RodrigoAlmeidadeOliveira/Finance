import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { reports, imports, catalog } from '../api/client'
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell
} from 'recharts'

// Cores padrão como fallback
const DEFAULT_COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#14B8A6', '#F97316']
const currency = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' })

export default function Reports() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [summary, setSummary] = useState(null)
  const [monthly, setMonthly] = useState([])
  const [includePending, setIncludePending] = useState(false)
  const [months, setMonths] = useState(6)
  const [start, setStart] = useState('')
  const [end, setEnd] = useState('')
  const [fallbackTransactions, setFallbackTransactions] = useState([])
  const [usingFallback, setUsingFallback] = useState(false)
  const [comparison, setComparison] = useState(null)
  const [categoryColors, setCategoryColors] = useState({})

  useEffect(() => {
    loadCategories()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    loadData()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [includePending, months])

  const loadCategories = async () => {
    try {
      const response = await catalog.listCategories()
      const categories = response.data.categories || []
      const colorMap = {}
      categories.forEach(cat => {
        if (cat.color) {
          colorMap[cat.name] = cat.color
        }
      })
      setCategoryColors(colorMap)
    } catch (error) {
      console.error('Erro ao carregar categorias:', error)
    }
  }

  const resolveDates = () => {
    if (start || end) {
      return {
        start: start || undefined,
        end: end || undefined
      }
    }
    const today = new Date()
    const endDate = today.toISOString().slice(0, 10)
    const startDateObj = new Date(today.getFullYear(), today.getMonth() - (months - 1), 1)
    const startDate = startDateObj.toISOString().slice(0, 10)
    return { start: startDate, end: endDate }
  }

  const asRangeDate = (value, isEnd = false) => {
    if (!value) return undefined
    return `${value}T${isEnd ? '23:59:59' : '00:00:00'}`
  }

  const loadData = async () => {
    setLoading(true)
    try {
      const baseDates = resolveDates()
      const params = {
        start: asRangeDate(baseDates.start, false),
        end: asRangeDate(baseDates.end, true),
        include_pending: includePending ? 1 : 0
      }
      const monthlyParams = {
        ...params,
        months
      }
      const [summaryResp, monthlyResp] = await Promise.all([
        reports.summary({
          ...params
        }),
        reports.monthly({
          ...monthlyParams
        })
      ])
      setSummary(summaryResp.data)
      setMonthly(monthlyResp.data.series || [])
      if (params.start && params.end) {
        const compareResp = await reports.compare(params)
        const prev = compareResp.data?.previous || { totals: { income: 0, expense: 0, balance: 0 } }
        const curr = summaryResp.data
        setComparison({
          previous: prev,
          current: curr,
          deltas: {
            income: (curr?.totals?.income || 0) - (prev.totals?.income || 0),
            expense: (curr?.totals?.expense || 0) - (prev.totals?.expense || 0),
            balance: (curr?.totals?.balance || 0) - (prev.totals?.balance || 0)
          }
        })
      } else {
        setComparison(null)
      }
      setUsingFallback(false)
      setFallbackTransactions([])
    } catch (error) {
      console.error('Erro ao carregar relatórios:', error)
      await loadFallback()
    } finally {
      setLoading(false)
    }
  }

  const loadFallback = async () => {
    try {
      const batchesResponse = await imports.listBatches()
      const batches = batchesResponse.data.batches || []
      const txs = []
      for (const batch of batches) {
        const transResponse = await imports.getTransactions(batch.id)
        txs.push(...(transResponse.data.transactions || []))
      }
      const filtered = filterTransactions(txs)
      setFallbackTransactions(filtered)
      setSummary(computeLocalSummary(filtered))
      setMonthly(computeLocalMonthly(filtered, months))
      setComparison(null)
      setUsingFallback(true)
    } catch (err) {
      console.error('Erro ao carregar fallback de transações:', err)
      setSummary(null)
      setMonthly([])
    }
  }

  const categoryChartData = useMemo(() => {
    if (!summary?.categories) return []
    return summary.categories
      .map((c, idx) => ({
        name: c.name.length > 20 ? `${c.name.slice(0, 20)}...` : c.name,
        fullName: c.name,
        value: Math.abs(c.total),
        income: c.income,
        expense: c.expense,
        color: categoryColors[c.name] || DEFAULT_COLORS[idx % DEFAULT_COLORS.length]
      }))
      .sort((a, b) => b.value - a.value)
      .slice(0, 8)
  }, [summary, categoryColors])

  const typeData = useMemo(() => {
    if (!summary) return []
    return [
      { name: 'Receitas', value: summary.totals?.income || 0 },
      { name: 'Despesas', value: summary.totals?.expense || 0 }
    ]
  }, [summary])

  const monthlyChartData = useMemo(() => {
    return monthly.map((m) => ({
      month: `${String(m.month).padStart(2, '0')}/${m.year}`,
      Débitos: m.expense,
      Créditos: m.income,
      Saldo: m.balance
    }))
  }, [monthly])

  const categoryPerc = useMemo(() => {
    if (!summary?.categories) return []
    const totalAbs = summary.categories.reduce((sum, c) => sum + Math.abs(c.total), 0) || 1
    return summary.categories.map((c) => ({
      name: c.name,
      perc: Math.round((Math.abs(c.total) / totalAbs) * 100)
    }))
  }, [summary])

  const filterTransactions = (txs) => {
    const { start: effectiveStart, end: effectiveEnd } = resolveDates()
    const startDate = effectiveStart ? new Date(`${effectiveStart}T00:00:00`) : null
    const endDate = effectiveEnd ? new Date(`${effectiveEnd}T23:59:59`) : null

    return txs.filter((t) => {
      const statusOk = includePending || ['approved', 'modified'].includes((t.review_status || '').toLowerCase())

      if (!statusOk) return false

      const txDate = t.date ? new Date(t.date) : null
      if (!txDate) return false

      if (startDate && txDate < startDate) return false
      if (endDate && txDate > endDate) return false

      return true
    })
  }

  const computeLocalSummary = (txs) => {
    const totals = { income: 0, expense: 0 }
    const cats = {}
    const statusCounts = {}

    txs.forEach((t) => {
      const category = t.user_category || t.predicted_category || 'Sem categoria'
      const status = t.review_status || 'pending'
      statusCounts[status] = (statusCounts[status] || 0) + 1
      if (!cats[category]) cats[category] = { name: category, income: 0, expense: 0, total: 0 }

      if (t.amount >= 0) {
        totals.income += t.amount
        cats[category].income += t.amount
        cats[category].total += t.amount
      } else {
        const val = Math.abs(t.amount)
        totals.expense += val
        cats[category].expense += val
        cats[category].total -= val
      }
    })

    return {
      totals: { ...totals, balance: totals.income - totals.expense },
      categories: Object.values(cats),
      status_counts: statusCounts,
      count: txs.length
    }
  }

  const computeLocalMonthly = (txs, monthsBack) => {
    const buckets = {}
    txs.forEach((t) => {
      const dt = new Date(t.date)
      const key = `${dt.getFullYear()}-${dt.getMonth()}`
      if (!buckets[key]) buckets[key] = { year: dt.getFullYear(), month: dt.getMonth() + 1, income: 0, expense: 0 }
      if (t.amount >= 0) buckets[key].income += t.amount
      else buckets[key].expense += Math.abs(t.amount)
    })

    return Object.values(buckets)
      .sort((a, b) => new Date(a.year, a.month - 1) - new Date(b.year, b.month - 1))
      .slice(-monthsBack)
      .map((b) => ({ ...b, balance: b.income - b.expense }))
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-800">📊 Relatórios</h1>
          <button
            onClick={() => navigate('/')}
            className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition shadow-sm"
          >
            ← Voltar
          </button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow-md p-4 mb-6">
          <h2 className="text-lg font-semibold text-gray-800 mb-3">Filtros</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm text-gray-700 mb-1" htmlFor="start-date">Data início</label>
              <input
                id="start-date"
                type="date"
                value={start}
                onChange={(e) => setStart(e.target.value)}
                className="w-full border rounded px-3 py-2"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-700 mb-1" htmlFor="end-date">Data fim</label>
              <input
                id="end-date"
                type="date"
                value={end}
                onChange={(e) => setEnd(e.target.value)}
                className="w-full border rounded px-3 py-2"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-700 mb-1" htmlFor="months">Meses (série)</label>
              <select
                id="months"
                value={months}
                onChange={(e) => setMonths(parseInt(e.target.value))}
                className="w-full border rounded px-3 py-2"
              >
                {[3, 6, 12, 24].map((m) => (
                  <option key={m} value={m}>{m} meses</option>
                ))}
              </select>
            </div>
            <div className="flex items-end gap-3">
              <label className="flex items-center gap-2 text-sm text-gray-700">
                <input
                  type="checkbox"
                  checked={includePending}
                  onChange={(e) => setIncludePending(e.target.checked)}
                />
                Incluir pendentes
              </label>
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
            <p className="mt-4 text-gray-600">Carregando relatórios...</p>
          </div>
        ) : !summary ? (
          <div className="bg-white rounded-lg shadow-md p-12 text-center">
            <div className="text-6xl mb-4">📊</div>
            <h3 className="text-xl font-bold text-gray-800 mb-2">Sem dados para exibir</h3>
            <p className="text-gray-600">Importe arquivos OFX ou inclua pendentes para visualizar relatórios</p>
          </div>
        ) : (
          <>
            {usingFallback && (
              <div className="bg-amber-50 border border-amber-200 text-amber-800 px-4 py-2 rounded mb-4">
                Exibindo dados locais (fallback) a partir das transações importadas.
              </div>
            )}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-blue-500">
                <p className="text-sm text-gray-600 mb-1">Receitas</p>
                <p className="text-3xl font-bold text-blue-600">{currency.format(summary.totals?.income || 0)}</p>
              </div>
              
              <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-red-500">
                <p className="text-sm text-gray-600 mb-1">Despesas</p>
                <p className="text-2xl font-bold text-red-600">{currency.format(summary.totals?.expense || 0)}</p>
              </div>
              
              <div className="bg-white p-6 rounded-lg shadow-md border-l-4 border-green-500">
                <p className="text-sm text-gray-600 mb-1">Saldo</p>
                <p className="text-2xl font-bold text-green-600">{currency.format(summary.totals?.balance || 0)}</p>
              </div>
            </div>

            {comparison && (summary?.count || 0) > 0 && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                <div className="bg-white p-4 rounded-lg shadow border border-blue-100">
                  <p className="text-xs text-gray-500">Comparativo Receita</p>
                  <p className="text-lg font-semibold text-gray-800">Δ {currency.format(comparison.deltas.income || 0)}</p>
                  <p className="text-xs text-gray-500">
                    Atual: {currency.format(comparison.current.totals.income || 0)} vs Anterior: {currency.format(comparison.previous.totals.income || 0)}
                  </p>
                </div>
                <div className="bg-white p-4 rounded-lg shadow border border-red-100">
                  <p className="text-xs text-gray-500">Comparativo Despesa</p>
                  <p className="text-lg font-semibold text-gray-800">Δ {currency.format(comparison.deltas.expense || 0)}</p>
                  <p className="text-xs text-gray-500">
                    Atual: {currency.format(comparison.current.totals.expense || 0)} vs Anterior: {currency.format(comparison.previous.totals.expense || 0)}
                  </p>
                </div>
                <div className="bg-white p-4 rounded-lg shadow border border-green-100">
                  <p className="text-xs text-gray-500">Comparativo Saldo</p>
                  <p className="text-lg font-semibold text-gray-800">Δ {currency.format(comparison.deltas.balance || 0)}</p>
                  <p className="text-xs text-gray-500">
                    Atual: {currency.format(comparison.current.totals.balance || 0)} vs Anterior: {currency.format(comparison.previous.totals.balance || 0)}
                  </p>
                </div>
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="bg-white p-4 rounded-lg shadow">
                <p className="text-xs text-gray-500 mb-1">Status</p>
                <div className="space-y-1 text-sm">
                  <p>Aprovadas: {summary.status_counts?.approved || 0}</p>
                  <p>Modificadas: {summary.status_counts?.modified || 0}</p>
                  <p>Pendentes: {summary.status_counts?.pending || 0}</p>
                  <p>Rejeitadas: {summary.status_counts?.rejected || 0}</p>
                </div>
              </div>
              <div className="bg-white p-4 rounded-lg shadow">
                <p className="text-xs text-gray-500 mb-1">Contagem</p>
                <p className="text-2xl font-semibold text-gray-800">{summary.count || 0} transações</p>
              </div>
              <div className="bg-white p-4 rounded-lg shadow">
                <p className="text-xs text-gray-500 mb-1">Pendentes incluídas?</p>
                <p className="text-lg font-semibold text-gray-800">{includePending ? 'Sim' : 'Não'}</p>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
              <div className="bg-white p-6 rounded-lg shadow-md">
                <h2 className="text-lg font-bold mb-4 text-gray-800">💰 Distribuição por Categoria</h2>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={categoryChartData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {categoryChartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => `R$ ${Number(value).toFixed(2)}`} />
                  </PieChart>
                </ResponsiveContainer>
              </div>

              <div className="bg-white p-6 rounded-lg shadow-md">
                <h2 className="text-lg font-bold mb-4 text-gray-800">📈 Receitas vs Despesas</h2>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie data={typeData} cx="50%" cy="50%" labelLine={false} dataKey="value" outerRadius={80}>
                      <Cell fill="#10B981" />
                      <Cell fill="#EF4444" />
                    </Pie>
                    <Tooltip formatter={(value) => `R$ ${value.toFixed(2)}`} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-md mb-6">
              <h2 className="text-lg font-bold mb-4 text-gray-800">📊 Categorias (Top 8)</h2>
              <ResponsiveContainer width="100%" height={350}>
                <BarChart data={categoryChartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip formatter={(value) => `R$ ${value.toFixed(2)}`} />
                  <Legend />
                  <Bar dataKey="value" fill="#3B82F6" name="Total" />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {categoryPerc.length > 0 && (
              <div className="bg-white p-5 rounded-lg shadow-md mb-6">
                <h2 className="text-lg font-bold mb-4 text-gray-800">Distribuição (%)</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {categoryPerc.map((c) => (
                    <div key={c.name} className="flex items-center justify-between border rounded px-3 py-2">
                      <span className="text-sm text-gray-800">{c.name}</span>
                      <span className="text-sm font-semibold text-gray-700">{c.perc}%</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {monthlyChartData.length > 0 && (
              <div className="bg-white p-6 rounded-lg shadow-md">
                <h2 className="text-lg font-bold mb-4 text-gray-800">📅 Evolução Mensal</h2>
                <ResponsiveContainer width="100%" height={350}>
                  <LineChart data={monthlyChartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip formatter={(value) => `R$ ${value.toFixed(2)}`} />
                    <Legend />
                    <Line type="monotone" dataKey="Débitos" stroke="#EF4444" strokeWidth={2} />
                    <Line type="monotone" dataKey="Créditos" stroke="#10B981" strokeWidth={2} />
                    <Line type="monotone" dataKey="Saldo" stroke="#3B82F6" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  )
}
