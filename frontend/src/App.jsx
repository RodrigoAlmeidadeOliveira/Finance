import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import Login from './pages/Login'
import Register from './pages/Register'
import ChangePassword from './pages/ChangePassword'
import Dashboard from './pages/Dashboard'
import ImportOFX from './pages/ImportOFX'
import Transactions from './pages/Transactions'
import Reports from './pages/Reports'
import Catalogs from './pages/Catalogs'
import ManageImports from './pages/ManageImports'
import BatchDetails from './pages/BatchDetails'
import Planning from './pages/Planning'
import Investments from './pages/Investments'
import MonthlyMatrix from './pages/MonthlyMatrix'
import Simulators from './pages/Simulators'
import AIAssistant from './pages/AIAssistant'
import MLTraining from './pages/MLTraining'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Verificar se há token válido no localStorage
    const token = localStorage.getItem('access_token')
    setIsAuthenticated(!!token)
    setLoading(false)
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">Carregando...</p>
        </div>
      </div>
    )
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/login"
          element={
            isAuthenticated ? (
              <Navigate to="/" replace />
            ) : (
              <Login setAuth={setIsAuthenticated} />
            )
          }
        />
        <Route
          path="/register"
          element={
            isAuthenticated ? (
              <Navigate to="/" replace />
            ) : (
              <Register setAuth={setIsAuthenticated} />
            )
          }
        />
        <Route
          path="/change-password"
          element={
            isAuthenticated ? (
              <ChangePassword />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
        <Route
          path="/"
          element={
            isAuthenticated ? (
              <Dashboard setAuth={setIsAuthenticated} />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
        <Route
          path="/import"
          element={
            isAuthenticated ? (
              <ImportOFX />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
        <Route
          path="/transactions"
          element={
            isAuthenticated ? (
              <Transactions />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
        <Route
          path="/catalogs"
          element={
            isAuthenticated ? (
              <Catalogs />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
        <Route
          path="/manage-imports"
          element={
            isAuthenticated ? (
              <ManageImports />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
        <Route
          path="/batch/:batchId"
          element={
            isAuthenticated ? (
              <BatchDetails />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
        <Route
          path="/reports"
          element={
            isAuthenticated ? (
              <Reports />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
        <Route
          path="/planning"
          element={
            isAuthenticated ? (
              <Planning />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
        <Route
          path="/investments"
          element={
            isAuthenticated ? (
              <Investments />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
        <Route
          path="/monthly-matrix"
          element={
            isAuthenticated ? (
              <MonthlyMatrix />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
        <Route
          path="/simulators"
          element={
            isAuthenticated ? (
              <Simulators />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
        <Route
          path="/ai-assistant"
          element={
            isAuthenticated ? (
              <AIAssistant />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
        <Route
          path="/training"
          element={
            isAuthenticated ? (
              <MLTraining />
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
