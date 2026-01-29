import { useNavigate } from 'react-router-dom'
import { useState } from 'react'

const currency = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' })

export default function Simulators() {
  const navigate = useNavigate()
  const [goalForm, setGoalForm] = useState({ objetivo: '', inicial: '', tempo: '', rent: '' })
  const [timeForm, setTimeForm] = useState({ objetivo: '', inicial: '', aporte: '', rent: '' })
  const [futureForm, setFutureForm] = useState({ inicial: '', aporte: '', tempo: '', rent: '' })
  const [result, setResult] = useState({ goal: null, time: null, future: null })

  const calcGoal = () => {
    const objetivo = Number(goalForm.objetivo || 0)
    const inicial = Number(goalForm.inicial || 0)
    const tempo = Number(goalForm.tempo || 0)
    const rent = Number(goalForm.rent || 0) / 100 / 12
    if (tempo <= 0) return
    const num = objetivo - inicial * Math.pow(1 + rent, tempo)
    const denom = ((1 + rent) ** tempo - 1) / rent || tempo
    const aporte = num / denom
    setResult((r) => ({ ...r, goal: { aporte, objetivo } }))
  }

  const calcTime = () => {
    const objetivo = Number(timeForm.objetivo || 0)
    const inicial = Number(timeForm.inicial || 0)
    const aporte = Number(timeForm.aporte || 0)
    const rent = Number(timeForm.rent || 0) / 100 / 12
    let saldo = inicial
    let meses = 0
    while (saldo < objetivo && meses < 600) {
      saldo = saldo * (1 + rent) + aporte
      meses += 1
    }
    setResult((r) => ({ ...r, time: { meses, saldo } }))
  }

  const calcFuture = () => {
    const inicial = Number(futureForm.inicial || 0)
    const aporte = Number(futureForm.aporte || 0)
    const tempo = Number(futureForm.tempo || 0)
    const rent = Number(futureForm.rent || 0) / 100 / 12
    const montante = inicial * (1 + rent) ** tempo + aporte * (((1 + rent) ** tempo - 1) / rent)
    setResult((r) => ({ ...r, future: { montante } }))
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-800">🧮 Simuladores</h1>
          <button
            onClick={() => navigate('/')}
            className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition shadow-sm"
          >
            ← Voltar
          </button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6 space-y-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg shadow-md p-5">
            <h2 className="text-lg font-semibold text-gray-800 mb-3">Objetivo (aporte mensal)</h2>
            <div className="space-y-2">
              <input className="w-full border rounded px-3 py-2" placeholder="Valor objetivo" type="number" value={goalForm.objetivo} onChange={(e) => setGoalForm({ ...goalForm, objetivo: e.target.value })} />
              <input className="w-full border rounded px-3 py-2" placeholder="Valor inicial" type="number" value={goalForm.inicial} onChange={(e) => setGoalForm({ ...goalForm, inicial: e.target.value })} />
              <input className="w-full border rounded px-3 py-2" placeholder="Tempo (meses)" type="number" value={goalForm.tempo} onChange={(e) => setGoalForm({ ...goalForm, tempo: e.target.value })} />
              <input className="w-full border rounded px-3 py-2" placeholder="Rentabilidade % a.a" type="number" value={goalForm.rent} onChange={(e) => setGoalForm({ ...goalForm, rent: e.target.value })} />
              <button onClick={calcGoal} className="w-full bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">Calcular</button>
              {result.goal && <p className="text-sm text-gray-800">Aporte mensal: {currency.format(result.goal.aporte || 0)}</p>}
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-5">
            <h2 className="text-lg font-semibold text-gray-800 mb-3">Tempo para objetivo</h2>
            <div className="space-y-2">
              <input className="w-full border rounded px-3 py-2" placeholder="Valor objetivo" type="number" value={timeForm.objetivo} onChange={(e) => setTimeForm({ ...timeForm, objetivo: e.target.value })} />
              <input className="w-full border rounded px-3 py-2" placeholder="Valor inicial" type="number" value={timeForm.inicial} onChange={(e) => setTimeForm({ ...timeForm, inicial: e.target.value })} />
              <input className="w-full border rounded px-3 py-2" placeholder="Aporte mensal" type="number" value={timeForm.aporte} onChange={(e) => setTimeForm({ ...timeForm, aporte: e.target.value })} />
              <input className="w-full border rounded px-3 py-2" placeholder="Rentabilidade % a.a" type="number" value={timeForm.rent} onChange={(e) => setTimeForm({ ...timeForm, rent: e.target.value })} />
              <button onClick={calcTime} className="w-full bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">Calcular</button>
              {result.time && <p className="text-sm text-gray-800">Tempo: {result.time.meses} meses · Montante: {currency.format(result.time.saldo || 0)}</p>}
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-5">
            <h2 className="text-lg font-semibold text-gray-800 mb-3">Montante futuro</h2>
            <div className="space-y-2">
              <input className="w-full border rounded px-3 py-2" placeholder="Valor inicial" type="number" value={futureForm.inicial} onChange={(e) => setFutureForm({ ...futureForm, inicial: e.target.value })} />
              <input className="w-full border rounded px-3 py-2" placeholder="Aporte mensal" type="number" value={futureForm.aporte} onChange={(e) => setFutureForm({ ...futureForm, aporte: e.target.value })} />
              <input className="w-full border rounded px-3 py-2" placeholder="Tempo (meses)" type="number" value={futureForm.tempo} onChange={(e) => setFutureForm({ ...futureForm, tempo: e.target.value })} />
              <input className="w-full border rounded px-3 py-2" placeholder="Rentabilidade % a.a" type="number" value={futureForm.rent} onChange={(e) => setFutureForm({ ...futureForm, rent: e.target.value })} />
              <button onClick={calcFuture} className="w-full bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">Calcular</button>
              {result.future && <p className="text-sm text-gray-800">Montante: {currency.format(result.future.montante || 0)}</p>}
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
