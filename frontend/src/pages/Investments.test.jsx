import '@testing-library/jest-dom'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'
import Investments from './Investments'

vi.mock('../api/client', () => ({
  investments: {
    list: vi.fn().mockResolvedValue({ data: { items: [] } }),
    summary: vi.fn().mockResolvedValue({ data: { total_invested: 0, total_current: 0, total_gain: 0 } }),
    create: vi.fn().mockResolvedValue({}),
    remove: vi.fn().mockResolvedValue({}),
    addDividend: vi.fn().mockResolvedValue({}),
    deleteDividend: vi.fn().mockResolvedValue({})
  },
  catalog: {
    listInstitutions: vi.fn().mockResolvedValue({ data: { items: [] } }),
    listInvestmentTypes: vi.fn().mockResolvedValue({ data: { items: [] } })
  }
}))

describe('Investments page', () => {
  it('renders form and summary', async () => {
    render(
      <MemoryRouter>
        <Investments />
      </MemoryRouter>
    )

    await waitFor(() => expect(screen.getByText(/Investido/)).toBeInTheDocument())
    expect(screen.getByLabelText(/Nome/)).toBeInTheDocument()
  })

  it('creates a new investment', async () => {
    const { investments } = await import('../api/client')
    render(
      <MemoryRouter>
        <Investments />
      </MemoryRouter>
    )

    await waitFor(() => expect(screen.getByLabelText(/Nome/)).toBeInTheDocument())
    fireEvent.change(screen.getByLabelText(/Nome/), { target: { value: 'CDB Banco' } })
    fireEvent.change(screen.getByLabelText(/Aplicado/), { target: { value: '1000' } })
    fireEvent.submit(screen.getByText(/Salvar investimento/).closest('form'))

    await waitFor(() => expect(investments.create).toHaveBeenCalled())
  })
})
