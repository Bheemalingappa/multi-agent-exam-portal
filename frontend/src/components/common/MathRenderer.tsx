import React, { useEffect, useRef } from 'react';
import katex from 'katex';
import 'katex/dist/katex.min.css';

interface Props {
  content: string;
  className?: string;
}

export const MathRenderer: React.FC<Props> = ({ content, className = '' }) => {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    // Parse LaTeX inline \(...\) or display \[...\] or $...$
    const raw = content || '';
    
    // Convert LaTeX math delimiters into HTML rendered by KaTeX
    let parsedHtml = raw;

    // Replace display math \[ ... \] or $$ ... $$
    parsedHtml = parsedHtml.replace(/\\\[(.*?)\\\]|\$\$(.*?)\$\$/gs, (_, match1, match2) => {
      const expr = match1 || match2;
      try {
        return `<div class="my-2 text-center">${katex.renderToString(expr.trim(), { displayMode: true, throwOnError: false })}</div>`;
      } catch (err) {
        return expr;
      }
    });

    // Replace inline math \( ... \) or $ ... $
    parsedHtml = parsedHtml.replace(/\\\((.*?)\\\)|\$(.*?)\$/g, (_, match1, match2) => {
      const expr = match1 || match2;
      try {
        return katex.renderToString(expr.trim(), { displayMode: false, throwOnError: false });
      } catch (err) {
        return expr;
      }
    });

    containerRef.current.innerHTML = parsedHtml;
  }, [content]);

  return <div ref={containerRef} className={`inline-block ${className}`} />;
};
