const BASE = import.meta.env.VITE_API_URL ?? "";
async function json(path, init) {
    const res = await fetch(`${BASE}${path}`, {
        headers: { "Content-Type": "application/json" },
        ...init,
    });
    if (!res.ok) {
        const err = await res.text();
        throw new Error(`API ${res.status}: ${err}`);
    }
    return res.json();
}
// ── Intake ────────────────────────────────────────────────────────────────────
/**
 * Opens an SSE connection to the intake message endpoint.
 * Returns an EventSource-like cleanup function.
 */
export function streamIntakeMessage(messages, onToken, onDone, onError) {
    const controller = new AbortController();
    fetch(`${BASE}/api/intake/message`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages }),
        signal: controller.signal,
    })
        .then(async (res) => {
        if (!res.body)
            throw new Error("No response body");
        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        while (true) {
            const { done, value } = await reader.read();
            if (done)
                break;
            const chunk = decoder.decode(value);
            for (const line of chunk.split("\n")) {
                if (line.startsWith("data: ")) {
                    const data = line.slice(6);
                    if (data === "[DONE]") {
                        onDone();
                        return;
                    }
                    onToken(data);
                }
            }
        }
        onDone();
    })
        .catch((err) => {
        if (err instanceof Error && err.name !== "AbortError")
            onError(err);
    });
    return () => controller.abort();
}
export function finalizeIntake(userId, conversationHistory) {
    return json("/api/intake/finalize", {
        method: "POST",
        body: JSON.stringify({ user_id: userId, conversation_history: conversationHistory }),
    });
}
// ── Trips ─────────────────────────────────────────────────────────────────────
export function createTrip(userId, constraints, tebSnapshot) {
    return json("/api/trips", {
        method: "POST",
        body: JSON.stringify({
            user_id: userId,
            constraints,
            teb_snapshot: tebSnapshot,
        }),
    });
}
export function getTripStatus(tripId) {
    return json(`/api/trips/${tripId}/status`);
}
export function getItinerary(tripId) {
    return json(`/api/trips/${tripId}/itinerary`);
}
export function refineTrip(tripId, instruction) {
    return json(`/api/trips/${tripId}/refine`, {
        method: "POST",
        body: JSON.stringify({ instruction }),
    });
}
// ── Profile ───────────────────────────────────────────────────────────────────
export function getTEB(userId) {
    return json(`/api/profile/teb?user_id=${userId}`);
}
