import { useCallback, useRef, useState } from "react";
import { streamIntakeMessage } from "@/lib/api";
import type { ConversationMessage } from "@/lib/types";

interface UseSSEReturn {
  streamingText: string;
  isStreaming: boolean;
  sendMessage: (messages: ConversationMessage[]) => void;
  cancel: () => void;
}

export function useSSE(onComplete: (fullText: string) => void): UseSSEReturn {
  const [streamingText, setStreamingText] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const cancelRef = useRef<(() => void) | null>(null);
  const bufferRef = useRef("");

  const sendMessage = useCallback(
    (messages: ConversationMessage[]) => {
      bufferRef.current = "";
      setStreamingText("");
      setIsStreaming(true);

      cancelRef.current = streamIntakeMessage(
        messages,
        (token) => {
          bufferRef.current += token;
          setStreamingText(bufferRef.current);
        },
        () => {
          setIsStreaming(false);
          onComplete(bufferRef.current);
        },
        (err) => {
          console.error("SSE error:", err);
          setIsStreaming(false);
        }
      );
    },
    [onComplete]
  );

  const cancel = useCallback(() => {
    cancelRef.current?.();
    setIsStreaming(false);
  }, []);

  return { streamingText, isStreaming, sendMessage, cancel };
}
