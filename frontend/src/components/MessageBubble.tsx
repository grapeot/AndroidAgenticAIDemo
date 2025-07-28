import React from 'react';
import { format } from 'date-fns';
import { MessageBubbleProps, MessageRole } from '../types';

const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const isUser = message.role === MessageRole.USER;
  const isSystem = message.role === MessageRole.SYSTEM;

  const formatTime = (date: Date) => {
    return format(date, 'HH:mm');
  };

  const getStatusIcon = () => {
    switch (message.status) {
      case 'sending':
        return '🕐';
      case 'sent':
        return '✓';
      case 'error':
        return '❌';
      default:
        return '';
    }
  };

  const renderToolCalls = () => {
    if (!message.toolCalls || message.toolCalls.length === 0) {
      return null;
    }

    return (
      <div style={styles.toolCalls}>
        {message.toolCalls.map((toolCall, index) => (
          <div key={index} style={styles.toolCall}>
            <span style={styles.toolIcon}>🔧</span>
            <span style={styles.toolName}>{toolCall.name}</span>
            <span style={styles.toolArgs}>
              {JSON.stringify(toolCall.args)}
            </span>
          </div>
        ))}
      </div>
    );
  };

  if (isSystem) {
    return (
      <div style={styles.systemContainer}>
        <div style={styles.systemMessage}>
          {message.content}
        </div>
      </div>
    );
  }

  return (
    <div style={{
      ...styles.container,
      justifyContent: isUser ? 'flex-end' : 'flex-start',
    }}>
      <div style={{
        ...styles.bubble,
        ...(isUser ? styles.userBubble : styles.assistantBubble),
      }}>
        <div style={styles.content}>
          {message.content}
        </div>
        
        {renderToolCalls()}
        
        <div style={styles.footer}>
          <span style={styles.time}>
            {formatTime(message.timestamp)}
          </span>
          {message.status && (
            <span style={styles.status}>
              {getStatusIcon()}
            </span>
          )}
        </div>
      </div>
    </div>
  );
};

const styles = {
  container: {
    display: 'flex',
    padding: '4px 20px',
    marginBottom: '8px',
  } as React.CSSProperties,
  
  bubble: {
    maxWidth: '70%',
    borderRadius: '18px',
    padding: '12px 16px',
    fontSize: '14px',
    lineHeight: '1.4',
    wordWrap: 'break-word',
  } as React.CSSProperties,
  
  userBubble: {
    backgroundColor: '#007AFF',
    color: 'white',
  } as React.CSSProperties,
  
  assistantBubble: {
    backgroundColor: 'white',
    color: '#333',
    border: '1px solid #e0e0e0',
  } as React.CSSProperties,
  
  content: {
    marginBottom: '4px',
  } as React.CSSProperties,
  
  toolCalls: {
    marginTop: '8px',
    marginBottom: '4px',
  } as React.CSSProperties,
  
  toolCall: {
    display: 'flex',
    alignItems: 'center',
    backgroundColor: 'rgba(0, 0, 0, 0.05)',
    borderRadius: '8px',
    padding: '4px 8px',
    fontSize: '12px',
    marginBottom: '4px',
  } as React.CSSProperties,
  
  toolIcon: {
    marginRight: '4px',
  } as React.CSSProperties,
  
  toolName: {
    fontWeight: 'bold',
    marginRight: '8px',
  } as React.CSSProperties,
  
  toolArgs: {
    color: '#666',
    fontFamily: 'monospace',
  } as React.CSSProperties,
  
  footer: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: '4px',
  } as React.CSSProperties,
  
  time: {
    fontSize: '11px',
    opacity: 0.7,
  } as React.CSSProperties,
  
  status: {
    fontSize: '12px',
  } as React.CSSProperties,
  
  systemContainer: {
    display: 'flex',
    justifyContent: 'center',
    padding: '8px 20px',
  } as React.CSSProperties,
  
  systemMessage: {
    backgroundColor: '#fff3cd',
    color: '#856404',
    border: '1px solid #ffeaa7',
    borderRadius: '12px',
    padding: '8px 12px',
    fontSize: '12px',
    textAlign: 'center',
  } as React.CSSProperties,
};

export default MessageBubble;