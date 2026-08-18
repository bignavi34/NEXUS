"use client";

import { useState } from "react";
import ReactMarkdown from "react-markdown";
import { sendMessage } from "@/lib/api";

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Hello. I'm NEXUS, your personal operating system agent. How can I help you?",
    },
  ]);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSend() {
    const message = input.trim();

    if (!message || loading) {
      return;
    }

    setInput("");

    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        content: message,
      },
    ]);

    setLoading(true);

    try {
      const response = await sendMessage(message);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: response,
        },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            error instanceof Error
              ? `**Error:** ${error.message}`
              : "**Error:** Unable to contact NEXUS.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function handleKeyDown(
    event: React.KeyboardEvent<HTMLTextAreaElement>
  ) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  }

  return (
    <div className="flex h-screen bg-[#0a0a0a] text-white">
      {/* Sidebar */}

      <aside className="hidden w-64 border-r border-white/10 bg-[#0d0d0d] p-4 md:block">
        <div className="mb-8">
          <div className="text-xl font-semibold">
            NEXUS
          </div>

          <div className="mt-1 text-xs text-white/40">
            Personal Operating System
          </div>
        </div>

        <button
          onClick={() =>
            setMessages([
              {
                role: "assistant",
                content:
                  "Hello. I'm NEXUS, your personal operating system agent. How can I help you?",
              },
            ])
          }
          className="w-full rounded-lg border border-white/10 px-4 py-2 text-left text-sm hover:bg-white/5"
        >
          + New conversation
        </button>

        <div className="mt-8">
          <div className="mb-3 text-xs uppercase tracking-wider text-white/30">
            Systems
          </div>

          <div className="space-y-2 text-sm text-white/60">
            <div>🧠 Memory</div>
            <div>📋 Tasks</div>
            <div>📅 Calendar</div>
            <div>📁 Files</div>
            <div>✉️ Email</div>
          </div>
        </div>
      </aside>

      {/* Main */}

      <main className="flex min-w-0 flex-1 flex-col">
        {/* Header */}

        <header className="flex h-16 items-center border-b border-white/10 px-5">
          <div>
            <div className="font-medium">NEXUS</div>

            <div className="flex items-center gap-2 text-xs text-white/40">
              <span className="h-2 w-2 rounded-full bg-green-500" />
              Online
            </div>
          </div>
        </header>

        {/* Messages */}

        <div className="flex-1 overflow-y-auto">
          <div className="mx-auto max-w-4xl px-4 py-8">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`mb-6 flex ${
                  message.role === "user"
                    ? "justify-end"
                    : "justify-start"
                }`}
              >
                <div
                  className={`max-w-[80%] rounded-2xl px-5 py-3 ${
                    message.role === "user"
                      ? "bg-white text-black"
                      : "border border-white/10 bg-[#111111]"
                  }`}
                >
                  <div className="prose prose-invert max-w-none text-sm">
                    <ReactMarkdown>
                      {message.content}
                    </ReactMarkdown>
                  </div>
                </div>
              </div>
            ))}

            {loading && (
              <div className="flex justify-start">
                <div className="rounded-2xl border border-white/10 bg-[#111111] px-5 py-3">
                  <div className="flex items-center gap-2 text-sm text-white/50">
                    <span className="animate-pulse">
                      NEXUS is thinking...
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Composer */}

        <div className="border-t border-white/10 p-4">
          <div className="mx-auto max-w-4xl">
            <div className="flex items-end gap-3 rounded-2xl border border-white/10 bg-[#111111] p-2">
              <textarea
                value={input}
                onChange={(event) =>
                  setInput(event.target.value)
                }
                onKeyDown={handleKeyDown}
                placeholder="Ask NEXUS anything..."
                rows={1}
                disabled={loading}
                className="max-h-40 min-h-12 flex-1 resize-none bg-transparent px-3 py-3 text-sm outline-none placeholder:text-white/30"
              />

              <button
                onClick={handleSend}
                disabled={!input.trim() || loading}
                className="mb-1 rounded-xl bg-white px-4 py-3 text-sm font-medium text-black transition hover:bg-white/90 disabled:cursor-not-allowed disabled:opacity-30"
              >
                Send
              </button>
            </div>

            <div className="mt-2 text-center text-xs text-white/20">
              NEXUS can access your memory, tasks, calendar,
              workspace and email.
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
