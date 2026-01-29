import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { catalog } from '../api/client'

const initialCategoryForm = { name: '', type: 'expense', parent_id: '', color: '' }
const initialInstitutionForm = { name: '', account_type: 'corrente', partition: '', initial_balance: '' }
const initialCardForm = { name: '', institution_id: '', brand: '', closing_day: '', due_day: '', limit_amount: '' }
const initialInvestmentForm = { name: '', classification: '', description: '' }

export default function Catalogs() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [categories, setCategories] = useState([])
  const [institutions, setInstitutions] = useState([])
  const [cards, setCards] = useState([])
  const [investmentTypes, setInvestmentTypes] = useState([])
  const [catForm, setCatForm] = useState(initialCategoryForm)
  const [instForm, setInstForm] = useState(initialInstitutionForm)
  const [cardForm, setCardForm] = useState(initialCardForm)
  const [invForm, setInvForm] = useState(initialInvestmentForm)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  useEffect(() => {
    loadAll()
  }, [])

  const incomeCategories = useMemo(
    () => categories.filter(c => c.type === 'income'),
    [categories]
  )
  const expenseCategories = useMemo(
    () => categories.filter(c => c.type === 'expense'),
    [categories]
  )

  const loadAll = async () => {
    try {
      setLoading(true)
      const [cats, insts, cardsResp, invTypes] = await Promise.all([
        catalog.listCategories({ include_inactive: true }),
        catalog.listInstitutions({ include_inactive: true }),
        catalog.listCreditCards({ include_inactive: true }),
        catalog.listInvestmentTypes()
      ])
      setCategories(cats.data.items || [])
      setInstitutions(insts.data.items || [])
      setCards(cardsResp.data.items || [])
      setInvestmentTypes(invTypes.data.items || [])
    } catch (err) {
      setError(err.response?.data?.error || 'Erro ao carregar cadastros.')
    } finally {
      setLoading(false)
    }
  }

  const handleMessage = (text) => {
    setMessage(text)
    setTimeout(() => setMessage(''), 4000)
  }

  const handleError = (text) => {
    setError(text)
    setTimeout(() => setError(''), 5000)
  }

  const submitCategory = async (e) => {
    e.preventDefault()
    try {
      await catalog.createCategory({
        name: catForm.name,
        type: catForm.type,
        parent_id: catForm.parent_id ? Number(catForm.parent_id) : null,
        color: catForm.color || null
      })
      handleMessage('Categoria criada.')
      setCatForm(initialCategoryForm)
      loadAll()
    } catch (err) {
      handleError(err.response?.data?.error || 'Erro ao criar categoria.')
    }
  }

  const submitInstitution = async (e) => {
    e.preventDefault()
    try {
      await catalog.createInstitution({
        name: instForm.name,
        account_type: instForm.account_type,
        partition: instForm.partition || null,
        initial_balance: instForm.initial_balance ? Number(instForm.initial_balance) : 0
      })
      handleMessage('Instituição criada.')
      setInstForm(initialInstitutionForm)
      loadAll()
    } catch (err) {
      handleError(err.response?.data?.error || 'Erro ao criar instituição.')
    }
  }

  const submitCard = async (e) => {
    e.preventDefault()
    try {
      await catalog.createCreditCard({
        name: cardForm.name,
        institution_id: Number(cardForm.institution_id),
        brand: cardForm.brand || null,
        closing_day: cardForm.closing_day ? Number(cardForm.closing_day) : null,
        due_day: cardForm.due_day ? Number(cardForm.due_day) : null,
        limit_amount: cardForm.limit_amount ? Number(cardForm.limit_amount) : null
      })
      handleMessage('Cartão criado.')
      setCardForm(initialCardForm)
      loadAll()
    } catch (err) {
      handleError(err.response?.data?.error || 'Erro ao criar cartão.')
    }
  }

  const submitInvestment = async (e) => {
    e.preventDefault()
    try {
      await catalog.createInvestmentType({
        name: invForm.name,
        classification: invForm.classification || null,
        description: invForm.description || null
      })
      handleMessage('Tipo de investimento criado.')
      setInvForm(initialInvestmentForm)
      loadAll()
    } catch (err) {
      handleError(err.response?.data?.error || 'Erro ao criar tipo.')
    }
  }

  const deleteItem = async (type, id) => {
    try {
      if (type === 'category') await catalog.deleteCategory(id)
      if (type === 'institution') await catalog.deleteInstitution(id)
      if (type === 'card') await catalog.deleteCreditCard(id)
      if (type === 'investment') await catalog.deleteInvestmentType(id)
      handleMessage('Registro removido.')
      loadAll()
    } catch (err) {
      handleError(err.response?.data?.error || 'Erro ao remover.')
    }
  }

  const renderCategoryList = (items, title) => (
    <div className="bg-white rounded-lg shadow-md p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-lg font-semibold text-gray-800">{title}</h3>
        <span className="text-xs text-gray-500">{items.length} itens</span>
      </div>
      <ul className="divide-y divide-gray-100">
        {items.map((cat) => (
          <li key={cat.id} className="py-2 flex items-center justify-between">
            <div>
              <p className="font-medium text-gray-800">{cat.name}</p>
              {cat.parent_id && (
                <p className="text-xs text-gray-500">Sub de #{cat.parent_id}</p>
              )}
            </div>
            <button
              onClick={() => deleteItem('category', cat.id)}
              className="text-sm text-red-600 hover:underline"
            >
              Remover
            </button>
          </li>
        ))}
        {items.length === 0 && (
          <li className="text-sm text-gray-500 py-2">Nenhum registro</li>
        )}
      </ul>
    </div>
  )

  const renderSimpleList = (items, type) => (
    <ul className="divide-y divide-gray-100">
      {items.map((item) => (
        <li key={item.id} className="py-2 flex items-center justify-between">
          <div>
            <p className="font-medium text-gray-800">{item.name}</p>
            {type === 'institution' && (
              <p className="text-xs text-gray-500">
                {item.account_type} · Saldo {item.current_balance ?? item.initial_balance}
              </p>
            )}
            {type === 'card' && (
              <p className="text-xs text-gray-500">
                {item.brand || '—'} · Fechamento {item.closing_day || '-'}
              </p>
            )}
            {type === 'investment' && (
              <p className="text-xs text-gray-500">
                {item.classification || '—'} {item.description ? `· ${item.description}` : ''}
              </p>
            )}
          </div>
          <button
            onClick={() => deleteItem(type, item.id)}
            className="text-sm text-red-600 hover:underline"
          >
            Remover
          </button>
        </li>
      ))}
      {items.length === 0 && (
        <li className="text-sm text-gray-500 py-2">Nenhum registro</li>
      )}
    </ul>
  )

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <span className="text-3xl">🗂️</span>
            <div>
              <h1 className="text-xl font-bold text-gray-800">Cadastros Base</h1>
              <p className="text-xs text-gray-500">Categorias, Instituições, Cartões, Tipos</p>
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
        {message && (
          <div className="bg-green-100 text-green-800 px-4 py-2 rounded border border-green-200">
            {message}
          </div>
        )}
        {error && (
          <div className="bg-red-100 text-red-800 px-4 py-2 rounded border border-red-200">
            {error}
          </div>
        )}

        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            <p className="mt-4 text-gray-600">Carregando cadastros...</p>
          </div>
        ) : (
          <div className="space-y-8">
            <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-1 bg-white rounded-lg shadow-md p-5">
                <h2 className="text-lg font-semibold text-gray-800 mb-4">Nova Categoria</h2>
                <form className="space-y-3" onSubmit={submitCategory}>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="cat-name">Nome</label>
                    <input
                      id="cat-name"
                      value={catForm.name}
                      onChange={(e) => setCatForm({ ...catForm, name: e.target.value })}
                      className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                      required
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="cat-type">Tipo</label>
                      <select
                        id="cat-type"
                        value={catForm.type}
                        onChange={(e) => setCatForm({ ...catForm, type: e.target.value })}
                        className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="expense">Despesa</option>
                        <option value="income">Receita</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="cat-color">Cor</label>
                      <input
                        id="cat-color"
                        value={catForm.color}
                        onChange={(e) => setCatForm({ ...catForm, color: e.target.value })}
                        placeholder="#ffaa00"
                        className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="cat-parent">Categoria Pai (opcional)</label>
                    <select
                      id="cat-parent"
                      value={catForm.parent_id}
                      onChange={(e) => setCatForm({ ...catForm, parent_id: e.target.value })}
                      className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">Sem pai</option>
                      {categories
                        .filter(c => c.parent_id === null)
                        .filter(c => c.type === catForm.type)
                        .map(cat => (
                          <option key={cat.id} value={cat.id}>{cat.name}</option>
                        ))}
                    </select>
                  </div>
                  <button
                    type="submit"
                    className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition"
                  >
                    Salvar Categoria
                  </button>
                </form>
              </div>
              <div className="lg:col-span-2 grid grid-cols-1 md:grid-cols-2 gap-4">
                {renderCategoryList(expenseCategories, 'Categorias de Despesa')}
                {renderCategoryList(incomeCategories, 'Categorias de Receita')}
              </div>
            </section>

            <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="bg-white rounded-lg shadow-md p-5">
                <h2 className="text-lg font-semibold text-gray-800 mb-4">Nova Instituição</h2>
                <form className="space-y-3" onSubmit={submitInstitution}>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="inst-name">Nome</label>
                    <input
                      id="inst-name"
                      value={instForm.name}
                      onChange={(e) => setInstForm({ ...instForm, name: e.target.value })}
                      required
                      className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="inst-account-type">Tipo de conta</label>
                    <input
                      id="inst-account-type"
                      value={instForm.account_type}
                      onChange={(e) => setInstForm({ ...instForm, account_type: e.target.value })}
                      required
                      className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="inst-partition">Partição</label>
                      <input
                        id="inst-partition"
                        value={instForm.partition}
                        onChange={(e) => setInstForm({ ...instForm, partition: e.target.value })}
                        className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="inst-balance">Saldo inicial</label>
                      <input
                        id="inst-balance"
                        type="number"
                        value={instForm.initial_balance}
                        onChange={(e) => setInstForm({ ...instForm, initial_balance: e.target.value })}
                        className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                  </div>
                  <button
                    type="submit"
                    className="w-full bg-green-600 text-white py-2 rounded-lg hover:bg-green-700 transition"
                  >
                    Salvar Instituição
                  </button>
                </form>
              </div>
              <div className="lg:col-span-2 bg-white rounded-lg shadow-md p-5">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-lg font-semibold text-gray-800">Instituições</h3>
                  <span className="text-xs text-gray-500">{institutions.length} itens</span>
                </div>
                {renderSimpleList(institutions, 'institution')}
              </div>
            </section>

            <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="bg-white rounded-lg shadow-md p-5">
                <h2 className="text-lg font-semibold text-gray-800 mb-4">Novo Cartão</h2>
                <form className="space-y-3" onSubmit={submitCard}>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="card-name">Nome</label>
                    <input
                      id="card-name"
                      value={cardForm.name}
                      onChange={(e) => setCardForm({ ...cardForm, name: e.target.value })}
                      required
                      className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="card-institution">Instituição</label>
                    <select
                      id="card-institution"
                      value={cardForm.institution_id}
                      onChange={(e) => setCardForm({ ...cardForm, institution_id: e.target.value })}
                      required
                      className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">Selecione</option>
                      {institutions.map(inst => (
                        <option key={inst.id} value={inst.id}>{inst.name}</option>
                      ))}
                    </select>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="card-closing">Fechamento</label>
                      <input
                        id="card-closing"
                        type="number"
                        value={cardForm.closing_day}
                        onChange={(e) => setCardForm({ ...cardForm, closing_day: e.target.value })}
                        className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="card-due">Vencimento</label>
                      <input
                        id="card-due"
                        type="number"
                        value={cardForm.due_day}
                        onChange={(e) => setCardForm({ ...cardForm, due_day: e.target.value })}
                        className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="card-limit">Limite</label>
                    <input
                      id="card-limit"
                      type="number"
                      value={cardForm.limit_amount}
                      onChange={(e) => setCardForm({ ...cardForm, limit_amount: e.target.value })}
                      className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <button
                    type="submit"
                    className="w-full bg-purple-600 text-white py-2 rounded-lg hover:bg-purple-700 transition"
                  >
                    Salvar Cartão
                  </button>
                </form>
              </div>
              <div className="lg:col-span-2 bg-white rounded-lg shadow-md p-5">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-lg font-semibold text-gray-800">Cartões</h3>
                  <span className="text-xs text-gray-500">{cards.length} itens</span>
                </div>
                {renderSimpleList(cards, 'card')}
              </div>
            </section>

            <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="bg-white rounded-lg shadow-md p-5">
                <h2 className="text-lg font-semibold text-gray-800 mb-4">Novo Tipo de Investimento</h2>
                <form className="space-y-3" onSubmit={submitInvestment}>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="inv-name">Nome</label>
                    <input
                      id="inv-name"
                      value={invForm.name}
                      onChange={(e) => setInvForm({ ...invForm, name: e.target.value })}
                      required
                      className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="inv-classification">Classificação</label>
                    <input
                      id="inv-classification"
                      value={invForm.classification}
                      onChange={(e) => setInvForm({ ...invForm, classification: e.target.value })}
                      className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                      placeholder="renda_fixa, renda_variavel..."
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="inv-description">Descrição</label>
                    <textarea
                      id="inv-description"
                      value={invForm.description}
                      onChange={(e) => setInvForm({ ...invForm, description: e.target.value })}
                      className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                      rows="2"
                    />
                  </div>
                  <button
                    type="submit"
                    className="w-full bg-amber-600 text-white py-2 rounded-lg hover:bg-amber-700 transition"
                  >
                    Salvar Tipo
                  </button>
                </form>
              </div>
              <div className="lg:col-span-2 bg-white rounded-lg shadow-md p-5">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-lg font-semibold text-gray-800">Tipos de Investimento</h3>
                  <span className="text-xs text-gray-500">{investmentTypes.length} itens</span>
                </div>
                {renderSimpleList(investmentTypes, 'investment')}
              </div>
            </section>
          </div>
        )}
      </main>
    </div>
  )
}
