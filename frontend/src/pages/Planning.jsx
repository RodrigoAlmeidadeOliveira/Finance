import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { planning, catalog } from '../api/client'
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Legend, CartesianGrid } from 'recharts'

const currency = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' })

const emptyPlan = {
  name: '',
  goal_amount: '',
  current_balance: '',
  monthly_contribution: '',
  institution_id: '',
  partition: '',
  target_date: '',
  notes: ''
}

const emptyProjection = {
  description: '',
  amount: '',
  expected_date: '',
  projection_type: 'fixed',
  received: false
}

export default function Planning() {
  const navigate = useNavigate()
  const [plans, setPlans] = useState([])
  const [projections, setProjections] = useState([])
  const [budgets, setBudgets] = useState([])
  const [budgetCompliance, setBudgetCompliance] = useState([])
  const [budgetForm, setBudgetForm] = useState({
    category_id: '',
    amount: '',
    month: new Date().getMonth() + 1,
    year: new Date().getFullYear()
  })
  const [categories, setCategories] = useState([])
  const [institutions, setInstitutions] = useState([])
  const [planForm, setPlanForm] = useState(emptyPlan)
  const [projectionForm, setProjectionForm] = useState(emptyProjection)
  const [planUpdates, setPlanUpdates] = useState({})
  const [recurringList, setRecurringList] = useState([])
  const [recurringForm, setRecurringForm] = useState({ category_id: '', amount: '', start_date: '', end_date: '' })
  const [start, setStart] = useState('')
  const [end, setEnd] = useState('')
  const [months, setMonths] = useState(6)
  const [includeReceived, setIncludeReceived] = useState(true)
  const [includePendingTx, setIncludePendingTx] = useState(false)
  const [editingPlanId, setEditingPlanId] = useState(null)
  const [plannedSurplus, setPlannedSurplus] = useState({ projected_income: 0, expense_budget: 0, planned_surplus: 0 })
  const [notesList, setNotesList] = useState([])
  const [noteContent, setNoteContent] = useState('')
  const [loading, setLoading] = useState(true)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    loadAll()
  }, [])

  const resolveProjectionDates = () => {
    if (start || end) {
      return {
        start: start || undefined,
        end: end || undefined
      }
    }

    const today = new Date()
    const startDate = today.toISOString().slice(0, 10)
    const endDate = new Date(today.getFullYear(), today.getMonth() + months, 0).toISOString().slice(0, 10)
    return { start: startDate, end: endDate }
  }

  const loadAll = async () => {
    try {
      setLoading(true)
      const baseDates = resolveProjectionDates()
      const [
        plansResp,
        projResp,
        instResp,
        budgetsResp,
        complianceResp,
        categoriesResp,
        surplusResp,
        notesResp,
        recurringResp
      ] = await Promise.all([
        planning.listPlans(),
        planning.listIncomeProjections({
          start: baseDates.start,
          end: baseDates.end,
          include_received: includeReceived ? 1 : 0
        }),
        catalog.listInstitutions(),
        planning.listBudgets({ month: budgetForm.month, year: budgetForm.year }),
        planning.budgetCompliance({
          start: baseDates.start,
          end: baseDates.end,
          include_pending: includePendingTx ? 1 : 0
        }),
        catalog.listCategories({ include_inactive: true }),
        planning.plannedSurplus(),
        planning.listNotes(),
        planning.listRecurring()
      ])
      setPlans(plansResp.data.items || [])
      setProjections(projResp.data.items || [])
      setInstitutions(instResp.data.items || [])
      setBudgets(budgetsResp.data.items || [])
      setBudgetCompliance(complianceResp.data.items || [])
      setCategories(categoriesResp.data.items || [])
      setPlannedSurplus(surplusResp.data || { projected_income: 0, expense_budget: 0, planned_surplus: 0 })
      setNotesList(notesResp.data.items || [])
      setRecurringList(recurringResp.data.items || [])
    } catch (err) {
      setError(err.response?.data?.error || 'Erro ao carregar planejamento.')
    } finally {
      setLoading(false)
    }
  }

  const handleMessage = (text) => {
    setMessage(text)
    setTimeout(() => setMessage(''), 3000)
  }

  const handleError = (text) => {
    setError(text)
    setTimeout(() => setError(''), 4000)
  }

  const submitPlan = async (e) => {
    e.preventDefault()
    try {
      if (editingPlanId) {
        await planning.updatePlan(editingPlanId, {
          ...planForm,
          goal_amount: planForm.goal_amount ? Number(planForm.goal_amount) : undefined,
          current_balance: planForm.current_balance ? Number(planForm.current_balance) : undefined,
          monthly_contribution: planForm.monthly_contribution ? Number(planForm.monthly_contribution) : undefined,
          institution_id: planForm.institution_id ? Number(planForm.institution_id) : undefined
        })
        handleMessage('Plano atualizado.')
      } else {
        await planning.createPlan({
          ...planForm,
          goal_amount: Number(planForm.goal_amount),
          current_balance: planForm.current_balance ? Number(planForm.current_balance) : 0,
          monthly_contribution: planForm.monthly_contribution ? Number(planForm.monthly_contribution) : 0,
          institution_id: planForm.institution_id ? Number(planForm.institution_id) : null
        })
        handleMessage('Plano criado.')
      }
      setPlanForm(emptyPlan)
      setEditingPlanId(null)
      loadAll()
    } catch (err) {
      handleError(err.response?.data?.error || 'Erro ao criar plano.')
    }
  }

  const submitProjection = async (e) => {
    e.preventDefault()
    try {
      await planning.createIncomeProjection({
        ...projectionForm,
        amount: Number(projectionForm.amount),
        received: Boolean(projectionForm.received)
      })
      setProjectionForm(emptyProjection)
      handleMessage('Projeção criada.')
      loadAll()
    } catch (err) {
      handleError(err.response?.data?.error || 'Erro ao criar projeção.')
    }
  }

  const submitBudget = async (e) => {
    e.preventDefault()
    try {
      await planning.createBudget({
        category_id: Number(budgetForm.category_id),
        amount: Number(budgetForm.amount),
        month: Number(budgetForm.month),
        year: Number(budgetForm.year)
      })
      handleMessage('Meta salva.')
      loadAll()
    } catch (err) {
      handleError(err.response?.data?.error || 'Erro ao salvar meta.')
    }
  }

  const deleteBudget = async (id) => {
    try {
      await planning.deleteBudget(id)
      handleMessage('Meta removida.')
      loadAll()
    } catch (err) {
      handleError('Erro ao remover meta.')
    }
  }

  const applyPlanUpdate = async (planId) => {
    const update = planUpdates[planId] || {}
    const topUp = update.topUp ? Number(update.topUp) : 0
    const monthly = update.monthly ? Number(update.monthly) : null

    if (!topUp && monthly === null) {
      handleError('Informe um aporte ou um novo valor mensal.')
      return
    }

    const plan = plans.find((p) => p.id === planId)
    if (!plan) return

    const payload = {}
    if (topUp) {
      payload.current_balance = (plan.current_balance || 0) + topUp
    }
    if (monthly !== null) {
      payload.monthly_contribution = monthly
    }

    try {
      await planning.updatePlan(planId, payload)
      setPlanUpdates((prev) => ({ ...prev, [planId]: { topUp: '', monthly: '' } }))
      handleMessage('Plano atualizado.')
      loadAll()
    } catch (err) {
      handleError(err.response?.data?.error || 'Erro ao atualizar plano.')
    }
  }

  const toggleReceived = async (item) => {
    try {
      await planning.updateIncomeProjection(item.id, { received: !item.received })
      loadAll()
    } catch (err) {
      handleError('Erro ao atualizar projeção.')
    }
  }

  const deleteItem = async (type, id) => {
    try {
      if (type === 'plan') await planning.deletePlan(id)
      else await planning.deleteIncomeProjection(id)
      loadAll()
    } catch (err) {
      handleError('Erro ao remover.')
    }
  }

  const progressAverage = useMemo(() => {
    if (!plans.length) return 0
    return Math.round(plans.reduce((sum, p) => sum + (p.progress || 0), 0) / plans.length)
  }, [plans])

  const projectionsSummary = useMemo(() => {
    return projections.reduce(
      (acc, p) => {
        const amount = Number(p.amount) || 0
        if (p.received) {
          acc.received += amount
        } else {
          acc.pending += amount
        }
        if (p.projection_type === 'extra') {
          acc.extra += amount
        } else {
          acc.fixed += amount
        }
        acc.total += amount
        return acc
      },
      { total: 0, fixed: 0, extra: 0, received: 0, pending: 0 }
    )
  }, [projections])

  const projectionSeries = useMemo(() => {
    const buckets = {}
    projections.forEach((p) => {
      if (!p.expected_date) return
      const dt = new Date(p.expected_date)
      const key = `${dt.getFullYear()}-${dt.getMonth()}`
      if (!buckets[key]) {
        buckets[key] = {
          monthLabel: `${String(dt.getMonth() + 1).padStart(2, '0')}/${dt.getFullYear()}`,
          fixed: 0,
          extra: 0,
          total: 0
        }
      }
      const amount = Number(p.amount) || 0
      if (p.projection_type === 'extra') {
        buckets[key].extra += amount
      } else {
        buckets[key].fixed += amount
      }
      buckets[key].total += amount
    })
    return Object.values(buckets).sort((a, b) => {
      const [mA, yA] = a.monthLabel.split('/')
      const [mB, yB] = b.monthLabel.split('/')
      return new Date(Number(yA), Number(mA) - 1) - new Date(Number(yB), Number(mB) - 1)
    })
  }, [projections])

  const concludePlan = async (plan) => {
    try {
      await planning.updatePlan(plan.id, { current_balance: plan.goal_amount, is_active: false })
      handleMessage('Plano concluído.')
      loadAll()
    } catch (err) {
      handleError('Erro ao concluir plano.')
    }
  }

  const addNote = async (e) => {
    e.preventDefault()
    if (!noteContent.trim()) return
    try {
      await planning.createNote({ content: noteContent })
      setNoteContent('')
      loadAll()
    } catch (err) {
      handleError(err.response?.data?.error || 'Erro ao salvar nota.')
    }
  }

  const removeNote = async (id) => {
    try {
      await planning.deleteNote(id)
      loadAll()
    } catch (err) {
      handleError('Erro ao remover nota.')
    }
  }

  const createRecurring = async (e) => {
    e.preventDefault()
    try {
      await planning.createRecurring({
        category_id: Number(recurringForm.category_id),
        amount: Number(recurringForm.amount),
        start_date: recurringForm.start_date,
        end_date: recurringForm.end_date || null
      })
      setRecurringForm({ category_id: '', amount: '', start_date: '', end_date: '' })
      handleMessage('Recorrência criada.')
      loadAll()
    } catch (err) {
      handleError(err.response?.data?.error || 'Erro ao criar recorrência.')
    }
  }

  const deleteRecurring = async (id) => {
    try {
      await planning.deleteRecurring(id)
      loadAll()
    } catch (err) {
      handleError('Erro ao remover recorrência.')
    }
  }

  const startEditPlan = (plan) => {
    setEditingPlanId(plan.id)
    setPlanForm({
      name: plan.name,
      goal_amount: plan.goal_amount,
      current_balance: plan.current_balance,
      monthly_contribution: plan.monthly_contribution,
      institution_id: plan.institution_id || '',
      partition: plan.partition || '',
      target_date: plan.target_date || '',
      notes: plan.notes || ''
    })
  }

  const timeline = useMemo(() => {
    return [...plans].sort((a, b) => {
      if (!a.target_date) return 1
      if (!b.target_date) return -1
      return new Date(a.target_date) - new Date(b.target_date)
    })
  }, [plans])

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <span className="text-3xl">🎯</span>
            <div>
              <h1 className="text-xl font-bold text-gray-800">Planejamento</h1>
              <p className="text-xs text-gray-500">Planos financeiros e projeções de receita</p>
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

      <main className="max-w-7xl mx-auto px-4 py-6 space-y-6">
        {message && <div className="bg-green-100 text-green-800 px-4 py-2 rounded border border-green-200">{message}</div>}
        {error && <div className="bg-red-100 text-red-800 px-4 py-2 rounded border border-red-200">{error}</div>}

        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <p className="mt-4 text-gray-600">Carregando planejamento...</p>
          </div>
        ) : (
          <>
            <section className="bg-white rounded-lg shadow-md p-4 mb-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="text-lg font-semibold text-gray-800">Filtros de período (projeções)</h2>
                  <p className="text-xs text-gray-500">Usa o mesmo padrão de período da tela de relatórios</p>
                </div>
                <button
                  onClick={loadAll}
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
                >
                  Atualizar
                </button>
              </div>
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
                  <label className="block text-sm text-gray-700 mb-1" htmlFor="months">Meses (janela)</label>
                  <select
                    id="months"
                    value={months}
                    onChange={(e) => setMonths(Number(e.target.value))}
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
                      checked={includeReceived}
                      onChange={(e) => setIncludeReceived(e.target.checked)}
                    />
                    Incluir recebidas
                  </label>
                  <label className="flex items-center gap-2 text-sm text-gray-700">
                    <input
                      type="checkbox"
                      checked={includePendingTx}
                      onChange={(e) => setIncludePendingTx(e.target.checked)}
                    />
                    Incluir pendentes (compliance)
                  </label>
                  <div className="text-xs text-gray-500">
                    Janela: {resolveProjectionDates().start} → {resolveProjectionDates().end}
                  </div>
                </div>
              </div>
            </section>

            <section className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-white p-4 rounded-lg shadow border-l-4 border-blue-500">
                <p className="text-xs text-gray-500">Planos ativos</p>
                <p className="text-3xl font-bold text-gray-800">{plans.length}</p>
              </div>
              <div className="bg-white p-4 rounded-lg shadow border-l-4 border-green-500">
                <p className="text-xs text-gray-500">Projeções no período</p>
                <p className="text-3xl font-bold text-gray-800">{projections.length}</p>
              </div>
              <div className="bg-white p-4 rounded-lg shadow border-l-4 border-amber-500">
                <p className="text-xs text-gray-500">% médio concluído</p>
                <p className="text-3xl font-bold text-gray-800">{progressAverage}%</p>
              </div>
              <div className="bg-white p-4 rounded-lg shadow border-l-4 border-indigo-500">
                <p className="text-xs text-gray-500">Previsto (fixa + extra)</p>
                <p className="text-2xl font-bold text-gray-800">{currency.format(projectionsSummary.total)}</p>
              </div>
            </section>

            <section className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-white p-4 rounded-lg shadow border-l-4 border-emerald-500">
                <p className="text-xs text-gray-500">Receitas projetadas (abertas)</p>
                <p className="text-xl font-bold text-gray-800">{currency.format(plannedSurplus.projected_income || 0)}</p>
              </div>
              <div className="bg-white p-4 rounded-lg shadow border-l-4 border-red-500">
                <p className="text-xs text-gray-500">Orçamentos de despesa</p>
                <p className="text-xl font-bold text-gray-800">{currency.format(plannedSurplus.expense_budget || 0)}</p>
              </div>
              <div className="bg-white p-4 rounded-lg shadow border-l-4 border-blue-500">
                <p className="text-xs text-gray-500">Sobra planejada</p>
                <p className="text-xl font-bold text-gray-800">{currency.format(plannedSurplus.planned_surplus || 0)}</p>
              </div>
            </section>

            <section className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-white p-4 rounded-lg shadow border-l-4 border-emerald-500">
                <p className="text-xs text-gray-500">Receitas projetadas (abertas)</p>
                <p className="text-xl font-bold text-gray-800">{currency.format(plannedSurplus.projected_income || 0)}</p>
              </div>
              <div className="bg-white p-4 rounded-lg shadow border-l-4 border-red-500">
                <p className="text-xs text-gray-500">Orçamentos de despesa</p>
                <p className="text-xl font-bold text-gray-800">{currency.format(plannedSurplus.expense_budget || 0)}</p>
              </div>
              <div className="bg-white p-4 rounded-lg shadow border-l-4 border-blue-500">
                <p className="text-xs text-gray-500">Sobra planejada</p>
                <p className="text-xl font-bold text-gray-800">{currency.format(plannedSurplus.planned_surplus || 0)}</p>
              </div>
            </section>

            <section className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div className="bg-white p-4 rounded-lg shadow border-l-4 border-green-500">
                <p className="text-xs text-gray-500">Receitas fixas</p>
                <p className="text-xl font-bold text-gray-800">{currency.format(projectionsSummary.fixed)}</p>
              </div>
              <div className="bg-white p-4 rounded-lg shadow border-l-4 border-amber-500">
                <p className="text-xs text-gray-500">Receitas extras</p>
                <p className="text-xl font-bold text-gray-800">{currency.format(projectionsSummary.extra)}</p>
              </div>
              <div className="bg-white p-4 rounded-lg shadow border-l-4 border-red-500">
                <p className="text-xs text-gray-500">Pendentes</p>
                <p className="text-xl font-bold text-gray-800">{currency.format(projectionsSummary.pending)}</p>
              </div>
            </section>

            {projectionSeries.length > 0 && (
              <section className="bg-white rounded-lg shadow-md p-5 mb-6">
                <div className="flex items-center justify-between mb-3">
                  <h2 className="text-lg font-semibold text-gray-800">Projeção por mês</h2>
                  <span className="text-xs text-gray-500">{projectionSeries.length} meses</span>
                </div>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={projectionSeries}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="monthLabel" />
                    <YAxis />
                    <Tooltip formatter={(value) => currency.format(value)} />
                    <Legend />
                    <Bar dataKey="fixed" stackId="total" fill="#3B82F6" name="Fixa" />
                    <Bar dataKey="extra" stackId="total" fill="#F97316" name="Extra" />
                  </BarChart>
                </ResponsiveContainer>
              </section>
            )}

            <section className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
              <div className="bg-white rounded-lg shadow-md p-5">
                <h2 className="text-lg font-semibold text-gray-800 mb-3">Planejamento mensal por categoria</h2>
                <form className="grid grid-cols-1 md:grid-cols-2 gap-3" onSubmit={submitBudget}>
                  <div className="md:col-span-2">
                    <label className="block text-sm text-gray-700 mb-1" htmlFor="budget-category">Categoria</label>
                    <select
                      id="budget-category"
                      value={budgetForm.category_id}
                      onChange={(e) => setBudgetForm({ ...budgetForm, category_id: e.target.value })}
                      required
                      className="w-full border rounded px-3 py-2"
                    >
                      <option value="">Selecione</option>
                      {categories.map((c) => (
                        <option key={c.id} value={c.id}>
                          {c.name} ({c.type === 'expense' ? 'Despesa' : 'Receita'})
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm text-gray-700 mb-1" htmlFor="budget-month">Mês</label>
                    <input
                      id="budget-month"
                      type="number"
                      min="1"
                      max="12"
                      value={budgetForm.month}
                      onChange={(e) => setBudgetForm({ ...budgetForm, month: e.target.value })}
                      className="w-full border rounded px-3 py-2"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-700 mb-1" htmlFor="budget-year">Ano</label>
                    <input
                      id="budget-year"
                      type="number"
                      value={budgetForm.year}
                      onChange={(e) => setBudgetForm({ ...budgetForm, year: e.target.value })}
                      className="w-full border rounded px-3 py-2"
                      required
                    />
                  </div>
                  <div className="md:col-span-2">
                    <label className="block text-sm text-gray-700 mb-1" htmlFor="budget-amount">Valor (meta)</label>
                    <input
                      id="budget-amount"
                      type="number"
                      value={budgetForm.amount}
                      onChange={(e) => setBudgetForm({ ...budgetForm, amount: e.target.value })}
                      className="w-full border rounded px-3 py-2"
                      required
                    />
                  </div>
                  <div className="md:col-span-2 flex justify-end">
                    <button type="submit" className="bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700">
                      Salvar meta
                    </button>
                  </div>
                </form>
              </div>

              <div className="bg-white rounded-lg shadow-md p-5">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-lg font-semibold text-gray-800">Metas cadastradas</h3>
                  <span className="text-xs text-gray-500">{budgets.length} itens</span>
                </div>
                <div className="divide-y divide-gray-100">
                  {budgets.map((b) => (
                    <div key={b.id} className="py-2 flex items-center justify-between">
                      <div>
                        <p className="font-semibold text-gray-800">
                          {b.category_name || `Categoria #${b.category_id}`}
                        </p>
                        <p className="text-xs text-gray-500">
                          {String(b.month).padStart(2, '0')}/{b.year} · {currency.format(b.amount)}
                        </p>
                      </div>
                      <button
                        onClick={() => deleteBudget(b.id)}
                        className="text-sm text-red-600 hover:underline"
                      >
                        Remover
                      </button>
                    </div>
                  ))}
                  {budgets.length === 0 && <p className="text-sm text-gray-500 py-2">Nenhuma meta cadastrada.</p>}
                </div>
              </div>
            </section>

            {budgetCompliance.length > 0 && (
              <section className="bg-white rounded-lg shadow-md p-5 mb-6">
                <div className="flex items-center justify-between mb-3">
                  <h2 className="text-lg font-semibold text-gray-800">Compliance do planejamento</h2>
                  <span className="text-xs text-gray-500">{budgetCompliance.length} categorias</span>
                </div>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200 text-sm">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-3 py-2 text-left text-xs font-semibold text-gray-600">Categoria</th>
                        <th className="px-3 py-2 text-left text-xs font-semibold text-gray-600">Meta</th>
                        <th className="px-3 py-2 text-left text-xs font-semibold text-gray-600">Realizado</th>
                        <th className="px-3 py-2 text-left text-xs font-semibold text-gray-600">Delta</th>
                        <th className="px-3 py-2 text-left text-xs font-semibold text-gray-600">Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {budgetCompliance.map((item) => (
                        <tr key={item.budget_id}>
                          <td className="px-3 py-2">
                            <div className="font-semibold text-gray-800">{item.category_name}</div>
                            <div className="text-xs text-gray-500">
                              {String(item.month).padStart(2, '0')}/{item.year} · {item.category_type === 'income' ? 'Receita' : 'Despesa'}
                            </div>
                          </td>
                          <td className="px-3 py-2">{currency.format(item.target)}</td>
                          <td className="px-3 py-2">{currency.format(item.actual)}</td>
                          <td className="px-3 py-2">{currency.format(item.delta)}</td>
                          <td className="px-3 py-2">
                            <span
                              className={`px-2 py-1 rounded text-xs ${
                                item.status === 'ok' ? 'bg-green-100 text-green-700' : 'bg-amber-100 text-amber-700'
                              }`}
                            >
                              {item.status === 'ok' ? 'OK' : 'Alerta'}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </section>
            )}

            <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white rounded-lg shadow-md p-5">
                <h2 className="text-lg font-semibold text-gray-800 mb-4">Novo Plano</h2>
                <form className="grid grid-cols-1 md:grid-cols-2 gap-4" onSubmit={submitPlan}>
                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="plan-name">Nome</label>
                    <input
                      id="plan-name"
                      type="text"
                      value={planForm.name}
                      onChange={(e) => setPlanForm({ ...planForm, name: e.target.value })}
                      required
                      className="w-full border rounded px-3 py-2"
                    />
                    {editingPlanId && <p className="text-xs text-gray-500 mt-1">Editando plano #{editingPlanId} — deixe campos em branco para manter valores.</p>}
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="goal">Meta (R$)</label>
                    <input
                      id="goal"
                      type="number"
                      value={planForm.goal_amount}
                      onChange={(e) => setPlanForm({ ...planForm, goal_amount: e.target.value })}
                      required
                      className="w-full border rounded px-3 py-2"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="current">Acumulado (R$)</label>
                    <input
                      id="current"
                      type="number"
                      value={planForm.current_balance}
                      onChange={(e) => setPlanForm({ ...planForm, current_balance: e.target.value })}
                      className="w-full border rounded px-3 py-2"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="monthly">Aporte mensal (R$)</label>
                    <input
                      id="monthly"
                      type="number"
                      value={planForm.monthly_contribution}
                      onChange={(e) => setPlanForm({ ...planForm, monthly_contribution: e.target.value })}
                      className="w-full border rounded px-3 py-2"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="target">Data alvo</label>
                    <input
                      id="target"
                      type="date"
                      value={planForm.target_date}
                      onChange={(e) => setPlanForm({ ...planForm, target_date: e.target.value })}
                      className="w-full border rounded px-3 py-2"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="inst">Instituição</label>
                    <select
                      id="inst"
                      value={planForm.institution_id}
                      onChange={(e) => setPlanForm({ ...planForm, institution_id: e.target.value })}
                      className="w-full border rounded px-3 py-2"
                    >
                      <option value="">Selecione</option>
                      {institutions.map((i) => (
                        <option key={i.id} value={i.id}>{i.name}</option>
                      ))}
                    </select>
                  </div>
                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="notes">Notas</label>
                    <textarea
                      id="notes"
                      value={planForm.notes}
                      onChange={(e) => setPlanForm({ ...planForm, notes: e.target.value })}
                      className="w-full border rounded px-3 py-2"
                      rows="2"
                    />
                  </div>
                  <div className="md:col-span-2 flex justify-end">
                    <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">Salvar Plano</button>
                  </div>
                </form>
              </div>

              <div className="bg-white rounded-lg shadow-md p-5">
                <h2 className="text-lg font-semibold text-gray-800 mb-4">Nova Projeção de Receita</h2>
                <form className="space-y-3" onSubmit={submitProjection}>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="desc">Descrição</label>
                    <input
                      id="desc"
                      type="text"
                      value={projectionForm.description}
                      onChange={(e) => setProjectionForm({ ...projectionForm, description: e.target.value })}
                      required
                      className="w-full border rounded px-3 py-2"
                    />
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="amount">Valor (R$)</label>
                      <input
                        id="amount"
                        type="number"
                        value={projectionForm.amount}
                        onChange={(e) => setProjectionForm({ ...projectionForm, amount: e.target.value })}
                        required
                        className="w-full border rounded px-3 py-2"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="date">Data esperada</label>
                      <input
                        id="date"
                        type="date"
                        value={projectionForm.expected_date}
                        onChange={(e) => setProjectionForm({ ...projectionForm, expected_date: e.target.value })}
                        required
                        className="w-full border rounded px-3 py-2"
                      />
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <label className="text-sm text-gray-700">Tipo:</label>
                    <select
                      value={projectionForm.projection_type}
                      onChange={(e) => setProjectionForm({ ...projectionForm, projection_type: e.target.value })}
                      className="border rounded px-3 py-2"
                    >
                      <option value="fixed">Fixa</option>
                      <option value="extra">Extra</option>
                    </select>
                    <label className="flex items-center gap-2 text-sm text-gray-700">
                      <input
                        type="checkbox"
                        checked={projectionForm.received}
                        onChange={(e) => setProjectionForm({ ...projectionForm, received: e.target.checked })}
                      />
                      Recebida
                    </label>
                  </div>
                  <div className="flex justify-end">
                    <button type="submit" className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700">Salvar Projeção</button>
                  </div>
                </form>
              </div>
            </section>

            <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div className="bg-white rounded-lg shadow-md p-5">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="text-lg font-semibold text-gray-800">Planos</h3>
                      <span className="text-xs text-gray-500">{plans.length} itens</span>
                    </div>
                    <ul className="divide-y divide-gray-100">
                      {plans.map((plan) => (
                        <li key={plan.id} className="py-3 flex flex-col gap-2">
                          <div className="flex items-start justify-between">
                            <div>
                              <p className="font-semibold text-gray-800">{plan.name}</p>
                              <p className="text-xs text-gray-500">
                                Meta {currency.format(plan.goal_amount)} · Aporte {currency.format(plan.monthly_contribution || 0)} · Progresso {plan.progress}%
                              </p>
                              <p className="text-xs text-gray-500">
                                Acumulado {currency.format(plan.current_balance || 0)} {plan.target_date ? `· Alvo ${plan.target_date}` : ''}
                              </p>
                            </div>
                            <div className="flex items-center gap-2">
                              <button
                                onClick={() => startEditPlan(plan)}
                                className="text-sm text-blue-600 hover:underline"
                              >
                                Editar
                              </button>
                              <button
                                onClick={() => concludePlan(plan)}
                                className="text-sm text-emerald-600 hover:underline"
                              >
                                Concluir
                              </button>
                              <button
                                onClick={() => deleteItem('plan', plan.id)}
                                className="text-sm text-red-600 hover:underline"
                              >
                                Remover
                              </button>
                            </div>
                          </div>
                          <div className="w-full bg-gray-100 rounded h-3 overflow-hidden">
                            <div
                              className="bg-blue-500 h-3"
                              style={{ width: `${Math.min(plan.progress || 0, 100)}%` }}
                            />
                          </div>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                        <div className="md:col-span-1">
                          <label className="block text-xs text-gray-600 mb-1">Aporte (R$)</label>
                          <input
                            type="number"
                            className="w-full border rounded px-3 py-2 text-sm"
                            value={planUpdates[plan.id]?.topUp || ''}
                            onChange={(e) =>
                              setPlanUpdates((prev) => ({
                                ...prev,
                                [plan.id]: { ...prev[plan.id], topUp: e.target.value }
                              }))
                            }
                            placeholder="Ex: 500"
                          />
                        </div>
                        <div className="md:col-span-1">
                          <label className="block text-xs text-gray-600 mb-1">Aporte mensal (R$)</label>
                          <input
                            type="number"
                            className="w-full border rounded px-3 py-2 text-sm"
                            value={planUpdates[plan.id]?.monthly || ''}
                            onChange={(e) =>
                              setPlanUpdates((prev) => ({
                                ...prev,
                                [plan.id]: { ...prev[plan.id], monthly: e.target.value }
                              }))
                            }
                            placeholder="Manter vazio para não alterar"
                          />
                        </div>
                        <div className="flex items-end">
                          <button
                            onClick={() => applyPlanUpdate(plan.id)}
                            className="w-full bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
                          >
                            Atualizar progresso
                          </button>
                        </div>
                      </div>
                    </li>
                  ))}
                  {plans.length === 0 && <li className="text-sm text-gray-500 py-3">Nenhum plano cadastrado.</li>}
                </ul>
              </div>

              <div className="bg-white rounded-lg shadow-md p-5">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-lg font-semibold text-gray-800">Projeções</h3>
                  <span className="text-xs text-gray-500">{projections.length} itens</span>
                </div>
                <ul className="divide-y divide-gray-100">
                  {projections.map((proj) => (
                    <li key={proj.id} className="py-3 flex items-center justify-between">
                      <div>
                        <p className="font-semibold text-gray-800">{proj.description}</p>
                        <p className="text-xs text-gray-500">
                          {currency.format(proj.amount)} · {proj.expected_date} · {proj.projection_type === 'fixed' ? 'Fixa' : 'Extra'}
                        </p>
                      </div>
                      <div className="flex items-center gap-3">
                        <label className="flex items-center gap-1 text-sm text-gray-700">
                          <input type="checkbox" checked={proj.received} onChange={() => toggleReceived(proj)} />
                          Recebida
                        </label>
                        <button
                          onClick={() => deleteItem('projection', proj.id)}
                          className="text-sm text-red-600 hover:underline"
                        >
                          Remover
                        </button>
                      </div>
                    </li>
                  ))}
                  {projections.length === 0 && <li className="text-sm text-gray-500 py-3">Nenhuma projeção cadastrada.</li>}
                </ul>
              </div>
            </section>

            <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white rounded-lg shadow-md p-5">
                <h2 className="text-lg font-semibold text-gray-800 mb-3">Linha do tempo de planos</h2>
                <ul className="divide-y divide-gray-100">
                  {timeline.map((plan) => (
                    <li key={plan.id} className="py-2 flex items-center justify-between">
                      <div>
                        <p className="font-semibold text-gray-800">{plan.name}</p>
                        <p className="text-xs text-gray-500">
                          Alvo: {plan.target_date || '—'} · Progresso {plan.progress}%
                        </p>
                      </div>
                      <span
                        className={`text-xs px-2 py-1 rounded ${
                          plan.is_active ? 'bg-blue-100 text-blue-700' : 'bg-gray-200 text-gray-700'
                        }`}
                      >
                        {plan.is_active ? 'Ativo' : 'Concluído'}
                      </span>
                    </li>
                  ))}
                  {timeline.length === 0 && <li className="py-2 text-sm text-gray-500">Nenhum plano.</li>}
                </ul>
              </div>
              <div className="bg-white rounded-lg shadow-md p-5">
                <h2 className="text-lg font-semibold text-gray-800 mb-3">Notas de planejamento</h2>
                <form className="mb-3" onSubmit={addNote}>
                  <textarea
                    value={noteContent}
                    onChange={(e) => setNoteContent(e.target.value)}
                    className="w-full border rounded px-3 py-2"
                    rows="2"
                    placeholder="Anotações sobre o planejamento..."
                  />
                  <div className="flex justify-end mt-2">
                    <button type="submit" className="bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700">
                      Salvar nota
                    </button>
                  </div>
                </form>
                <ul className="divide-y divide-gray-100">
                  {notesList.map((n) => (
                    <li key={n.id} className="py-2 flex items-start justify-between">
                      <div>
                        <p className="text-sm text-gray-800 whitespace-pre-wrap">{n.content}</p>
                        <p className="text-[11px] text-gray-500">{n.created_at}</p>
                      </div>
                      <button
                        onClick={() => removeNote(n.id)}
                        className="text-xs text-red-600 hover:underline"
                      >
                        Remover
                      </button>
                    </li>
                  ))}
                  {notesList.length === 0 && <li className="py-2 text-sm text-gray-500">Nenhuma nota.</li>}
                </ul>
              </div>
              <div className="bg-white rounded-lg shadow-md p-5">
                <h2 className="text-lg font-semibold text-gray-800 mb-3">Recorrência por categoria</h2>
                <form className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-4" onSubmit={createRecurring}>
                  <div className="md:col-span-2">
                    <label className="block text-sm text-gray-700 mb-1">Categoria</label>
                    <select
                      value={recurringForm.category_id}
                      onChange={(e) => setRecurringForm({ ...recurringForm, category_id: e.target.value })}
                      required
                      className="w-full border rounded px-3 py-2"
                    >
                      <option value="">Selecione</option>
                      {categories.map((c) => (
                        <option key={c.id} value={c.id}>
                          {c.name} ({c.type === 'expense' ? 'Despesa' : 'Receita'})
                        </option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm text-gray-700 mb-1">Valor (mês)</label>
                    <input
                      type="number"
                      value={recurringForm.amount}
                      onChange={(e) => setRecurringForm({ ...recurringForm, amount: e.target.value })}
                      className="w-full border rounded px-3 py-2"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-700 mb-1">Data início</label>
                    <input
                      type="date"
                      value={recurringForm.start_date}
                      onChange={(e) => setRecurringForm({ ...recurringForm, start_date: e.target.value })}
                      className="w-full border rounded px-3 py-2"
                      required
                    />
                  </div>
                  <div className="md:col-span-2">
                    <label className="block text-sm text-gray-700 mb-1">Data fim (opcional)</label>
                    <input
                      type="date"
                      value={recurringForm.end_date}
                      onChange={(e) => setRecurringForm({ ...recurringForm, end_date: e.target.value })}
                      className="w-full border rounded px-3 py-2"
                    />
                  </div>
                  <div className="md:col-span-2 flex justify-end">
                    <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">Salvar recorrência</button>
                  </div>
                </form>
                <ul className="divide-y divide-gray-100">
                  {recurringList.map((r) => (
                    <li key={r.id} className="py-2 flex items-center justify-between">
                      <div>
                        <p className="font-semibold text-gray-800">
                          {categories.find((c) => c.id === r.category_id)?.name || `Categoria #${r.category_id}`}
                        </p>
                        <p className="text-xs text-gray-500">
                          {currency.format(r.amount)} · {r.start_date} até {r.end_date || 'indefinido'}
                        </p>
                      </div>
                      <button
                        onClick={() => deleteRecurring(r.id)}
                        className="text-xs text-red-600 hover:underline"
                      >
                        Remover
                      </button>
                    </li>
                  ))}
                  {recurringList.length === 0 && <li className="py-2 text-sm text-gray-500">Nenhuma recorrência.</li>}
                </ul>
              </div>
            </section>
          </>
        )}
      </main>
    </div>
  )
}
