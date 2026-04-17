import { ChatWidget } from "@/components/chat/ChatWidget";

export default function ChatPage() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md h-[80vh]">
        <ChatWidget embedded={true} />
      </div>
    </main>
  );
}
