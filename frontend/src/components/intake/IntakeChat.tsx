import { useCallback, useState, useEffect, useRef } from "react";
import { useSSE } from "@/hooks/useSSE";
import { finalizeIntake } from "@/lib/api";
import { useAppStore } from "@/stores/appStore";

function renderMarkdown(text: string) {
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
  const bottomRef = useRef<HTMLDivElement>(null);

  const handleComplete = useCallback(
    (fullText: string) => {
      addMessage({ role: "assistant", content: fullText });
    },
    [addMessage]
  );

  const { streamingText, isStreaming, sendMessage } = useSSE(handleComplete);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingText]);

  const handleSend = () => {
    if (!input.trim() || isStreaming) return;
    const userMsg = { role: "user" as const, content: input.trim() };
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

  return (
    <div className="flex flex-col h-screen max-w-2xl mx-auto p-4">
      {/* Header */}
      <div className="py-4 border-b mb-4">
        <h1 className="text-2xl font-bold text-gray-900">Plan your trip ✈</h1>
        <p className="text-sm text-gray-500">Tell us how you're feeling and we'll build your emotional travel profile</p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto flex flex-col gap-3 pb-4">
        {messages.length === 0 && (
          <p className="text-gray-400 text-sm text-center mt-8">
            Start by telling us how you're feeling about this trip...
          </p>
        )}

        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`rounded-2xl px-4 py-3 max-w-prose text-sm leading-relaxed ${
                msg.role === "user"
                  ? "bg-blue-600 text-white rounded-br-sm"
                  : "bg-gray-100 text-gray-900 rounded-bl-sm"
              }`}
              dangerouslySetInnerHTML={{ __html: renderMarkdown(msg.content) }}
            />
          </div>
        ))}

        {/* Streaming */}
        {isStreaming && streamingText && (
          <div className="flex justify-start">
            <div className="bg-gray-100 text-gray-900 rounded-2xl rounded-bl-sm px-4 py-3 max-w-prose text-sm leading-relaxed"
              dangerouslySetInnerHTML={{ __html: renderMarkdown(streamingText) }}
            />
          </div>
        )}

        {isStreaming && !streamingText && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-2xl px-4 py-3">
              <span className="flex gap-1">
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
              </span>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Input */}
      {!isFinalized ? (
        <div className="border-t pt-4 flex flex-col gap-2">
          <div className="flex gap-2">
            <input
              className="flex-1 border rounded-xl px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSend()}
              placeholder="Tell us how you're feeling about this trip..."
              disabled={isStreaming}
            />
            <button
              className="bg-blue-600 text-white px-4 py-2 rounded-xl text-sm font-medium disabled:opacity-50 hover:bg-blue-700"
              onClick={handleSend}
              disabled={isStreaming || !input.trim()}
            >
              Send
            </button>
          </div>

          {messages.length >= 5 && (
            <button
              className="w-full bg-green-600 text-white py-2 rounded-xl text-sm font-medium hover:bg-green-700 disabled:opacity-50"
              onClick={handleFinalize}
              disabled={isFinalizing}
            >
              {isFinalizing ? "Building your profile..." : "Build my travel profile →"}
            </button>
          )}
        </div>
      ) : (
        <div className="border-t pt-4 text-center">
          <p className="text-green-600 font-medium">✅ Travel profile created!</p>
          <a href="/plan" className="text-blue-600 text-sm underline mt-1 block">
            Continue to plan your trip →
          </a>
        </div>
      )}
    </div>
  );
}