import '@testing-library/jest-dom'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { MemoryRouter } from 'react-router-dom'
import Catalogs from './Catalogs'

vi.mock('../api/client', () => {
  return {
    catalog: {
      listCategories: vi.fn().mockResolvedValue({ data: { items: [] } }),
      listInstitutions: vi.fn().mockResolvedValue({ data: { items: [] } }),
      listCreditCards: vi.fn().mockResolvedValue({ data: { items: [] } }),
      listInvestmentTypes: vi.fn().mockResolvedValue({ data: { items: [] } }),
      createCategory: vi.fn().mockResolvedValue({}),
      createInstitution: vi.fn().mockResolvedValue({}),
      createCreditCard: vi.fn().mockResolvedValue({}),
      createInvestmentType: vi.fn().mockResolvedValue({})
    }
  }
})

describe('Catalogs page', () => {
  it('renders forms for all entities and submits category', async () => {
    render(
      <MemoryRouter>
        <Catalogs />
      </MemoryRouter>
    )

    expect(screen.getByText(/Cadastros Base/i)).toBeInTheDocument()
    await waitFor(() => expect(screen.getByText(/Nova Categoria/i)).toBeInTheDocument())
    expect(screen.getByText(/Nova Instituição/i)).toBeInTheDocument()
    expect(screen.getByText(/Novo Cartão/i)).toBeInTheDocument()
    expect(screen.getByText(/Novo Tipo de Investimento/i)).toBeInTheDocument()

    fireEvent.change(screen.getAllByLabelText(/Nome/i, { selector: 'input' })[0], {
      target: { value: 'Alimentação' }
    })
    fireEvent.click(screen.getByText(/Salvar Categoria/i))

    await waitFor(() => {
      expect(screen.getByText(/Categoria criada/i)).toBeInTheDocument()
    })
  })
})
