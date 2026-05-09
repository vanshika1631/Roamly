import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { createTrip } from "@/lib/api";
import { useAppStore } from "@/stores/appStore";
export default function PlanPage() {
    const navigate = useNavigate();
    const setTripId = useAppStore((s) => s.setTripId);
    const [form, setForm] = useState({
        destination: "",
        departure_city: "",
        start_date: "",
        end_date: "",
        total_budget_usd: "",
        traveler_count: "1",
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const teb = useAppStore((s) => s.teb);
    const handleSubmit = async () => {
        setError("");
        setLoading(true);
        try {
            const result = await createTrip("test-user-1", {
                destination: form.destination,
                departure_city: form.departure_city,
                start_date: form.start_date,
                end_date: form.end_date,
                total_budget_usd: parseFloat(form.total_budget_usd),
                traveler_count: parseInt(form.traveler_count),
            }, teb ?? undefined);
            setTripId(result.trip_id);
            navigate("/itinerary");
        }
        catch (err) {
            setError("Something went wrong. Please try again.");
        }
        finally {
            setLoading(false);
        }
    };
    const isValid = form.destination &&
        form.departure_city &&
        form.start_date &&
        form.end_date &&
        form.total_budget_usd &&
        form.traveler_count;
    return (_jsxs("div", { className: "max-w-lg mx-auto p-6", children: [_jsxs("div", { className: "py-4 border-b mb-6", children: [_jsx("h1", { className: "text-2xl font-bold text-gray-900", children: "Plan your trip \u2708" }), _jsx("p", { className: "text-sm text-gray-500", children: "Enter your trip details" })] }), _jsxs("div", { className: "flex flex-col gap-4", children: [_jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-1", children: "Where are you going?" }), _jsx("input", { className: "w-full border rounded-xl px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500", placeholder: "e.g. Lisbon", value: form.destination, onChange: (e) => setForm({ ...form, destination: e.target.value }) })] }), _jsxs("div", { children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-1", children: "Departing from?" }), _jsx("input", { className: "w-full border rounded-xl px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500", placeholder: "e.g. New York", value: form.departure_city, onChange: (e) => setForm({ ...form, departure_city: e.target.value }) })] }), _jsxs("div", { className: "flex gap-3", children: [_jsxs("div", { className: "flex-1", children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-1", children: "Start date" }), _jsx("input", { type: "date", className: "w-full border rounded-xl px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500", value: form.start_date, onChange: (e) => setForm({ ...form, start_date: e.target.value }) })] }), _jsxs("div", { className: "flex-1", children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-1", children: "End date" }), _jsx("input", { type: "date", className: "w-full border rounded-xl px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500", value: form.end_date, onChange: (e) => setForm({ ...form, end_date: e.target.value }) })] })] }), _jsxs("div", { className: "flex gap-3", children: [_jsxs("div", { className: "flex-1", children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-1", children: "Total budget (USD)" }), _jsx("input", { type: "number", className: "w-full border rounded-xl px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500", placeholder: "e.g. 2000", value: form.total_budget_usd, onChange: (e) => setForm({ ...form, total_budget_usd: e.target.value }) })] }), _jsxs("div", { className: "flex-1", children: [_jsx("label", { className: "block text-sm font-medium text-gray-700 mb-1", children: "Travelers" }), _jsx("input", { type: "number", min: "1", max: "20", className: "w-full border rounded-xl px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500", value: form.traveler_count, onChange: (e) => setForm({ ...form, traveler_count: e.target.value }) })] })] }), error && _jsx("p", { className: "text-red-500 text-sm", children: error }), _jsx("button", { className: "w-full bg-blue-600 text-white py-3 rounded-xl text-sm font-medium hover:bg-blue-700 disabled:opacity-50 mt-2", onClick: handleSubmit, disabled: !isValid || loading, children: loading ? "Creating your trip..." : "Generate my itinerary →" })] })] }));
}
