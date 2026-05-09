import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Link, Route, Routes } from "react-router-dom";
import IntakePage from "@/pages/IntakePage";
import ItineraryPage from "@/pages/ItineraryPage";
import PlanPage from "@/pages/PlanPage";
const queryClient = new QueryClient();
function Nav() {
    return (_jsxs("nav", { className: "border-b px-6 py-3 flex gap-6 text-sm font-medium", children: [_jsx(Link, { to: "/", className: "text-blue-600", children: "Roamly \u2708" }), _jsx(Link, { to: "/intake", className: "text-gray-600 hover:text-gray-900", children: "Intake" }), _jsx(Link, { to: "/itinerary", className: "text-gray-600 hover:text-gray-900", children: "Itinerary" })] }));
}
export default function App() {
    return (_jsx(QueryClientProvider, { client: queryClient, children: _jsx(BrowserRouter, { children: _jsxs("div", { className: "min-h-screen flex flex-col", children: [_jsx(Nav, {}), _jsx("main", { className: "flex-1", children: _jsxs(Routes, { children: [_jsx(Route, { path: "/", element: _jsx(IntakePage, {}) }), _jsx(Route, { path: "/intake", element: _jsx(IntakePage, {}) }), _jsx(Route, { path: "/itinerary", element: _jsx(ItineraryPage, {}) }), _jsx(Route, { path: "/plan", element: _jsx(PlanPage, {}) })] }) })] }) }) }));
}
