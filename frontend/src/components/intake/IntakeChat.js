import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useCallback, useState, useEffect, useRef } from "react";
import { useSSE } from "@/hooks/useSSE";
import { finalizeIntake } from "@/lib/api";
import { useAppStore } from "@/stores/appStore";
function renderMarkdown(text) {
    return text
        .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
        .replace(/\*(.*?)\*/g, "<em>$1</em>");
}
export function IntakeChat() {
    const { messages, addMessage, setTeb, userId } = useAppStore((s) => ({
        messages: s.messages,
        addMessage: s.addMessage,
        setTeb: s.setTeb,
        userId: s.userId,
    }));
    const [input, setInput] = useState("");
    const [isFinalized, setIsFinalized] = useState(false);
    const [isFinalizing, setIsFinalizing] = useState(false);
    const bottomRef = useRef(null);
    const handleComplete = useCallback((fullText) => {
        addMessage({ role: "assistant", content: fullText });
    }, [addMessage]);
    const { streamingText, isStreaming, sendMessage } = useSSE(handleComplete);
    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages, streamingText]);
    const handleSend = () => {
        if (!input.trim() || isStreaming)
            return;
        const userMsg = { role: "user", content: input.trim() };
        addMessage(userMsg);
        setInput("");
        sendMessage([...messages, userMsg]);
    };
    const handleFinalize = async () => {
        setIsFinalizing(true);
        const teb = await finalizeIntake(userId ?? "test-user-1", messages);
        setTeb(teb);
        setIsFinalized(true);
        setIsFinalizing(false);
    };
    return (_jsxs("div", { className: "flex flex-col h-screen max-w-2xl mx-auto p-4", children: [_jsxs("div", { className: "py-4 border-b mb-4", children: [_jsx("h1", { className: "text-2xl font-bold text-gray-900", children: "Plan your trip \u2708" }), _jsx("p", { className: "text-sm text-gray-500", children: "Tell us how you're feeling and we'll build your emotional travel profile" })] }), _jsxs("div", { className: "flex-1 overflow-y-auto flex flex-col gap-3 pb-4", children: [messages.length === 0 && (_jsx("p", { className: "text-gray-400 text-sm text-center mt-8", children: "Start by telling us how you're feeling about this trip..." })), messages.map((msg, i) => (_jsx("div", { className: `flex ${msg.role === "user" ? "justify-end" : "justify-start"}`, children: _jsx("div", { className: `rounded-2xl px-4 py-3 max-w-prose text-sm leading-relaxed ${msg.role === "user"
                                ? "bg-blue-600 text-white rounded-br-sm"
                                : "bg-gray-100 text-gray-900 rounded-bl-sm"}`, dangerouslySetInnerHTML: { __html: renderMarkdown(msg.content) } }) }, i))), isStreaming && streamingText && (_jsx("div", { className: "flex justify-start", children: _jsx("div", { className: "bg-gray-100 text-gray-900 rounded-2xl rounded-bl-sm px-4 py-3 max-w-prose text-sm leading-relaxed", dangerouslySetInnerHTML: { __html: renderMarkdown(streamingText) } }) })), isStreaming && !streamingText && (_jsx("div", { className: "flex justify-start", children: _jsx("div", { className: "bg-gray-100 rounded-2xl px-4 py-3", children: _jsxs("span", { className: "flex gap-1", children: [_jsx("span", { className: "w-2 h-2 bg-gray-400 rounded-full animate-bounce", style: { animationDelay: "0ms" } }), _jsx("span", { className: "w-2 h-2 bg-gray-400 rounded-full animate-bounce", style: { animationDelay: "150ms" } }), _jsx("span", { className: "w-2 h-2 bg-gray-400 rounded-full animate-bounce", style: { animationDelay: "300ms" } })] }) }) })), _jsx("div", { ref: bottomRef })] }), !isFinalized ? (_jsxs("div", { className: "border-t pt-4 flex flex-col gap-2", children: [_jsxs("div", { className: "flex gap-2", children: [_jsx("input", { className: "flex-1 border rounded-xl px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500", value: input, onChange: (e) => setInput(e.target.value), onKeyDown: (e) => e.key === "Enter" && handleSend(), placeholder: "Tell us how you're feeling about this trip...", disabled: isStreaming }), _jsx("button", { className: "bg-blue-600 text-white px-4 py-2 rounded-xl text-sm font-medium disabled:opacity-50 hover:bg-blue-700", onClick: handleSend, disabled: isStreaming || !input.trim(), children: "Send" })] }), messages.length >= 5 && (_jsx("button", { className: "w-full bg-green-600 text-white py-2 rounded-xl text-sm font-medium hover:bg-green-700 disabled:opacity-50", onClick: handleFinalize, disabled: isFinalizing, children: isFinalizing ? "Building your profile..." : "Build my travel profile →" }))] })) : (_jsxs("div", { className: "border-t pt-4 text-center", children: [_jsx("p", { className: "text-green-600 font-medium", children: "\u2705 Travel profile created!" }), _jsx("a", { href: "/plan", className: "text-blue-600 text-sm underline mt-1 block", children: "Continue to plan your trip \u2192" })] }))] }));
}
