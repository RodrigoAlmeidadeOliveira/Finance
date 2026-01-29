import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api'

const client = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Interceptor para adicionar token JWT
client.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Interceptor para tratar erros de autenticação
client.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      // Token expirado ou inválido
      localStorage.clear()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const auth = {
  login: (email, password) =>
    client.post('/auth/login', { email, password }),

  devLogin: () => client.get('/auth/dev-login'),

  register: (email, password, full_name) =>
    client.post('/auth/register', { email, password, full_name }),

  me: () => client.get('/auth/me'),

  logout: () => client.post('/auth/logout'),

  refresh: (refresh_token) =>
    client.post('/auth/refresh', { refresh_token }),

  changePassword: (current_password, new_password, confirm_password) =>
    client.put('/auth/change-password', { current_password, new_password, confirm_password })
}

export const imports = {
  upload: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return client.post('/imports/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  listBatches: () => client.get('/imports/batches'),

  getBatch: (id) => client.get(`/imports/batches/${id}`),

  updateBatch: (id, data) =>
    client.put(`/imports/batches/${id}`, data),

  deleteBatch: (id) =>
    client.delete(`/imports/batches/${id}`),

  getTransactions: (batchId) =>
    client.get(`/imports/batches/${batchId}/transactions`),

  reviewTransaction: (batchId, transactionId, category, status, notes) =>
    client.put(`/imports/batches/${batchId}/transactions/${transactionId}`, {
      category,
      status,
      notes
    }),

  deleteTransaction: (batchId, transactionId) =>
    client.delete(`/imports/batches/${batchId}/transactions/${transactionId}`),

  findDuplicates: (thresholdDays = 3) =>
    client.get('/imports/duplicates', { params: { threshold_days: thresholdDays } }),

  mergeDuplicates: (keepTransactionId, removeTransactionIds) =>
    client.post('/imports/merge-duplicates', {
      keep_transaction_id: keepTransactionId,
      remove_transaction_ids: removeTransactionIds
    })
}

export const catalog = {
  listCategories: (params = {}) =>
    client.get('/catalog/categories', { params }),
  getCategory: (id) => client.get(`/catalog/categories/${id}`),
  createCategory: (payload) => client.post('/catalog/categories', payload),
  updateCategory: (id, payload) =>
    client.put(`/catalog/categories/${id}`, payload),
  deleteCategory: (id) => client.delete(`/catalog/categories/${id}`),

  listInstitutions: (params = {}) =>
    client.get('/catalog/institutions', { params }),
  createInstitution: (payload) =>
    client.post('/catalog/institutions', payload),
  updateInstitution: (id, payload) =>
    client.put(`/catalog/institutions/${id}`, payload),
  deleteInstitution: (id) =>
    client.delete(`/catalog/institutions/${id}`),

  listCreditCards: (params = {}) =>
    client.get('/catalog/credit-cards', { params }),
  createCreditCard: (payload) =>
    client.post('/catalog/credit-cards', payload),
  updateCreditCard: (id, payload) =>
    client.put(`/catalog/credit-cards/${id}`, payload),
  deleteCreditCard: (id) =>
    client.delete(`/catalog/credit-cards/${id}`),

  listInvestmentTypes: () =>
    client.get('/catalog/investment-types'),
  createInvestmentType: (payload) =>
    client.post('/catalog/investment-types', payload),
  updateInvestmentType: (id, payload) =>
    client.put(`/catalog/investment-types/${id}`, payload),
  deleteInvestmentType: (id) =>
    client.delete(`/catalog/investment-types/${id}`)
}

export const reports = {
  summary: (params = {}) => client.get('/reports/summary', { params }),
  monthly: (params = {}) => client.get('/reports/monthly', { params }),
  compare: (params = {}) => client.get('/reports/compare', { params }),
  monthlyCategories: (params = {}) => client.get('/reports/monthly-categories', { params })
}

export const planning = {
  listPlans: (params = {}) => client.get('/plans', { params }),
  createPlan: (payload) => client.post('/plans', payload),
  updatePlan: (id, payload) => client.put(`/plans/${id}`, payload),
  deletePlan: (id) => client.delete(`/plans/${id}`),
  listIncomeProjections: (params = {}) => client.get('/income-projections', { params }),
  createIncomeProjection: (payload) => client.post('/income-projections', payload),
  updateIncomeProjection: (id, payload) => client.put(`/income-projections/${id}`, payload),
  deleteIncomeProjection: (id) => client.delete(`/income-projections/${id}`),
  listBudgets: (params = {}) => client.get('/plans/budgets', { params }),
  createBudget: (payload) => client.post('/plans/budgets', payload),
  updateBudget: (id, payload) => client.put(`/plans/budgets/${id}`, payload),
  deleteBudget: (id) => client.delete(`/plans/budgets/${id}`),
  budgetCompliance: (params = {}) => client.get('/plans/budget-compliance', { params }),
  plannedSurplus: () => client.get('/plans/surplus'),
  listNotes: () => client.get('/plans/notes'),
  createNote: (payload) => client.post('/plans/notes', payload),
  deleteNote: (id) => client.delete(`/plans/notes/${id}`),
  listRecurring: () => client.get('/plans/recurring'),
  createRecurring: (payload) => client.post('/plans/recurring', payload),
  deleteRecurring: (id) => client.delete(`/plans/recurring/${id}`)
}

export const investments = {
  list: (params = {}) => client.get('/investments', { params }),
  create: (payload) => client.post('/investments', payload),
  update: (id, payload) => client.put(`/investments/${id}`, payload),
  remove: (id) => client.delete(`/investments/${id}`),
  addDividend: (id, payload) => client.post(`/investments/${id}/dividends`, payload),
  deleteDividend: (dividendId) => client.delete(`/investments/dividends/${dividendId}`),
  summary: () => client.get('/investments/summary'),
  redeem: (id, payload) => client.post(`/investments/${id}/redeem`, payload),
  performance: () => client.get('/investments/performance')
}

export const ml = {
  stats: () => client.get('/ml/stats'),
  health: () => client.get('/ml/health')
}

export const training = {
  uploadCSV: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return client.post('/training/upload-csv', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  train: (csvId, userId) =>
    client.post('/training/train', { csv_id: csvId, user_id: userId }),
  status: (jobId) => client.get(`/training/status/${jobId}`),
  history: (params = {}) => client.get('/training/history', { params }),
  autoRetrain: (userId, minTransactions) =>
    client.post('/training/auto-retrain', {
      user_id: userId,
      min_transactions: minTransactions
    }),
  activate: (modelVersion) =>
    client.post('/training/activate', { model_version: modelVersion })
}

export const ai = {
  analyze: (summary, timeframe = 'last_month') =>
    client.post('/ai/analyze', { summary, timeframe }),
  chat: (message, context = {}) =>
    client.post('/ai/chat', { message, context }),
  insights: (params = {}) => client.get('/ai/insights', { params }),
  projections: (goals, currentState) =>
    client.post('/ai/projections', { goals, current_state: currentState }),
  health: () => client.get('/ai/health')
}

// Transactions (manual cash flow)
export const transactions = {
  create: (transaction) => client.post('/transactions/', transaction),
  list: (params = {}) => client.get('/transactions/', { params }),
  get: (id) => client.get(`/transactions/${id}`),
  update: (id, updates) => client.put(`/transactions/${id}`, updates),
  delete: (id, hard = false) => client.delete(`/transactions/${id}`, { params: { hard } }),
  markCompleted: (id) => client.post(`/transactions/${id}/complete`),
  markPending: (id) => client.post(`/transactions/${id}/pending`),
  bulkUpdateStatus: (transactionIds, status) =>
    client.post('/transactions/bulk-update-status', { transaction_ids: transactionIds, status }),
  duplicate: (id, newEventDate, linkAsRecurrence = true) =>
    client.post(`/transactions/${id}/duplicate`, { new_event_date: newEventDate, link_as_recurrence: linkAsRecurrence }),
  summary: (startDate, endDate, includePending = false) =>
    client.get('/transactions/summary', { params: { start_date: startDate, end_date: endDate, include_pending: includePending } }),
  monthlySummary: (year, month, includePending = false) =>
    client.get(`/transactions/monthly-summary/${year}/${month}`, { params: { include_pending: includePending } }),
  byCategory: (startDate, endDate, transactionType = null, includePending = false) =>
    client.get('/transactions/by-category', { params: { start_date: startDate, end_date: endDate, transaction_type: transactionType, include_pending: includePending } })
}

// Backup & Export
export const backup = {
  exportJSON: () => client.get('/backup/export/json', { responseType: 'blob' }),
  exportExcel: () => client.get('/backup/export/excel', { responseType: 'blob' }),
  import: (backupData, overwrite = false) => client.post('/backup/import', backupData, { params: { overwrite } }),
  importFile: (file, overwrite = false) => {
    const formData = new FormData()
    formData.append('file', file)
    return client.post('/backup/import', formData, { params: { overwrite }, headers: { 'Content-Type': 'multipart/form-data' } })
  },
  summary: () => client.get('/backup/summary'),
  validate: (backupData) => client.post('/backup/validate', backupData),
  validateFile: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return client.post('/backup/validate', formData, { headers: { 'Content-Type': 'multipart/form-data' } })
  }
}

export default client
