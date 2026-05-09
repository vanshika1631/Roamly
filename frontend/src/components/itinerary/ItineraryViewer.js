import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useItinerary } from "@/hooks/useItinerary";
import { useAppStore } from "@/stores/appStore";
import { useState } from "react";
import { refineTrip } from "@/lib/api";
const STATUS_LABELS = {
    pending: "Queued…",
    generating: "Generating your itinerary…",
    auditing: "Running bias audit…",
    ready: "Ready",
    failed: "Generation failed",
};
export function ItineraryViewer() {
    const tripId = useAppStore((s) => s.tripId);
    const { status, itinerary, isLoading, error } = useItinerary(tripId);
    const [refineInput, setRefineInput] = useState("");
    const [refining, setRefining] = useState(false);
    if (!tripId)
        return _jsx("p", { className: "text-gray-500", children: "No active trip." });
    if (error) {
        return (_jsxs("div", { className: "max-w-xl mx-auto mt-16 rounded-2xl border border-red-200 bg-red-50 p-6", children: [_jsx("h1", { className: "text-lg font-semibold text-red-900", children: "Could not load itinerary" }), _jsx("p", { className: "mt-2 text-sm text-red-700", children: error instanceof Error ? error.message : "Unknown error" })] }));
    }
    if (isLoading || !status) {
        return (_jsxs("div", { className: "flex flex-col items-center gap-4 mt-16", children: [_jsx("div", { className: "w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" }), _jsx("p", { className: "text-gray-600", children: "Preparing your itinerary\u2026" })] }));
    }
    if (status === "failed") {
        return (_jsxs("div", { className: "max-w-xl mx-auto mt-16 rounded-2xl border border-amber-200 bg-amber-50 p-6", children: [_jsx("h1", { className: "text-lg font-semibold text-amber-900", children: "Generation failed" }), _jsx("p", { className: "mt-2 text-sm text-amber-800", children: "The trip could not be generated. Try again from the planner with the same destination, or refresh this page if the backend job was just retried." })] }));
    }
    if (status !== "ready") {
        return (_jsxs("div", { className: "flex flex-col items-center gap-4 mt-16", children: [_jsx("div", { className: "w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" }), _jsx("p", { className: "text-gray-600", children: STATUS_LABELS[status] ?? status })] }));
    }
    if (!itinerary) {
        return (_jsxs("div", { className: "flex flex-col items-center gap-3 mt-16", children: [_jsx("div", { className: "w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" }), _jsx("p", { className: "text-gray-600", children: "Loading itinerary details\u2026" })] }));
    }
    const handleRefine = async () => {
        if (!refineInput.trim() || !tripId)
            return;
        setRefining(true);
        await refineTrip(tripId, refineInput.trim());
        setRefineInput("");
        setRefining(false);
        // Force page reload to reset polling state
        window.location.reload();
    };
    return (_jsxs("div", { className: "max-w-3xl mx-auto p-4 flex flex-col gap-6", children: [_jsxs("div", { className: "flex items-center justify-between", children: [_jsx("h1", { className: "text-3xl font-bold", children: itinerary.destination }), itinerary.audit_passed && (_jsx("span", { className: "text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full", children: "Bias audit passed \u2713" }))] }), itinerary.days.map((day) => (_jsx(DayCard, { day: day }, day.day_number))), _jsx("div", { className: "max-w-2xl mx-auto mt-8 mb-12 px-4", children: _jsxs("div", { className: "border rounded-2xl p-4 bg-gray-50", children: [_jsx("p", { className: "text-sm font-medium text-gray-700 mb-3", children: "\uD83D\uDD27 Want to tweak your itinerary?" }), _jsxs("div", { className: "flex gap-2", children: [_jsx("input", { className: "flex-1 border rounded-xl px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white", placeholder: 'e.g. "Add more food stops" or "Make it more adventurous"', value: refineInput, onChange: (e) => setRefineInput(e.target.value), onKeyDown: (e) => e.key === "Enter" && handleRefine(), disabled: refining }), _jsx("button", { className: "bg-blue-600 text-white px-4 py-2 rounded-xl text-sm font-medium hover:bg-blue-700 disabled:opacity-50", onClick: handleRefine, disabled: refining || !refineInput.trim(), children: refining ? "Updating..." : "Refine" })] }), _jsx("p", { className: "text-xs text-gray-400 mt-2", children: "Your emotional profile will be preserved \u2014 only the stops will change." })] }) })] }));
}
function DayCard({ day }) {
    return (_jsxs("div", { className: "border rounded-xl p-4 flex flex-col gap-3", children: [_jsxs("div", { children: [_jsxs("h2", { className: "text-lg font-semibold", children: ["Day ", day.day_number] }), _jsxs("p", { className: "text-sm text-gray-500", children: [day.date, " \u00B7 ", day.theme] })] }), day.stops.map((stop, i) => (_jsx(StopCard, { stop: stop }, i)))] }));
}
function StopCard({ stop }) {
    const tierColors = {
        hidden_gem: "bg-emerald-100 text-emerald-800",
        local_favourite: "bg-blue-100 text-blue-800",
        well_known: "bg-gray-100 text-gray-700",
        tourist_trap: "bg-red-100 text-red-700",
    };
    return (_jsxs("div", { className: "flex flex-col gap-1 pl-4 border-l-2 border-gray-200", children: [_jsxs("div", { className: "flex items-center gap-2", children: [_jsx("span", { className: "font-medium", children: stop.name }), _jsx("span", { className: `text-xs px-2 py-0.5 rounded-full ${tierColors[stop.popularity_tier]}`, children: stop.popularity_tier.replace("_", " ") })] }), _jsxs("p", { className: "text-xs text-gray-500", children: [stop.category, " \u00B7 ", stop.duration_minutes, " min"] }), stop.teb_explanation && (_jsxs("p", { className: "text-xs italic text-gray-400", children: ["\uD83D\uDCA1 ", stop.teb_explanation] }))] }));
}
