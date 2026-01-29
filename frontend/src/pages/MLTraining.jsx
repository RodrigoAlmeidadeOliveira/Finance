import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { training, ml } from '../api/client'
import '../App.css'

export default function MLTraining() {
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState('upload')
  const [selectedFile, setSelectedFile] = useState(null)
  const [csvPreview, setCsvPreview] = useState(null)
  const [uploadedCsvId, setUploadedCsvId] = useState(null)
  const [trainingStatus, setTrainingStatus] = useState(null)
  const [trainingHistory, setTrainingHistory] = useState([])
  const [currentModel, setCurrentModel] = useState(null)
  const [autoRetrainEnabled, setAutoRetrainEnabled] = useState(false)
  const [minTransactions, setMinTransactions] = useState(100)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    loadTrainingHistory()
    loadCurrentModel()
  }, [])

  const loadTrainingHistory = async () => {
    try {
      const response = await training.history({ limit: 10 })
      setTrainingHistory(response.data.jobs || [])
    } catch (err) {
      console.error('Erro ao carregar histórico:', err)
    }
  }

  const loadCurrentModel = async () => {
    try {
      const response = await ml.stats()
      setCurrentModel(response.data)
    } catch (err) {
      console.error('Erro ao carregar modelo atual:', err)
    }
  }

  const handleFileSelect = (e) => {
    const file = e.target.files?.[0]
    if (file) {
      setSelectedFile(file)
      setCsvPreview(null)
      setUploadedCsvId(null)
      setError(null)
    }
  }

  const handleFileDrop = (e) => {
    e.preventDefault()
    const file = e.dataTransfer.files?.[0]
    if (file && file.name.endsWith('.csv')) {
      setSelectedFile(file)
      setCsvPreview(null)
      setUploadedCsvId(null)
      setError(null)
    } else {
      setError('Apenas arquivos CSV são aceitos')
    }
  }

  const handleDragOver = (e) => {
    e.preventDefault()
  }

  const uploadCSV = async () => {
    if (!selectedFile) return

    setLoading(true)
    setError(null)

    try {
      const response = await training.uploadCSV(selectedFile)

      // FIX: Se response.data for string, parsear para objeto
      let data = response.data
      if (typeof data === 'string') {
        console.log('⚠️ Resposta veio como string, parseando...')
        data = JSON.parse(data)
      }

      // DEBUG: Log completo da resposta
      console.log('=== RESPOSTA DO BACKEND ===')
      console.log('Status:', response.status)
      console.log('Data tipo:', typeof data)
      console.log('Data completo:', JSON.stringify(data, null, 2))
      console.log('Campo valid:', data.valid)
      console.log('Tipo de valid:', typeof data.valid)
      console.log('valid === true?', data.valid === true)
      console.log('========================')

      const { csv_id, preview, valid } = data

      if (valid) {
        setCsvPreview(preview)
        setUploadedCsvId(csv_id)
        alert('CSV validado com sucesso! Você pode iniciar o treinamento.')
      } else {
        console.error('ERRO: valid é falsy!', valid)
        setError('CSV inválido. Verifique o formato.')
      }
    } catch (err) {
      console.error('ERRO no catch:', err)
      console.error('Resposta de erro:', err.response?.data)
      setError(err.response?.data?.details?.join(', ') || 'Erro ao enviar CSV')
    } finally {
      setLoading(false)
    }
  }

  const startTraining = async () => {
    if (!uploadedCsvId) return

    setLoading(true)
    setError(null)

    try {
      const response = await training.train(uploadedCsvId, 1) // TODO: usar userId real
      const { job_id, model_version, metrics } = response.data

      alert(`Treinamento iniciado!\nVersão do modelo: ${model_version}\nAcurácia: ${(metrics.accuracy * 100).toFixed(2)}%`)

      // Limpar formulário
      setSelectedFile(null)
      setCsvPreview(null)
      setUploadedCsvId(null)

      // Recarregar histórico e modelo
      loadTrainingHistory()
      loadCurrentModel()
    } catch (err) {
      setError(err.response?.data?.details || 'Erro ao treinar modelo')
    } finally {
      setLoading(false)
    }
  }

  const triggerAutoRetrain = async () => {
    setLoading(true)
    setError(null)

    try {
      const response = await training.autoRetrain(1, minTransactions) // TODO: usar userId real

      if (response.data.message) {
        alert(response.data.message)
      } else {
        const { model_version, metrics } = response.data
        alert(`Auto-retreinamento concluído!\nVersão: ${model_version}\nAcurácia: ${(metrics.accuracy * 100).toFixed(2)}%`)
        loadTrainingHistory()
        loadCurrentModel()
      }
    } catch (err) {
      setError(err.response?.data?.details || 'Erro no auto-retreinamento')
    } finally {
      setLoading(false)
    }
  }

  const activateModel = async (modelVersion) => {
    if (!confirm(`Ativar modelo ${modelVersion}?\nIsso substituirá o modelo atual. A aplicação precisa ser reiniciada.`)) {
      return
    }

    setLoading(true)
    setError(null)

    try {
      await training.activate(modelVersion)
      alert('Modelo ativado! Por favor, reinicie a aplicação.')
      loadCurrentModel()
    } catch (err) {
      setError(err.response?.data?.error || 'Erro ao ativar modelo')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <div className="header" style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
        <button
          onClick={() => navigate('/')}
          className="button"
          style={{
            padding: '8px 16px',
            backgroundColor: '#666',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}
        >
          ← Voltar
        </button>
        <div>
          <h1>🎓 Treinamento de Modelos ML</h1>
          <p>Treine novos modelos de categorização com dados históricos</p>
        </div>
      </div>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '20px', borderBottom: '1px solid #ddd' }}>
        {['upload', 'history', 'auto'].map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            style={{
              padding: '12px 24px',
              border: 'none',
              borderBottom: activeTab === tab ? '3px solid #4CAF50' : '3px solid transparent',
              background: 'none',
              cursor: 'pointer',
              fontWeight: activeTab === tab ? 'bold' : 'normal',
              color: activeTab === tab ? '#4CAF50' : '#666'
            }}
          >
            {tab === 'upload' && '📤 Upload CSV'}
            {tab === 'history' && '📊 Histórico'}
            {tab === 'auto' && '🔄 Auto-Retreinamento'}
          </button>
        ))}
      </div>

      {error && (
        <div style={{ padding: '12px', marginBottom: '20px', backgroundColor: '#fee', border: '1px solid #fcc', borderRadius: '4px' }}>
          ❌ {error}
        </div>
      )}

      {/* Tab: Upload CSV */}
      {activeTab === 'upload' && (
        <div className="card">
          <h2>📂 Upload de Dados Históricos</h2>
          <p style={{ color: '#666', marginBottom: '20px' }}>
            Formato esperado: <code>date, description, value, type, category</code>
          </p>

          {/* Drag & Drop Area */}
          <div
            onDrop={handleFileDrop}
            onDragOver={handleDragOver}
            style={{
              border: '2px dashed #ccc',
              borderRadius: '8px',
              padding: '40px',
              textAlign: 'center',
              backgroundColor: '#fafafa',
              marginBottom: '20px',
              cursor: 'pointer'
            }}
            onClick={() => document.getElementById('file-input').click()}
          >
            <p style={{ fontSize: '48px', margin: '0' }}>📄</p>
            <p style={{ margin: '10px 0', fontSize: '16px', fontWeight: 'bold' }}>
              {selectedFile ? selectedFile.name : 'Arraste um arquivo CSV ou clique para selecionar'}
            </p>
            <p style={{ color: '#999', fontSize: '14px' }}>Apenas arquivos .csv são aceitos</p>
            <input
              id="file-input"
              type="file"
              accept=".csv"
              onChange={handleFileSelect}
              style={{ display: 'none' }}
            />
          </div>

          <button
            onClick={uploadCSV}
            disabled={!selectedFile || loading}
            className="button"
            style={{ marginBottom: '20px' }}
          >
            {loading ? '⏳ Enviando...' : '📤 Validar CSV'}
          </button>

          {/* Preview */}
          {csvPreview && (
            <div style={{ marginTop: '20px' }}>
              <h3>👀 Preview dos Dados</h3>
              <p>
                Total de linhas: <strong>{csvPreview.total_rows}</strong> |
                Categorias: <strong>{csvPreview.categories_count}</strong>
              </p>

              <div style={{ overflowX: 'auto', marginBottom: '20px' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr style={{ backgroundColor: '#f5f5f5' }}>
                      {csvPreview.columns.map(col => (
                        <th key={col} style={{ padding: '8px', textAlign: 'left', border: '1px solid #ddd' }}>
                          {col}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {csvPreview.preview.map((row, idx) => (
                      <tr key={idx}>
                        {csvPreview.columns.map(col => (
                          <td key={col} style={{ padding: '8px', border: '1px solid #ddd' }}>
                            {row[col]}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <button
                onClick={startTraining}
                disabled={loading}
                className="button"
                style={{ backgroundColor: '#FF9800' }}
              >
                {loading ? '⏳ Treinando...' : '🚀 Iniciar Treinamento'}
              </button>
            </div>
          )}
        </div>
      )}

      {/* Tab: Histórico */}
      {activeTab === 'history' && (
        <div className="card">
          <h2>📊 Histórico de Treinamentos</h2>

          {currentModel && (
            <div style={{ padding: '16px', backgroundColor: '#e8f5e9', borderRadius: '4px', marginBottom: '20px' }}>
              <h3 style={{ margin: '0 0 10px 0' }}>✅ Modelo Atual</h3>
              <p style={{ margin: '5px 0' }}>
                Acurácia: <strong>{(currentModel.accuracy * 100).toFixed(2)}%</strong> |
                Categorias: <strong>{currentModel.n_categories}</strong> |
                Treinado em: <strong>{currentModel.training_date || 'N/A'}</strong>
              </p>
            </div>
          )}

          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ backgroundColor: '#f5f5f5' }}>
                <th style={{ padding: '12px', textAlign: 'left', border: '1px solid #ddd' }}>ID</th>
                <th style={{ padding: '12px', textAlign: 'left', border: '1px solid #ddd' }}>Versão</th>
                <th style={{ padding: '12px', textAlign: 'left', border: '1px solid #ddd' }}>Status</th>
                <th style={{ padding: '12px', textAlign: 'left', border: '1px solid #ddd' }}>Origem</th>
                <th style={{ padding: '12px', textAlign: 'left', border: '1px solid #ddd' }}>Acurácia</th>
                <th style={{ padding: '12px', textAlign: 'left', border: '1px solid #ddd' }}>Data</th>
                <th style={{ padding: '12px', textAlign: 'left', border: '1px solid #ddd' }}>Ações</th>
              </tr>
            </thead>
            <tbody>
              {trainingHistory.map(job => (
                <tr key={job.id}>
                  <td style={{ padding: '12px', border: '1px solid #ddd' }}>{job.id}</td>
                  <td style={{ padding: '12px', border: '1px solid #ddd' }}>{job.model_version}</td>
                  <td style={{ padding: '12px', border: '1px solid #ddd' }}>
                    <span style={{
                      padding: '4px 8px',
                      borderRadius: '4px',
                      fontSize: '12px',
                      backgroundColor: job.status === 'completed' ? '#4CAF50' : job.status === 'failed' ? '#f44336' : '#FF9800',
                      color: 'white'
                    }}>
                      {job.status}
                    </span>
                  </td>
                  <td style={{ padding: '12px', border: '1px solid #ddd' }}>{job.source}</td>
                  <td style={{ padding: '12px', border: '1px solid #ddd' }}>
                    {job.metrics ? `${(job.metrics.accuracy * 100).toFixed(2)}%` : '-'}
                  </td>
                  <td style={{ padding: '12px', border: '1px solid #ddd' }}>
                    {new Date(job.created_at).toLocaleString('pt-BR')}
                  </td>
                  <td style={{ padding: '12px', border: '1px solid #ddd' }}>
                    {job.status === 'completed' && (
                      <button
                        onClick={() => activateModel(job.model_version)}
                        className="button"
                        style={{ padding: '6px 12px', fontSize: '12px' }}
                      >
                        Ativar
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {trainingHistory.length === 0 && (
            <p style={{ textAlign: 'center', padding: '40px', color: '#999' }}>
              Nenhum treinamento realizado ainda
            </p>
          )}
        </div>
      )}

      {/* Tab: Auto-Retreinamento */}
      {activeTab === 'auto' && (
        <div className="card">
          <h2>🔄 Auto-Retreinamento</h2>
          <p style={{ color: '#666', marginBottom: '20px' }}>
            O sistema pode retreinar automaticamente usando transações aprovadas
          </p>

          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px' }}>
              <input
                type="checkbox"
                checked={autoRetrainEnabled}
                onChange={(e) => setAutoRetrainEnabled(e.target.checked)}
                style={{ width: '20px', height: '20px' }}
              />
              <span style={{ fontSize: '16px', fontWeight: 'bold' }}>
                Habilitar auto-retreinamento
              </span>
            </label>

            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}>
                Mínimo de transações aprovadas:
              </label>
              <input
                type="number"
                value={minTransactions}
                onChange={(e) => setMinTransactions(parseInt(e.target.value))}
                min="10"
                max="1000"
                style={{ width: '100%', padding: '8px', border: '1px solid #ddd', borderRadius: '4px' }}
              />
              <p style={{ color: '#999', fontSize: '14px', marginTop: '5px' }}>
                O retreinamento só ocorrerá quando houver pelo menos {minTransactions} transações aprovadas
              </p>
            </div>

            <button
              onClick={triggerAutoRetrain}
              disabled={loading || !autoRetrainEnabled}
              className="button"
              style={{ backgroundColor: '#2196F3' }}
            >
              {loading ? '⏳ Retreinando...' : '🔄 Executar Retreinamento Agora'}
            </button>
          </div>

          <div style={{ padding: '16px', backgroundColor: '#fff3cd', border: '1px solid #ffc107', borderRadius: '4px' }}>
            <h3 style={{ margin: '0 0 10px 0' }}>ℹ️ Como funciona?</h3>
            <ul style={{ margin: '0', paddingLeft: '20px' }}>
              <li>O sistema usa transações que você revisou e aprovou</li>
              <li>Quanto mais transações aprovadas, melhor a acurácia do modelo</li>
              <li>O novo modelo é criado mas não substituio anterior automaticamente</li>
              <li>Você pode ativar o novo modelo na aba "Histórico"</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  )
}
