import React from 'react';
import { LoadingIndicatorProps } from '../types';

const LoadingIndicator: React.FC<LoadingIndicatorProps> = ({ type, message }) => {
  const getLoadingText = () => {
    if (message) return message;
    
    switch (type) {
      case 'typing':
        return 'AI 正在思考...';
      case 'searching':
        return '正在搜索相关信息...';
      case 'processing':
        return '正在处理您的请求...';
      default:
        return '加载中...';
    }
  };

  const getIcon = () => {
    switch (type) {
      case 'searching':
        return '🔍';
      case 'processing':
        return '⚙️';
      case 'typing':
      default:
        return '💭';
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.content}>
        <span style={styles.icon}>{getIcon()}</span>
        <span style={styles.text}>{getLoadingText()}</span>
        <div style={styles.dots}>
          <span style={{ ...styles.dot, animationDelay: '0ms' }}>.</span>
          <span style={{ ...styles.dot, animationDelay: '150ms' }}>.</span>
          <span style={{ ...styles.dot, animationDelay: '300ms' }}>.</span>
        </div>
      </div>
    </div>
  );
};

const styles = {
  container: {
    display: 'flex',
    justifyContent: 'flex-start',
    padding: '10px 20px',
  } as React.CSSProperties,
  
  content: {
    display: 'flex',
    alignItems: 'center',
    backgroundColor: '#f0f0f0',
    borderRadius: '18px',
    padding: '8px 16px',
    fontSize: '14px',
    color: '#666',
  } as React.CSSProperties,
  
  icon: {
    marginRight: '8px',
    fontSize: '16px',
  } as React.CSSProperties,
  
  text: {
    marginRight: '4px',
  } as React.CSSProperties,
  
  dots: {
    display: 'inline-flex',
  } as React.CSSProperties,
  
  dot: {
    animation: 'loading-blink 1.4s infinite both',
    fontSize: '16px',
    lineHeight: '1',
  } as React.CSSProperties,
};

// 添加 CSS 动画
const style = document.createElement('style');
style.textContent = `
  @keyframes loading-blink {
    0%, 80%, 100% {
      opacity: 0;
    }
    40% {
      opacity: 1;
    }
  }
`;
document.head.appendChild(style);

export default LoadingIndicator;