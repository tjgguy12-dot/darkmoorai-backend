import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { motion } from 'framer-motion';

interface MarkdownRendererProps {
  content: string;
}

const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({ content }) => {
  return (
    <ReactMarkdown
      children={content}
      components={{
        h1: ({ node, ...props }) => (
          <h1 className="markdown-h1" {...props} />
        ),
        h2: ({ node, ...props }) => (
          <h2 className="markdown-h2" {...props} />
        ),
        h3: ({ node, ...props }) => (
          <h3 className="markdown-h3" {...props} />
        ),
        p: ({ node, ...props }) => (
          <p className="markdown-p" {...props} />
        ),
        strong: ({ node, ...props }) => (
          <strong className="markdown-strong" {...props} />
        ),
        em: ({ node, ...props }) => (
          <em className="markdown-em" {...props} />
        ),
        ul: ({ node, ...props }) => (
          <ul className="markdown-ul" {...props} />
        ),
        ol: ({ node, ...props }) => (
          <ol className="markdown-ol" {...props} />
        ),
        li: ({ node, ...props }) => (
          <li className="markdown-li" {...props} />
        ),
        blockquote: ({ node, ...props }) => (
          <blockquote className="markdown-blockquote" {...props} />
        ),
        code: ({ node, inline, className, children, ...props }: any) => {
          const match = /language-(\w+)/.exec(className || '');
          return !inline && match ? (
            <SyntaxHighlighter
              style={vscDarkPlus}
              language={match[1]}
              PreTag="div"
              className="markdown-code"
              {...props}
            >
              {String(children).replace(/\n$/, '')}
            </SyntaxHighlighter>
          ) : (
            <code className="markdown-inline-code" {...props}>
              {children}
            </code>
          );
        },
        a: ({ node, ...props }) => (
          <motion.a
            className="markdown-link"
            target="_blank"
            rel="noopener noreferrer"
            whileHover={{ color: '#8B7DF2' }}
            {...props}
          />
        ),
        hr: ({ node, ...props }) => (
          <hr className="markdown-hr" {...props} />
        ),
      }}
    />
  );
};

export default MarkdownRenderer;