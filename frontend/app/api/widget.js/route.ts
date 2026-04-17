import { NextRequest, NextResponse } from "next/server";

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const apiUrl = searchParams.get("apiUrl") || process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const primaryColor = searchParams.get("primaryColor") || "#E30613";
  const position = searchParams.get("position") || "bottom-right";

  const widgetCode = `
(function() {
  'use strict';
  
  const CONFIG = {
    apiUrl: '${apiUrl}',
    primaryColor: '${primaryColor}',
    position: '${position}',
    companyName: 'Hitech Steel Industries',
    botName: 'Hitech Assistant',
    welcomeMessage: 'Hello! Welcome to Hitech Steel Industries. How can I help you today?',
    sessionTTL: 24 * 60 * 60 * 1000
  };

  const SESSION_KEY = 'hitech_chat_session';
  
  let state = {
    isOpen: false,
    sessionId: null,
    leadInfo: null,
    messages: [],
    isTyping: false,
    hasSubmittedLead: false
  };

  // Load session
  function loadSession() {
    try {
      const saved = localStorage.getItem(SESSION_KEY);
      if (!saved) return false;
      const sessionData = JSON.parse(saved);
      const age = Date.now() - (sessionData.timestamp || 0);
      if (age > CONFIG.sessionTTL) {
        localStorage.removeItem(SESSION_KEY);
        return false;
      }
      state.sessionId = sessionData.sessionId;
      state.leadInfo = sessionData.leadInfo;
      state.messages = sessionData.messages || [];
      state.hasSubmittedLead = true;
      return true;
    } catch (e) {
      return false;
    }
  }

  function saveSession() {
    if (!state.sessionId) return;
    const sessionData = {
      sessionId: state.sessionId,
      leadInfo: state.leadInfo,
      messages: state.messages,
      timestamp: Date.now()
    };
    localStorage.setItem(SESSION_KEY, JSON.stringify(sessionData));
  }

  // API functions
  async function submitLead(leadData) {
    const response = await fetch(\`\${CONFIG.apiUrl}/api/lead\`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(leadData)
    });
    return response.json();
  }

  async function sendMessage(message) {
    const response = await fetch(\`\${CONFIG.apiUrl}/api/chat/sync\`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sessionId: state.sessionId, message })
    });
    return response.json();
  }

  async function talkToHuman(notes) {
    const response = await fetch(\`\${CONFIG.apiUrl}/api/talk-to-human\`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ sessionId: state.sessionId, notes })
    });
    return response.json();
  }

  // Create widget HTML
  function createWidget() {
    const widget = document.createElement('div');
    widget.id = 'hitech-chat-widget';
    widget.innerHTML = \`
      <style>
        #hitech-chat-container {
          position: fixed;
          \${CONFIG.position.includes('bottom') ? 'bottom: 80px' : 'top: 80px'};
          \${CONFIG.position.includes('right') ? 'right: 20px' : 'left: 20px'};
          width: 380px;
          height: 600px;
          background: white;
          border-radius: 16px;
          box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
          display: none;
          flex-direction: column;
          overflow: hidden;
          z-index: 9999;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        #hitech-chat-container.active { display: flex; }
        #hitech-chat-header {
          background: linear-gradient(135deg, \${CONFIG.primaryColor} 0%, #C00510 100%);
          color: white;
          padding: 16px;
          display: flex;
          align-items: center;
          justify-content: space-between;
        }
        #hitech-chat-toggle {
          position: fixed;
          \${CONFIG.position.includes('bottom') ? 'bottom: 20px' : 'top: 20px'};
          \${CONFIG.position.includes('right') ? 'right: 20px' : 'left: 20px'};
          width: 56px;
          height: 56px;
          background: linear-gradient(135deg, \${CONFIG.primaryColor} 0%, #C00510 100%);
          border-radius: 50%;
          border: none;
          cursor: pointer;
          box-shadow: 0 4px 12px rgba(227, 6, 19, 0.3);
          z-index: 10000;
          display: flex;
          align-items: center;
          justify-content: center;
        }
        #hitech-chat-toggle svg { width: 24px; height: 24px; color: white; }
        .hitech-messages { flex: 1; overflow-y: auto; padding: 16px; background: #F8F9FA; }
        .hitech-input-area { padding: 16px; background: white; border-top: 1px solid #E8EAED; }
        .hitech-message { display: flex; gap: 8px; margin-bottom: 12px; max-width: 85%; }
        .hitech-message.user { margin-left: auto; flex-direction: row-reverse; }
        .hitech-message-content { padding: 12px 16px; border-radius: 16px; font-size: 14px; }
        .hitech-message.user .hitech-message-content { background: white; color: #202124; border-bottom-right-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .hitech-message.bot .hitech-message-content { background: linear-gradient(135deg, \${CONFIG.primaryColor} 0%, #C00510 100%); color: white; border-bottom-left-radius: 4px; }
      </style>
      
      <button id="hitech-chat-toggle">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
        </svg>
      </button>
      
      <div id="hitech-chat-container">
        <div id="hitech-chat-header">
          <div style="display: flex; align-items: center; gap: 12px;">
            <div style="width: 40px; height: 40px; background: rgba(255,255,255,0.2); border-radius: 12px; display: flex; align-items: center; justify-content: center;">
              <svg style="width: 24px; height: 24px; color: white;" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
              </svg>
            </div>
            <div>
              <h3 style="margin: 0; font-weight: 600;">\${CONFIG.botName}</h3>
              <p style="margin: 0; font-size: 12px; opacity: 0.8;">Online</p>
            </div>
          </div>
          <button id="hitech-chat-close" style="background: none; border: none; color: white; cursor: pointer; padding: 8px;">
            <svg style="width: 20px; height: 20px;" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div id="hitech-chat-content" style="flex: 1; display: flex; flex-direction: column; overflow: hidden;">
          <!-- Content will be injected here -->
        </div>
      </div>
    \`;
    
    document.body.appendChild(widget);
    return widget;
  }

  // Initialize
  function init() {
    loadSession();
    const widget = createWidget();
    
    const toggle = document.getElementById('hitech-chat-toggle');
    const container = document.getElementById('hitech-chat-container');
    const closeBtn = document.getElementById('hitech-chat-close');
    
    toggle.addEventListener('click', () => {
      state.isOpen = !state.isOpen;
      container.classList.toggle('active');
      if (state.isOpen && !state.hasSubmittedLead) {
        showLeadForm();
      } else if (state.isOpen) {
        showChat();
      }
    });
    
    closeBtn.addEventListener('click', () => {
      state.isOpen = false;
      container.classList.remove('active');
    });
  }

  function showLeadForm() {
    const content = document.getElementById('hitech-chat-content');
    content.innerHTML = \`
      <div style="padding: 24px; overflow-y: auto;">
        <div style="text-align: center; margin-bottom: 24px;">
          <div style="width: 64px; height: 64px; background: linear-gradient(135deg, \${CONFIG.primaryColor} 0%, #C00510 100%); border-radius: 16px; margin: 0 auto 16px; display: flex; align-items: center; justify-content: center;">
            <svg style="width: 32px; height: 32px; color: white;" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
            </svg>
          </div>
          <h2 style="margin: 0 0 8px; font-size: 20px;">Get Started</h2>
          <p style="margin: 0; color: #666; font-size: 14px;">Please provide your details so we can assist you better.</p>
        </div>
        <form id="hitech-lead-form" style="display: flex; flex-direction: column; gap: 16px;">
          <div>
            <label style="display: block; font-size: 13px; font-weight: 500; margin-bottom: 6px;">Full Name *</label>
            <input type="text" name="fullName" required style="width: 100%; padding: 12px; border: 2px solid #E8EAED; border-radius: 10px; font-size: 14px; box-sizing: border-box;">
          </div>
          <div>
            <label style="display: block; font-size: 13px; font-weight: 500; margin-bottom: 6px;">Email Address *</label>
            <input type="email" name="email" required style="width: 100%; padding: 12px; border: 2px solid #E8EAED; border-radius: 10px; font-size: 14px; box-sizing: border-box;">
          </div>
          <div>
            <label style="display: block; font-size: 13px; font-weight: 500; margin-bottom: 6px;">Phone Number *</label>
            <input type="tel" name="phone" required placeholder="+966 5xxxxxxxx" style="width: 100%; padding: 12px; border: 2px solid #E8EAED; border-radius: 10px; font-size: 14px; box-sizing: border-box;">
          </div>
          <div>
            <label style="display: block; font-size: 13px; font-weight: 500; margin-bottom: 6px;">Company (Optional)</label>
            <input type="text" name="company" style="width: 100%; padding: 12px; border: 2px solid #E8EAED; border-radius: 10px; font-size: 14px; box-sizing: border-box;">
          </div>
          <button type="submit" style="width: 100%; padding: 14px; background: linear-gradient(135deg, \${CONFIG.primaryColor} 0%, #C00510 100%); color: white; border: none; border-radius: 10px; font-size: 16px; font-weight: 600; cursor: pointer;">Start Conversation</button>
          <p style="font-size: 11px; color: #888; text-align: center; margin: 0;">By submitting, you agree to our privacy policy.</p>
        </form>
      </div>
    \`;
    
    document.getElementById('hitech-lead-form').addEventListener('submit', async (e) => {
      e.preventDefault();
      const formData = new FormData(e.target);
      const leadData = {
        fullName: formData.get('fullName'),
        email: formData.get('email'),
        phone: formData.get('phone'),
        company: formData.get('company')
      };
      
      try {
        const result = await submitLead(leadData);
        if (result.success) {
          state.sessionId = result.sessionId;
          state.leadInfo = result.lead;
          state.hasSubmittedLead = true;
          saveSession();
          showChat();
        }
      } catch (err) {
        alert('Failed to submit. Please try again.');
      }
    });
  }

  function showChat() {
    const content = document.getElementById('hitech-chat-content');
    content.innerHTML = \`
      <div class="hitech-messages" id="hitech-messages"></div>
      <div class="hitech-input-area">
        <div style="display: flex; gap: 8px;">
          <input type="text" id="hitech-message-input" placeholder="Type your message..." style="flex: 1; padding: 12px; border: 2px solid #E8EAED; border-radius: 10px; font-size: 14px;">
          <button id="hitech-send-btn" style="padding: 12px 16px; background: linear-gradient(135deg, \${CONFIG.primaryColor} 0%, #C00510 100%); color: white; border: none; border-radius: 10px; cursor: pointer;">
            <svg style="width: 20px; height: 20px;" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </button>
        </div>
      </div>
    \`;
    
    renderMessages();
    
    document.getElementById('hitech-send-btn').addEventListener('click', handleSend);
    document.getElementById('hitech-message-input').addEventListener('keypress', (e) => {
      if (e.key === 'Enter') handleSend();
    });
  }

  function renderMessages() {
    const container = document.getElementById('hitech-messages');
    if (!container) return;
    
    container.innerHTML = state.messages.map(msg => \`
      <div class="hitech-message \${msg.isUser ? 'user' : 'bot'}">
        <div class="hitech-message-content">\${msg.content}</div>
      </div>
    \`).join('');
    
    container.scrollTop = container.scrollHeight;
  }

  async function handleSend() {
    const input = document.getElementById('hitech-message-input');
    const message = input.value.trim();
    if (!message) return;
    
    state.messages.push({ content: message, isUser: true });
    renderMessages();
    input.value = '';
    
    try {
      const result = await sendMessage(message);
      state.messages.push({ content: result.response, isUser: false });
      saveSession();
      renderMessages();
    } catch (err) {
      state.messages.push({ 
        content: 'Sorry, I could not process your message. Please try again.', 
        isUser: false 
      });
      renderMessages();
    }
  }

  // Start
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
`;

  return new NextResponse(widgetCode, {
    headers: {
      "Content-Type": "application/javascript",
      "Cache-Control": "public, max-age=3600",
    },
  });
}
