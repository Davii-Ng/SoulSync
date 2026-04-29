// Chat bubble with distinct user/AI styling

import type { Message } from "../../types";

interface Props {
  message: Message;
  voiceName?: string | null;
}

export function MessageBubble({ message, voiceName }: Props) {
  const isUser = message.role === "user";
  return (
    <div
      className={`flex msg-enter px-3 py-1.5 ${isUser ? "justify-start" : "justify-end"}`}
    >
      <div
        className={`max-w-[85%] rounded-2xl text-sm leading-relaxed ${
          isUser ? "bubble-user px-4 py-2.5" : "bubble-ai px-5 py-4"
        }`}
      >
        <span className="text-xs font-medium block mb-1 text-soul-text-muted">
          {isUser ? "You" : voiceName || "SoulSync"}
        </span>
        <span className="text-soul-text">{message.content}</span>
      </div>
    </div>
  );
}
