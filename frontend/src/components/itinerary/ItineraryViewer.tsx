import type { ItineraryDay, ItineraryStop } from "@/lib/types";
import { useItinerary } from "@/hooks/useItinerary";
import { useAppStore } from "@/stores/appStore";
import { useState } from "react";
import { refineTrip } from "@/lib/api";

const STATUS_LABELS: Record<string, string> = {
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

  if (!tripId) return <p className="text-gray-500">No active trip.</p>;

  if (error) {
    return (
      <div className="max-w-xl mx-auto mt-16 rounded-2xl border border-red-200 bg-red-50 p-6">
        <h1 className="text-lg font-semibold text-red-900">Could not load itinerary</h1>
        <p className="mt-2 text-sm text-red-700">
          {error instanceof Error ? error.message : "Unknown error"}
        </p>
      </div>
    );
  }

  if (isLoading || !status) {
    return (
      <div className="flex flex-col items-center gap-4 mt-16">
        <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
        <p className="text-gray-600">Preparing your itinerary…</p>
      </div>
    );
  }

  if (status === "failed") {
    return (
      <div className="max-w-xl mx-auto mt-16 rounded-2xl border border-amber-200 bg-amber-50 p-6">
        <h1 className="text-lg font-semibold text-amber-900">Generation failed</h1>
        <p className="mt-2 text-sm text-amber-800">
          The trip could not be generated. Try again from the planner with the same
          destination, or refresh this page if the backend job was just retried.
        </p>
      </div>
    );
  }

  if (status !== "ready") {
    return (
      <div className="flex flex-col items-center gap-4 mt-16">
        <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
        <p className="text-gray-600">{STATUS_LABELS[status] ?? status}</p>
      </div>
    );
  }

  if (!itinerary) {
    return (
      <div className="flex flex-col items-center gap-3 mt-16">
        <div className="w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
        <p className="text-gray-600">Loading itinerary details…</p>
      </div>
    );
  }

  const handleRefine = async () => {
    if (!refineInput.trim() || !tripId) return;
    setRefining(true);
    await refineTrip(tripId, refineInput.trim());
    setRefineInput("");
    setRefining(false);
    // Force page reload to reset polling state
    window.location.reload();
  };
  return (
    <div className="max-w-3xl mx-auto p-4 flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">{itinerary.destination}</h1>
        {itinerary.audit_passed && (
          <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">
            Bias audit passed ✓
          </span>
        )}
      </div>

      {itinerary.days.map((day) => (
        <DayCard key={day.day_number} day={day} />
      ))}
      {/* Refinement chat */}
      <div className="max-w-2xl mx-auto mt-8 mb-12 px-4">
        <div className="border rounded-2xl p-4 bg-gray-50">
          <p className="text-sm font-medium text-gray-700 mb-3">
            🔧 Want to tweak your itinerary?
          </p>
          <div className="flex gap-2">
            <input
              className="flex-1 border rounded-xl px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
              placeholder='e.g. "Add more food stops" or "Make it more adventurous"'
              value={refineInput}
              onChange={(e) => setRefineInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleRefine()}
              disabled={refining}
            />
            <button
              className="bg-blue-600 text-white px-4 py-2 rounded-xl text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
              onClick={handleRefine}
              disabled={refining || !refineInput.trim()}
            >
              {refining ? "Updating..." : "Refine"}
            </button>
          </div>
          <p className="text-xs text-gray-400 mt-2">
            Your emotional profile will be preserved — only the stops will
            change.
          </p>
        </div>
      </div>
    </div>
  );
}

function DayCard({ day }: { day: ItineraryDay }) {
  return (
    <div className="border rounded-xl p-4 flex flex-col gap-3">
      <div>
        <h2 className="text-lg font-semibold">Day {day.day_number}</h2>
        <p className="text-sm text-gray-500">
          {day.date} · {day.theme}
        </p>
      </div>
      {day.stops.map((stop, i) => (
        <StopCard key={i} stop={stop} />
      ))}
    </div>
  );
}

function StopCard({ stop }: { stop: ItineraryStop }) {
  const tierColors: Record<string, string> = {
    hidden_gem: "bg-emerald-100 text-emerald-800",
    local_favourite: "bg-blue-100 text-blue-800",
    well_known: "bg-gray-100 text-gray-700",
    tourist_trap: "bg-red-100 text-red-700",
  };

  return (
    <div className="flex flex-col gap-1 pl-4 border-l-2 border-gray-200">
      <div className="flex items-center gap-2">
        <span className="font-medium">{stop.name}</span>
        <span
          className={`text-xs px-2 py-0.5 rounded-full ${tierColors[stop.popularity_tier]}`}
        >
          {stop.popularity_tier.replace("_", " ")}
        </span>
      </div>
      <p className="text-xs text-gray-500">
        {stop.category} · {stop.duration_minutes} min
      </p>
      {stop.teb_explanation && (
        <p className="text-xs italic text-gray-400">
          💡 {stop.teb_explanation}
        </p>
      )}
    </div>
  );
}
