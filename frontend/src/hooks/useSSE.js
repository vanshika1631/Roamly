import { useCallback, useRef, useState } from "react";
import { streamIntakeMessage } from "@/lib/api";
export function useSSE(onComplete) {
    const [streamingText, setStreamingText] = useState("");
    const [isStreaming, setIsStreaming] = useState(false);
    const cancelRef = useRef(null);
    const bufferRef = useRef("");
    const sendMessage = useCallback((messages) => {
        bufferRef.current = "";
        setStreamingText("");
        setIsStreaming(true);
        cancelRef.current = streamIntakeMessage(messages, (token) => {
            bufferRef.current += token;
            setStreamingText(bufferRef.current);
        }, () => {
            setIsStreaming(false);
            onComplete(bufferRef.current);
        }, (err) => {
            console.error("SSE error:", err);
            setIsStreaming(false);
        });
    }, [onComplete]);
    const cancel = useCallback(() => {
        cancelRef.current?.();
        setIsStreaming(false);
    }, []);
    return { streamingText, isStreaming, sendMessage, cancel };
}
