import React, { useState, useRef, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { 
  Message, 
  MessageRole, 
  ConnectionStatus, 
  AppState,
  ChatInterfaceProps
} from '../types';
import { StreamingChatManager, SSEEventHandlers } from '../services/api';
import MessageBubble from './MessageBubble';
import LoadingIndicator from './LoadingIndicator';

const ChatInterface: React.FC<ChatInterfaceProps> = () => {
  const [state, setState] = useState<AppState>({
    messages: [],
    currentMessage: '',
    isLoading: false,
    connectionStatus: ConnectionStatus.DISCONNECTED,
    conversationId: uuidv4(),
  });

  const [streamingManager, setStreamingManager] = useState<StreamingChatManager | null>(null);
  const [currentStreamingMessage, setCurrentStreamingMessage] = useState<string>('');
  const [loadingMessage, setLoadingMessage] = useState<string>('');
  const [loadingType, setLoadingType] = useState<'typing' | 'searching' | 'processing'>('typing');
  const [debugLogs, setDebugLogs] = useState<string[]>([]);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // 自动滚动到底部
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // 添加调试日志
  const addDebugLog = (message: string) => {
    const timestamp = new Date().toLocaleTimeString();
    setDebugLogs(prev => {
      const newLogs = [...prev, `[${timestamp}] ${message}`];
      return newLogs.slice(-10); // 只保留最近10条
    });
  };

  useEffect(() => {
    scrollToBottom();
  }, [state.messages, currentStreamingMessage]);

  // 初始化流式管理器
  useEffect(() => {
    const handlers: SSEEventHandlers = {
      onStatus: (message: string) => {
        setLoadingMessage(message);
        setLoadingType('processing');
      },
      
      onToolCall: (toolName: string, args: Record<string, any>) => {
        setLoadingMessage(`正在使用 ${toolName} 工具搜索...`);
        setLoadingType('searching');
        
        // 可以在这里添加工具调用的显示逻辑
        console.log('Tool call:', toolName, args);
      },
      
      onContent: (content: string) => {
        setCurrentStreamingMessage(prev => prev + content);
      },
      
      onError: (error: string) => {
        console.error('Chat error:', error);
        // 显示详细错误信息在界面上
        const detailedError = `连接错误: ${error}`;
        setState(prev => ({
          ...prev,
          error: detailedError,
          isLoading: false,
          connectionStatus: ConnectionStatus.ERROR,
        }));
        setCurrentStreamingMessage('');
        setLoadingMessage('');
      },
      
      onDone: () => {
        // 将流式消息添加到消息列表
        if (currentStreamingMessage.trim()) {
          const assistantMessage: Message = {
            id: uuidv4(),
            role: MessageRole.ASSISTANT,
            content: currentStreamingMessage,
            timestamp: new Date(),
            status: 'sent',
          };
          
          setState(prev => ({
            ...prev,
            messages: [...prev.messages, assistantMessage],
            isLoading: false,
            connectionStatus: ConnectionStatus.DISCONNECTED,
          }));
        } else {
          // 如果没有收到内容，只更新状态
          setState(prev => ({
            ...prev,
            isLoading: false,
            connectionStatus: ConnectionStatus.DISCONNECTED,
          }));
        }
        
        setCurrentStreamingMessage('');
        setLoadingMessage('');
      },
    };

    const manager = new StreamingChatManager(handlers);
    setStreamingManager(manager);

    return () => {
      manager.stopStreaming();
    };
  }, [currentStreamingMessage]);

  const handleSendMessage = async () => {
    const messageText = state.currentMessage.trim();
    if (!messageText || state.isLoading) return;

    // 创建用户消息
    const userMessage: Message = {
      id: uuidv4(),
      role: MessageRole.USER,
      content: messageText,
      timestamp: new Date(),
      status: 'sent',
    };

    // 添加用户消息到列表
    setState(prev => ({
      ...prev,
      messages: [...prev.messages, userMessage],
      currentMessage: '',
      isLoading: true,
      connectionStatus: ConnectionStatus.CONNECTING,
    }));

    // 清空输入框
    setCurrentStreamingMessage('');
    setLoadingMessage('AI 正在思考...');
    setLoadingType('typing');

    // 使用非流式请求进行测试
    try {
      setState(prev => ({
        ...prev,
        connectionStatus: ConnectionStatus.CONNECTED,
      }));

      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          message: messageText, 
          conversation_id: state.conversationId 
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${await response.text()}`);
      }

      const result = await response.json();
      
      // 添加AI回复到消息列表
      const assistantMessage: Message = {
        id: uuidv4(),
        role: MessageRole.ASSISTANT,
        content: result.response || result.content || result.message || '收到空回复',
        timestamp: new Date(),
        status: 'sent',
      };

      setState(prev => ({
        ...prev,
        messages: [...prev.messages, assistantMessage],
        isLoading: false,
        connectionStatus: ConnectionStatus.DISCONNECTED,
      }));

    } catch (error) {
      setState(prev => ({
        ...prev,
        error: `发送消息失败: ${error}`,
        isLoading: false,
        connectionStatus: ConnectionStatus.ERROR,
      }));
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleStopGeneration = () => {
    if (streamingManager) {
      streamingManager.stopStreaming();
    }
    
    setState(prev => ({
      ...prev,
      isLoading: false,
      connectionStatus: ConnectionStatus.DISCONNECTED,
    }));
    
    setCurrentStreamingMessage('');
    setLoadingMessage('');
  };

  const testConnection = async () => {
    setState(prev => ({ ...prev, error: undefined }));
    
    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: 'test', conversation_id: 'test' })
      });
      
      if (response.ok) {
        setState(prev => ({
          ...prev,
          connectionStatus: ConnectionStatus.CONNECTED,
          error: undefined
        }));
        setTimeout(() => {
          setState(prev => ({ ...prev, connectionStatus: ConnectionStatus.DISCONNECTED }));
        }, 2000);
      } else {
        const errorText = await response.text();
        setState(prev => ({
          ...prev,
          connectionStatus: ConnectionStatus.ERROR,
          error: `连接测试失败: ${response.status} - ${errorText}`
        }));
      }
    } catch (error) {
      setState(prev => ({
        ...prev,
        connectionStatus: ConnectionStatus.ERROR,
        error: `连接测试失败: ${error}`
      }));
    }
  };

  return (
    <div style={styles.container}>
      {/* 标题栏 */}
      <div style={styles.header}>
        <h1 style={styles.title}>AI Chat System</h1>
        <div style={styles.status}>
          <span style={{
            ...styles.statusDot,
            backgroundColor: state.connectionStatus === ConnectionStatus.CONNECTED ? '#4CAF50' : 
                           state.connectionStatus === ConnectionStatus.ERROR ? '#f44336' : '#ccc'
          }} />
          <span style={styles.statusText}>
            {state.connectionStatus === ConnectionStatus.CONNECTED ? '已连接' : 
             state.connectionStatus === ConnectionStatus.ERROR ? '连接错误' : '未连接'}
          </span>
          <button 
            onClick={testConnection}
            style={styles.testButton}
          >
            测试连接
          </button>
        </div>
      </div>

      {/* 消息列表 */}
      <div style={styles.messagesContainer}>
        <div style={styles.messagesList}>
          {state.messages.map(message => (
            <MessageBubble key={message.id} message={message} />
          ))}
          
          {/* 流式消息显示 */}
          {currentStreamingMessage && (
            <MessageBubble 
              message={{
                id: 'streaming',
                role: MessageRole.ASSISTANT,
                content: currentStreamingMessage,
                timestamp: new Date(),
              }}
            />
          )}
          
          {/* 加载指示器 */}
          {state.isLoading && !currentStreamingMessage && (
            <LoadingIndicator 
              type={loadingType} 
              message={loadingMessage} 
            />
          )}
          
          {/* 错误消息 */}
          {state.error && (
            <div style={styles.errorMessage}>
              ❌ {state.error}
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* 输入区域 */}
      <div style={styles.inputContainer}>
        <div style={styles.inputWrapper}>
          <input
            ref={inputRef}
            type="text"
            value={state.currentMessage}
            onChange={(e) => setState(prev => ({ ...prev, currentMessage: e.target.value }))}
            onKeyPress={handleKeyPress}
            placeholder="输入消息..."
            style={styles.input}
            disabled={state.isLoading}
          />
          
          {state.isLoading ? (
            <button 
              onClick={handleStopGeneration}
              style={{ ...styles.button, ...styles.stopButton }}
            >
              ⏹️ 停止
            </button>
          ) : (
            <button 
              onClick={handleSendMessage}
              disabled={!state.currentMessage.trim()}
              style={{
                ...styles.button,
                ...styles.sendButton,
                opacity: state.currentMessage.trim() ? 1 : 0.5,
              }}
            >
              📤 发送
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

const styles = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    height: '100vh',
    backgroundColor: '#f5f5f5',
  } as React.CSSProperties,

  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '16px 24px',
    backgroundColor: 'white',
    borderBottom: '1px solid #e0e0e0',
    boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
  } as React.CSSProperties,

  title: {
    margin: 0,
    fontSize: '20px',
    fontWeight: '600',
    color: '#333',
  } as React.CSSProperties,

  status: {
    display: 'flex',
    alignItems: 'center',
  } as React.CSSProperties,

  statusDot: {
    width: '8px',
    height: '8px',
    borderRadius: '50%',
    marginRight: '8px',
  } as React.CSSProperties,

  statusText: {
    fontSize: '14px',
    color: '#666',
  } as React.CSSProperties,

  messagesContainer: {
    flex: 1,
    overflow: 'hidden',
    display: 'flex',
    flexDirection: 'column',
  } as React.CSSProperties,

  messagesList: {
    flex: 1,
    overflowY: 'auto',
    padding: '16px 0',
  } as React.CSSProperties,

  inputContainer: {
    padding: '16px 24px',
    backgroundColor: 'white',
    borderTop: '1px solid #e0e0e0',
  } as React.CSSProperties,

  inputWrapper: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
  } as React.CSSProperties,

  input: {
    flex: 1,
    padding: '12px 16px',
    border: '1px solid #ccc',
    borderRadius: '24px',
    fontSize: '14px',
    outline: 'none',
    backgroundColor: '#f9f9f9',
  } as React.CSSProperties,

  button: {
    padding: '12px 20px',
    borderRadius: '24px',
    border: 'none',
    fontSize: '14px',
    fontWeight: '500',
    cursor: 'pointer',
    transition: 'all 0.2s',
  } as React.CSSProperties,

  sendButton: {
    backgroundColor: '#007AFF',
    color: 'white',
  } as React.CSSProperties,

  stopButton: {
    backgroundColor: '#FF3B30',
    color: 'white',
  } as React.CSSProperties,

  errorMessage: {
    padding: '12px 20px',
    margin: '8px 20px',
    backgroundColor: '#ffebee',
    color: '#c62828',
    borderRadius: '12px',
    fontSize: '14px',
    textAlign: 'center',
  } as React.CSSProperties,

  testButton: {
    marginLeft: '8px',
    padding: '4px 8px',
    fontSize: '12px',
    backgroundColor: '#f0f0f0',
    color: '#666',
    border: '1px solid #ccc',
    borderRadius: '4px',
    cursor: 'pointer',
  } as React.CSSProperties,
};

export default ChatInterface;