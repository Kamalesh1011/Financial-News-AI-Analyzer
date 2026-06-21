import { ErrorBoundary } from "@/components/ui/ErrorBoundary"
import { Dashboard } from "@/components/dashboard/layout"

function App() {
  return (
    <ErrorBoundary>
      <Dashboard />
    </ErrorBoundary>
  )
}

export default App
