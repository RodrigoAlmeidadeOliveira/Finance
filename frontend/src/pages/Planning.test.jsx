import '@testing-library/jest-dom'
import { render, screen, waitFor, fireEvent } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'
import Planning from './Planning'

vi.mock('../api/client', () => ({
  planning: {
    listPlans: vi.fn().mockResolvedValue({ data: { items: [] } }),
    listIncomeProjections: vi.fn().mockResolvedValue({ data: { items: [] } }),
    createPlan: vi.fn().mockResolvedValue({}),
    createIncomeProjection: vi.fn().mockResolvedValue({}),
    updatePlan: vi.fn().mockResolvedValue({}),
    updateIncomeProjection: vi.fn().mockResolvedValue({}),
    deletePlan: vi.fn().mockResolvedValue({}),
    deleteIncomeProjection: vi.fn().mockResolvedValue({}),
    listBudgets: vi.fn().mockResolvedValue({ data: { items: [] } }),
    budgetCompliance: vi.fn().mockResolvedValue({ data: { items: [] } }),
    createBudget: vi.fn().mockResolvedValue({}),
    deleteBudget: vi.fn().mockResolvedValue({}),
    plannedSurplus: vi.fn().mockResolvedValue({ data: { projected_income: 0, expense_budget: 0, planned_surplus: 0 } }),
    listNotes: vi.fn().mockResolvedValue({ data: { items: [] } }),
    createNote: vi.fn().mockResolvedValue({}),
    deleteNote: vi.fn().mockResolvedValue({})
  },
  catalog: {
    listInstitutions: vi.fn().mockResolvedValue({ data: { items: [] } }),
    listCategories: vi.fn().mockResolvedValue({
      data: { items: [{ id: 1, name: 'Alimentação', type: 'expense' }] }
    })
  }
}))

describe('Planning page', () => {
  it('renders forms and basic stats', async () => {
    render(
      <MemoryRouter>
        <Planning />
      </MemoryRouter>
    )

    await waitFor(() => expect(screen.getByText(/Planejamento/)).toBeInTheDocument())
    expect(screen.getByLabelText(/Meta/)).toBeInTheDocument()
    expect(screen.getByLabelText(/Data esperada/)).toBeInTheDocument()
  })

  it('submits new plan', async () => {
    const { planning } = await import('../api/client')
    render(
      <MemoryRouter>
        <Planning />
      </MemoryRouter>
    )

    await waitFor(() => expect(screen.getByText(/Planejamento/)).toBeInTheDocument())
    fireEvent.change(screen.getByLabelText(/Nome/), { target: { value: 'Plano Teste' } })
    fireEvent.change(screen.getByLabelText(/Meta/), { target: { value: '1000' } })
    fireEvent.submit(screen.getByText(/Salvar Plano/).closest('form'))

    await waitFor(() => expect(planning.createPlan).toHaveBeenCalled())
  })

  it('applies filters when updating projections', async () => {
    const { planning } = await import('../api/client')
    render(
      <MemoryRouter>
        <Planning />
      </MemoryRouter>
    )

    await waitFor(() => expect(planning.listIncomeProjections).toHaveBeenCalled())
    fireEvent.change(screen.getByLabelText(/Data início/), { target: { value: '2025-01-01' } })
    fireEvent.change(screen.getByLabelText(/Data fim/), { target: { value: '2025-02-01' } })
    fireEvent.click(screen.getByText(/Atualizar/))

    await waitFor(() => {
      const last = planning.listIncomeProjections.mock.calls.at(-1)?.[0]
      expect(last?.start).toBe('2025-01-01')
      expect(last?.end).toBe('2025-02-01')
    })
  })

  it('creates a budget meta', async () => {
    const { planning } = await import('../api/client')
    render(
      <MemoryRouter>
        <Planning />
      </MemoryRouter>
    )

    await waitFor(() => expect(planning.listBudgets).toHaveBeenCalled())
    fireEvent.change(screen.getByLabelText(/Categoria/), { target: { value: '1' } })
    fireEvent.change(screen.getByLabelText(/^Mês$/), { target: { value: '1' } })
    fireEvent.change(screen.getByLabelText(/Ano/), { target: { value: '2025' } })
    fireEvent.change(screen.getByLabelText(/Valor \(meta\)/), { target: { value: '500' } })
    fireEvent.click(screen.getByText(/Salvar meta/))

    await waitFor(() => expect(planning.createBudget).toHaveBeenCalled())
  })
})
