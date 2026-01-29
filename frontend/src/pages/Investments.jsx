import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { investments, catalog } from '../api/client'

const currency = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' })

const emptyForm = {
  name: '',
  institution_id: '',
  investment_type_id: '',
  classification: '',
  amount_invested: '',
  current_value: '',
  applied_at: '',
  maturity_date: '',
  profitability_rate: '',
  notes: ''
}

export default function Investments() {
  const navigate = useNavigate()
  const [items, setItems] = useState([])
  const [summary, setSummary] = useState(null)
  const [performance, setPerformance] = useState([])
  const [insts, setInsts] = useState([])
  const [types, setTypes] = useState([])
  const [form, setForm] = useState(emptyForm)
  const [divForms, setDivForms] = useState({})
  const [redeemForms, setRedeemForms] = useState({})
  const [loading, setLoading] = useState(true)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    loadAll()
  }, [])

  const loadAll = async () => {
    try {
      setLoading(true)
      const [invResp, sumResp, perfResp, instResp, typeResp] = await Promise.all([
        investments.list({ include_inactive: true }),
        investments.summary(),
        investments.performance(),
        catalog.listInstitutions({ include_inactive: true }),
        catalog.listInvestmentTypes()
      ])
      setItems(invResp.data.items || [])
      setSummary(sumResp.data || null)
      setPerformance(perfResp.data.items || [])
      setInsts(instResp.data.items || [])
      setTypes(typeResp.data.items || [])
    } catch (err) {
      setError(err.response?.data?.error || 'Erro ao carregar investimentos.')
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

  const submitInvestment = async (e) => {
    e.preventDefault()
    try {
      await investments.create({
        ...form,
        institution_id: form.institution_id ? Number(form.institution_id) : null,
        investment_type_id: form.investment_type_id ? Number(form.investment_type_id) : null,
        amount_invested: Number(form.amount_invested || 0),
        current_value: form.current_value ? Number(form.current_value) : undefined,
        profitability_rate: form.profitability_rate ? Number(form.profitability_rate) : undefined
      })
      setForm(emptyForm)
      handleMessage('Investimento criado.')
      loadAll()
    } catch (err) {
      handleError(err.response?.data?.error || 'Erro ao criar investimento.')
    }
  }

  const removeInvestment = async (id) => {
    try {
      await investments.remove(id)
      handleMessage('Investimento removido.')
      loadAll()
    } catch (err) {
      handleError('Erro ao remover investimento.')
    }
  }

  const submitDividend = async (invId) => {
    const data = divForms[invId] || {}
    const amount = Number(data.amount || 0)
    if (!amount) {
      handleError('Informe um valor de provento.')
      return
    }
    try {
      await investments.addDividend(invId, {
        amount,
        description: data.description || '',
        received_at: data.received_at || null
      })
      setDivForms((prev) => ({ ...prev, [invId]: { amount: '', description: '', received_at: '' } }))
      handleMessage('Provento registrado.')
      loadAll()
    } catch (err) {
      handleError(err.response?.data?.error || 'Erro ao registrar provento.')
    }
  }

  const redeemInvestment = async (invId, closePosition = false) => {
    const data = redeemForms[invId] || {}
    const amount = data.amount ? Number(data.amount) : undefined
    try {
      await investments.redeem(invId, { amount, close_position: closePosition })
      setRedeemForms((prev) => ({ ...prev, [invId]: { amount: '' } }))
      handleMessage(closePosition ? 'Resgate total realizado.' : 'Resgate registrado.')
      loadAll()
    } catch (err) {
      handleError(err.response?.data?.error || 'Erro ao resgatar.')
    }
  }

  const formattedGain = useMemo(() => {
    if (!summary) return null
    return {
      invested: currency.format(summary.total_invested || 0),
      current: currency.format(summary.total_current || 0),
      gain: currency.format(summary.total_gain || 0)
    }
  }, [summary])

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <span className="text-3xl">📈</span>
            <div>
              <h1 className="text-xl font-bold text-gray-800">Investimentos</h1>
              <p className="text-xs text-gray-500">Carteira, proventos e rentabilidade</p>
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
            <p className="mt-4 text-gray-600">Carregando carteira...</p>
          </div>
        ) : (
          <>
            <section className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-white p-4 rounded-lg shadow border-l-4 border-blue-500">
                <p className="text-xs text-gray-500">Investido</p>
                <p className="text-2xl font-bold text-gray-800">{formattedGain?.invested || currency.format(0)}</p>
              </div>
              <div className="bg-white p-4 rounded-lg shadow border-l-4 border-green-500">
                <p className="text-xs text-gray-500">Valor atual</p>
                <p className="text-2xl font-bold text-gray-800">{formattedGain?.current || currency.format(0)}</p>
              </div>
              <div className="bg-white p-4 rounded-lg shadow border-l-4 border-amber-500">
                <p className="text-xs text-gray-500">Ganho</p>
                <p className="text-2xl font-bold text-gray-800">{formattedGain?.gain || currency.format(0)}</p>
              </div>
            </section>

            <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white rounded-lg shadow-md p-5">
                <h2 className="text-lg font-semibold text-gray-800 mb-4">Novo investimento</h2>
                <form className="grid grid-cols-1 md:grid-cols-2 gap-3" onSubmit={submitInvestment}>
                  <div className="md:col-span-2">
                    <label className="block text-sm text-gray-700 mb-1" htmlFor="inv-name">Nome</label>
                    <input
                      id="inv-name"
                      value={form.name}
                      onChange={(e) => setForm({ ...form, name: e.target.value })}
                      required
                      className="w-full border rounded px-3 py-2"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-700 mb-1" htmlFor="inv-inst">Instituição</label>
                    <select
                      id="inv-inst"
                      value={form.institution_id}
                      onChange={(e) => setForm({ ...form, institution_id: e.target.value })}
                      className="w-full border rounded px-3 py-2"
                    >
                      <option value="">Selecione</option>
                      {insts.map((i) => (
                        <option key={i.id} value={i.id}>{i.name}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm text-gray-700 mb-1" htmlFor="inv-type">Tipo</label>
                    <select
                      id="inv-type"
                      value={form.investment_type_id}
                      onChange={(e) => setForm({ ...form, investment_type_id: e.target.value })}
                      className="w-full border rounded px-3 py-2"
                    >
                      <option value="">Selecione</option>
                      {types.map((t) => (
                        <option key={t.id} value={t.id}>{t.name}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm text-gray-700 mb-1" htmlFor="inv-class">Classificação</label>
                    <select
                      id="inv-class"
                      value={form.classification}
                      onChange={(e) => setForm({ ...form, classification: e.target.value })}
                      className="w-full border rounded px-3 py-2"
                    >
                      <option value="">Selecione</option>
                      <option value="renda_fixa">Renda Fixa</option>
                      <option value="renda_variavel">Renda Variável</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm text-gray-700 mb-1" htmlFor="inv-amount">Aplicado (R$)</label>
                    <input
                      id="inv-amount"
                      type="number"
                      value={form.amount_invested}
                      onChange={(e) => setForm({ ...form, amount_invested: e.target.value })}
                      required
                      className="w-full border rounded px-3 py-2"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-700 mb-1" htmlFor="inv-current">Valor atual (R$)</label>
                    <input
                      id="inv-current"
                      type="number"
                      value={form.current_value}
                      onChange={(e) => setForm({ ...form, current_value: e.target.value })}
                      className="w-full border rounded px-3 py-2"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-700 mb-1" htmlFor="inv-applied">Data aplicação</label>
                    <input
                      id="inv-applied"
                      type="date"
                      value={form.applied_at}
                      onChange={(e) => setForm({ ...form, applied_at: e.target.value })}
                      className="w-full border rounded px-3 py-2"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-700 mb-1" htmlFor="inv-maturity">Vencimento</label>
                    <input
                      id="inv-maturity"
                      type="date"
                      value={form.maturity_date}
                      onChange={(e) => setForm({ ...form, maturity_date: e.target.value })}
                      className="w-full border rounded px-3 py-2"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-700 mb-1" htmlFor="inv-rate">Taxa (% a.a)</label>
                    <input
                      id="inv-rate"
                      type="number"
                      value={form.profitability_rate}
                      onChange={(e) => setForm({ ...form, profitability_rate: e.target.value })}
                      className="w-full border rounded px-3 py-2"
                    />
                  </div>
                  <div className="md:col-span-2">
                    <label className="block text-sm text-gray-700 mb-1" htmlFor="inv-notes">Notas</label>
                    <textarea
                      id="inv-notes"
                      value={form.notes}
                      onChange={(e) => setForm({ ...form, notes: e.target.value })}
                      className="w-full border rounded px-3 py-2"
                      rows="2"
                    />
                  </div>
                  <div className="md:col-span-2 flex justify-end">
                    <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">Salvar investimento</button>
                  </div>
                </form>
              </div>

              <div className="bg-white rounded-lg shadow-md p-5">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-lg font-semibold text-gray-800">Carteira</h3>
                  <span className="text-xs text-gray-500">{items.length} itens</span>
                </div>
                <div className="divide-y divide-gray-100">
                  {items.map((inv) => {
                    const perf = performance.find((p) => p.id === inv.id)
                    return (
                    <div key={inv.id} className="py-3 space-y-2">
                      <div className="flex items-start justify-between">
                        <div>
                          <p className="font-semibold text-gray-800">{inv.name}</p>
                          <p className="text-xs text-gray-500">
                            {inv.classification || '–'} · Aplicado {currency.format(inv.amount_invested || 0)} · Atual {currency.format(inv.current_value || 0)}
                            {perf ? ` · ROI ${perf.roi}% · Ganho ${currency.format(perf.gain)}` : ''}
                          </p>
                        </div>
                        <button
                          onClick={() => removeInvestment(inv.id)}
                          className="text-sm text-red-600 hover:underline"
                        >
                          Remover
                        </button>
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                        <div>
                          <label className="block text-xs text-gray-600 mb-1">Resgate (R$)</label>
                          <input
                            type="number"
                            className="w-full border rounded px-3 py-2 text-sm"
                            value={redeemForms[inv.id]?.amount || ''}
                            onChange={(e) =>
                              setRedeemForms((prev) => ({
                                ...prev,
                                [inv.id]: { amount: e.target.value }
                              }))
                            }
                            placeholder="Parcial"
                          />
                        </div>
                        <div className="flex items-end gap-2">
                          <button
                            onClick={() => redeemInvestment(inv.id, false)}
                            className="w-full bg-gray-200 text-gray-800 px-3 py-2 rounded hover:bg-gray-300 text-sm"
                          >
                            Resgatar parcial
                          </button>
                          <button
                            onClick={() => redeemInvestment(inv.id, true)}
                            className="w-full bg-red-600 text-white px-3 py-2 rounded hover:bg-red-700 text-sm"
                          >
                            Resgate total
                          </button>
                        </div>
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                        <div>
                          <label className="block text-xs text-gray-600 mb-1">Provento (R$)</label>
                          <input
                            type="number"
                            className="w-full border rounded px-3 py-2 text-sm"
                            value={divForms[inv.id]?.amount || ''}
                            onChange={(e) =>
                              setDivForms((prev) => ({
                                ...prev,
                                [inv.id]: { ...prev[inv.id], amount: e.target.value }
                              }))
                            }
                          />
                        </div>
                        <div>
                          <label className="block text-xs text-gray-600 mb-1">Data</label>
                          <input
                            type="date"
                            className="w-full border rounded px-3 py-2 text-sm"
                            value={divForms[inv.id]?.received_at || ''}
                            onChange={(e) =>
                              setDivForms((prev) => ({
                                ...prev,
                                [inv.id]: { ...prev[inv.id], received_at: e.target.value }
                              }))
                            }
                          />
                        </div>
                        <div>
                          <label className="block text-xs text-gray-600 mb-1">Descrição</label>
                          <input
                            type="text"
                            className="w-full border rounded px-3 py-2 text-sm"
                            value={divForms[inv.id]?.description || ''}
                            onChange={(e) =>
                              setDivForms((prev) => ({
                                ...prev,
                                [inv.id]: { ...prev[inv.id], description: e.target.value }
                              }))
                            }
                            placeholder="ex: Dividendo"
                          />
                        </div>
                      </div>
                      <div className="flex justify-end">
                        <button
                          onClick={() => submitDividend(inv.id)}
                          className="bg-emerald-600 text-white px-3 py-1 rounded hover:bg-emerald-700 text-sm"
                        >
                          Registrar provento
                        </button>
                      </div>
                    </div>
                    )
                  })}
                  {items.length === 0 && <p className="text-sm text-gray-500 py-3">Nenhum investimento cadastrado.</p>}
                </div>
              </div>
            </section>
          </>
        )}
      </main>
    </div>
  )
}
