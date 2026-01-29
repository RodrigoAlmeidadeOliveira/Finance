import { useState, useEffect } from 'react'
import { transactions, catalog } from '../api/client'

export default function TransactionForm({ transaction, onClose, onSaved }) {
  const isEdit = !!transaction

  const [formData, setFormData] = useState({
    event_date: transaction?.event_date?.split('T')[0] || new Date().toISOString().split('T')[0],
    event_time: transaction?.event_date?.split('T')[1]?.substring(0, 5) || '12:00',
    effective_date: transaction?.effective_date?.split('T')[0] || '',
    transaction_type: transaction?.transaction_type || 'EXPENSE',
    category_id: transaction?.category_id || '',
    institution_id: transaction?.institution_id || '',
    credit_card_id: transaction?.credit_card_id || '',
    amount: transaction?.amount || '',
    description: transaction?.description || '',
    notes: transaction?.notes || '',
    status: transaction?.status || 'PENDING',
    is_recurring: transaction?.is_recurring || false
  })

  const [categories, setCategories] = useState([])
  const [institutions, setInstitutions] = useState([])
  const [creditCards, setCreditCards] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    loadCatalogs()
  }, [])

  const loadCatalogs = async () => {
    try {
      const [catResp, instResp, ccResp] = await Promise.all([
        catalog.listCategories(),
        catalog.listInstitutions(),
        catalog.listCreditCards()
      ])

      setCategories(catResp.data.items || [])
      setInstitutions(instResp.data.items || [])
      setCreditCards(ccResp.data.items || [])
    } catch (err) {
      console.error('Erro ao carregar catálogos:', err)
      setError('Erro ao carregar categorias e instituições')
    }
  }

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      // Combine date and time
      const eventDateTime = `${formData.event_date}T${formData.event_time}:00`
      const effectiveDateTime = formData.effective_date
        ? `${formData.effective_date}T${formData.event_time}:00`
        : null

      const payload = {
        event_date: eventDateTime,
        effective_date: effectiveDateTime,
        transaction_type: formData.transaction_type,
        category_id: parseInt(formData.category_id),
        amount: parseFloat(formData.amount),
        description: formData.description,
        notes: formData.notes || null,
        institution_id: formData.institution_id ? parseInt(formData.institution_id) : null,
        credit_card_id: formData.credit_card_id ? parseInt(formData.credit_card_id) : null,
        status: formData.status,
        is_recurring: formData.is_recurring
      }

      if (isEdit) {
        await transactions.update(transaction.id, payload)
      } else {
        await transactions.create(payload)
      }

      onSaved()
      onClose()
    } catch (err) {
      console.error('Erro ao salvar transação:', err)
      setError(err.response?.data?.error || 'Erro ao salvar transação')
    } finally {
      setLoading(false)
    }
  }

  // Filter categories by type
  const filteredCategories = categories.filter(
    cat => cat.type === formData.transaction_type.toLowerCase()
  )

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white border-b px-6 py-4 flex justify-between items-center">
          <h2 className="text-2xl font-bold text-gray-800">
            {isEdit ? '✏️ Editar Transação' : '➕ Nova Transação'}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl"
          >
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          {/* Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Tipo *
            </label>
            <div className="grid grid-cols-2 gap-4">
              <button
                type="button"
                onClick={() => setFormData(prev => ({ ...prev, transaction_type: 'INCOME', category_id: '' }))}
                className={`px-4 py-3 border-2 rounded-lg font-medium transition ${
                  formData.transaction_type === 'INCOME'
                    ? 'border-green-500 bg-green-50 text-green-700'
                    : 'border-gray-300 text-gray-600 hover:border-green-300'
                }`}
              >
                💰 Receita
              </button>
              <button
                type="button"
                onClick={() => setFormData(prev => ({ ...prev, transaction_type: 'EXPENSE', category_id: '' }))}
                className={`px-4 py-3 border-2 rounded-lg font-medium transition ${
                  formData.transaction_type === 'EXPENSE'
                    ? 'border-red-500 bg-red-50 text-red-700'
                    : 'border-gray-300 text-gray-600 hover:border-red-300'
                }`}
              >
                💸 Despesa
              </button>
            </div>
          </div>

          {/* Date and Time */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Data do Evento *
              </label>
              <input
                type="date"
                name="event_date"
                value={formData.event_date}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Hora
              </label>
              <input
                type="time"
                name="event_time"
                value={formData.event_time}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          {/* Effective Date */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Data de Efetivação (opcional)
            </label>
            <input
              type="date"
              name="effective_date"
              value={formData.effective_date}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p className="text-xs text-gray-500 mt-1">
              Quando o dinheiro entra/sai da conta. Deixe em branco para usar a data do evento.
            </p>
          </div>

          {/* Category */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Categoria *
            </label>
            <select
              name="category_id"
              value={formData.category_id}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Selecione uma categoria</option>
              {filteredCategories.map(cat => (
                <option key={cat.id} value={cat.id}>
                  {cat.name}
                </option>
              ))}
            </select>
          </div>

          {/* Amount */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Valor (R$) *
            </label>
            <input
              type="number"
              name="amount"
              value={formData.amount}
              onChange={handleChange}
              required
              min="0.01"
              step="0.01"
              placeholder="0.00"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Descrição *
            </label>
            <input
              type="text"
              name="description"
              value={formData.description}
              onChange={handleChange}
              required
              maxLength="500"
              placeholder="Ex: Compras no supermercado"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Institution and Credit Card */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Instituição (opcional)
              </label>
              <select
                name="institution_id"
                value={formData.institution_id}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Nenhuma</option>
                {institutions.map(inst => (
                  <option key={inst.id} value={inst.id}>
                    {inst.name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Cartão de Crédito (opcional)
              </label>
              <select
                name="credit_card_id"
                value={formData.credit_card_id}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Nenhum</option>
                {creditCards.map(cc => (
                  <option key={cc.id} value={cc.id}>
                    {cc.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Notes */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Observações (opcional)
            </label>
            <textarea
              name="notes"
              value={formData.notes}
              onChange={handleChange}
              rows="3"
              placeholder="Anotações adicionais..."
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Status */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Status
            </label>
            <div className="grid grid-cols-2 gap-4">
              <button
                type="button"
                onClick={() => setFormData(prev => ({ ...prev, status: 'PENDING' }))}
                className={`px-4 py-2 border-2 rounded-lg font-medium transition ${
                  formData.status === 'PENDING'
                    ? 'border-yellow-500 bg-yellow-50 text-yellow-700'
                    : 'border-gray-300 text-gray-600 hover:border-yellow-300'
                }`}
              >
                ⏳ Pendente
              </button>
              <button
                type="button"
                onClick={() => setFormData(prev => ({ ...prev, status: 'COMPLETED' }))}
                className={`px-4 py-2 border-2 rounded-lg font-medium transition ${
                  formData.status === 'COMPLETED'
                    ? 'border-green-500 bg-green-50 text-green-700'
                    : 'border-gray-300 text-gray-600 hover:border-green-300'
                }`}
              >
                ✅ Concluída
              </button>
            </div>
          </div>

          {/* Recurring */}
          <div className="flex items-center">
            <input
              type="checkbox"
              name="is_recurring"
              checked={formData.is_recurring}
              onChange={handleChange}
              className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <label className="ml-2 text-sm text-gray-700">
              Transação recorrente
            </label>
          </div>

          {/* Buttons */}
          <div className="flex justify-end gap-3 pt-4 border-t">
            <button
              type="button"
              onClick={onClose}
              className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Salvando...' : isEdit ? 'Atualizar' : 'Criar'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
