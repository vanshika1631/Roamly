import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Link, Route, Routes } from "react-router-dom";
import IntakePage from "@/pages/IntakePage";
import ItineraryPage from "@/pages/ItineraryPage";
import PlanPage from "@/pages/PlanPage";

const queryClient = new QueryClient();

function Nav() {
  return (
    <nav className="border-b px-6 py-3 flex gap-6 text-sm font-medium">
      <Link to="/" className="text-blue-600">Roamly ✈</Link>
      <Link to="/intake" className="text-gray-600 hover:text-gray-900">Intake</Link>
      <Link to="/itinerary" className="text-gray-600 hover:text-gray-900">Itinerary</Link>
    </nav>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <div className="min-h-screen flex flex-col">
          <Nav />
          <main className="flex-1">
            <Routes>
              <Route path="/" element={<IntakePage />} />
              <Route path="/intake" element={<IntakePage />} />
              <Route path="/itinerary" element={<ItineraryPage />} />
              <Route path="/plan" element={<PlanPage />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
