import { describe, expect, it, vi, beforeEach } from 'vitest'
import client, { catalog } from './client'

describe('catalog api client', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('calls category endpoints with expected paths', async () => {
    const getSpy = vi.spyOn(client, 'get').mockResolvedValue({ data: {} })
    const postSpy = vi.spyOn(client, 'post').mockResolvedValue({ data: {} })
    const putSpy = vi.spyOn(client, 'put').mockResolvedValue({ data: {} })
    const delSpy = vi.spyOn(client, 'delete').mockResolvedValue({ data: {} })

    await catalog.listCategories()
    await catalog.getCategory(5)
    await catalog.createCategory({ name: 'Teste', type: 'expense' })
    await catalog.updateCategory(5, { name: 'Atualizado' })
    await catalog.deleteCategory(7)

    expect(getSpy).toHaveBeenCalledWith('/catalog/categories', { params: {} })
    expect(getSpy).toHaveBeenCalledWith('/catalog/categories/5')
    expect(postSpy).toHaveBeenCalledWith('/catalog/categories', { name: 'Teste', type: 'expense' })
    expect(putSpy).toHaveBeenCalledWith('/catalog/categories/5', { name: 'Atualizado' })
    expect(delSpy).toHaveBeenCalledWith('/catalog/categories/7')
  })

  it('calls institutions, cards and investment endpoints', async () => {
    const getSpy = vi.spyOn(client, 'get').mockResolvedValue({ data: {} })
    const postSpy = vi.spyOn(client, 'post').mockResolvedValue({ data: {} })
    const putSpy = vi.spyOn(client, 'put').mockResolvedValue({ data: {} })
    const delSpy = vi.spyOn(client, 'delete').mockResolvedValue({ data: {} })

    await catalog.listInstitutions()
    await catalog.createInstitution({ name: 'Banco', account_type: 'corrente' })
    await catalog.updateInstitution(2, { name: 'Banco 2' })
    await catalog.deleteInstitution(3)

    await catalog.listCreditCards()
    await catalog.createCreditCard({ name: 'Card', institution_id: 1 })
    await catalog.updateCreditCard(1, { limit_amount: 500 })
    await catalog.deleteCreditCard(2)

    await catalog.listInvestmentTypes()
    await catalog.createInvestmentType({ name: 'CDB' })
    await catalog.updateInvestmentType(2, { name: 'ETF' })
    await catalog.deleteInvestmentType(3)

    expect(getSpy).toHaveBeenCalledWith('/catalog/institutions', { params: {} })
    expect(postSpy).toHaveBeenCalledWith('/catalog/institutions', { name: 'Banco', account_type: 'corrente' })
    expect(putSpy).toHaveBeenCalledWith('/catalog/institutions/2', { name: 'Banco 2' })
    expect(delSpy).toHaveBeenCalledWith('/catalog/institutions/3')

    expect(getSpy).toHaveBeenCalledWith('/catalog/credit-cards', { params: {} })
    expect(postSpy).toHaveBeenCalledWith('/catalog/credit-cards', { name: 'Card', institution_id: 1 })
    expect(putSpy).toHaveBeenCalledWith('/catalog/credit-cards/1', { limit_amount: 500 })
    expect(delSpy).toHaveBeenCalledWith('/catalog/credit-cards/2')

    expect(getSpy).toHaveBeenCalledWith('/catalog/investment-types')
    expect(postSpy).toHaveBeenCalledWith('/catalog/investment-types', { name: 'CDB' })
    expect(putSpy).toHaveBeenCalledWith('/catalog/investment-types/2', { name: 'ETF' })
    expect(delSpy).toHaveBeenCalledWith('/catalog/investment-types/3')
  })
})
