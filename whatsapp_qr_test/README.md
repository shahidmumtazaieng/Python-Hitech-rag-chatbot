# WhatsApp QR Code Testing for Hi-Tech Flow

This separate folder contains a Node.js application that uses WhatsApp Web API to test the Hi-Tech Industrial Group customer support flow via QR code authentication.

## Features

- **QR Code Authentication**: Connect to WhatsApp by scanning a QR code
- **Full Flow Implementation**: All steps from the `chatflow_complete.json` are implemented
- **Real WhatsApp Testing**: Test the flow on actual WhatsApp conversations
- **Session Management**: Maintains user sessions across conversations
- **Interactive Elements**: Supports buttons, lists, and text input forms

## Prerequisites

- Node.js (v14 or higher)
- WhatsApp account for testing
- Internet connection

## Installation

1. Navigate to this folder:
   ```bash
   cd whatsapp_qr_test
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

## Usage

1. Start the application:
   ```bash
   npm start
   ```

2. The application will generate a QR code in the terminal. Scan it with WhatsApp on your phone:
   - Open WhatsApp on your phone
   - Go to Settings → Linked Devices
   - Tap "Link a Device"
   - Scan the QR code displayed in the terminal

3. Once connected, the bot will be ready to handle messages.

4. Test the flow by sending messages to any WhatsApp contact or have them message you.

## How It Works

- **QR Authentication**: Uses `whatsapp-web.js` to authenticate via QR code
- **Session Tracking**: Each user has their own session state
- **Flow Navigation**: Messages navigate through the predefined flow steps
- **Interactive Responses**: Sends appropriate WhatsApp interactive messages (buttons, lists)
- **Fallback Handling**: Handles unrecognized inputs gracefully

## Flow Steps Supported

- Welcome message with language selection
- Main menu with 7 specialized divisions
- Detailed sub-menus for each service area
- Quotation forms for all products/services
- Human handoff for complex inquiries
- Document/video sharing
- Site visit scheduling

## Testing the Flow

1. Start a conversation by sending any message
2. The bot will start with the welcome message
3. Follow the interactive buttons and lists
4. For text forms, provide sample information
5. Test different branches of the conversation tree

## File Structure

```
whatsapp_qr_test/
├── package.json          # Node.js dependencies
├── index.js             # Main application logic
└── README.md            # This file
```

## Troubleshooting

- **QR Code Issues**: Make sure your phone has a stable internet connection
- **Authentication Errors**: Delete the `.wwebjs_auth` folder and restart if authentication fails
- **Message Handling**: Check console logs for any errors in message processing

## Security Notes

- This is for testing purposes only
- The authentication data is stored locally in `.wwebjs_auth`
- Do not use this in production without proper security measures
- Consider the WhatsApp Terms of Service for automated messaging

## Integration with Cloud API

This QR testing setup complements the WhatsApp Cloud API implementation by allowing:

- **Parallel Testing**: Test flows simultaneously on both platforms
- **Real User Experience**: Experience the exact WhatsApp interface
- **Flow Validation**: Ensure the JSON flow works correctly
- **Development Iteration**: Quick testing during development

Use this alongside your Cloud API implementation for comprehensive testing coverage.