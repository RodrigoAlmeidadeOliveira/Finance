import '@testing-library/jest-dom'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'
import Reports from './Reports'

vi.mock('../api/client', () => ({
  reports: {
    summary: vi.fn().mockResolvedValue({
      data: {
        totals: { income: 1000, expense: 400, balance: 600 },
        categories: [
          { name: 'Salário', income: 1000, expense: 0, total: 1000 },
          { name: 'Mercado', income: 0, expense: 400, total: -400 }
        ],
        status_counts: { approved: 2, pending: 1 },
        count: 3
      }
    }),
    monthly: vi.fn().mockResolvedValue({
      data: {
        series: [
          { year: 2025, month: 1, income: 1000, expense: 200, balance: 800 },
          { year: 2025, month: 2, income: 800, expense: 300, balance: 500 }
        ]
      }
    }),
    compare: vi.fn().mockResolvedValue({
      data: {
        previous: { totals: { income: 800, expense: 300, balance: 500 } }
      }
    })
  },
  imports: {
    listBatches: vi.fn().mockResolvedValue({ data: { batches: [] } })
  },
  catalog: {
    listCategories: vi.fn().mockResolvedValue({ data: { items: [] } })
  }
}))

describe('Reports page', () => {
  it('renders summary cards and charts after load', async () => {
    render(
      <MemoryRouter>
        <Reports />
      </MemoryRouter>
    )

    await waitFor(() => {
      expect(screen.getAllByText((text) => text.includes('R$') && text.includes('1.000')).length).toBeGreaterThan(0)
    })
    expect(screen.getAllByText((text) => text.includes('R$') && text.includes('400')).length).toBeGreaterThan(0)
    expect(screen.getAllByText((text) => text.includes('R$') && text.includes('600')).length).toBeGreaterThan(0)
  })

  it('allows toggling include pending and refreshing', async () => {
    const { reports } = await import('../api/client')

    render(
      <MemoryRouter>
        <Reports />
      </MemoryRouter>
    )

    await waitFor(() => {
      expect(screen.getAllByText((text) => text.includes('R$') && text.includes('1.000')).length).toBeGreaterThan(0)
    })
    fireEvent.click(screen.getByLabelText(/Incluir pendentes/i))
    fireEvent.click(screen.getByText(/Atualizar/i))

    await waitFor(() => {
      const lastCall = reports.summary.mock.calls.at(-1)?.[0]
      expect(lastCall?.include_pending).toBe(1)
    })
  })
})
