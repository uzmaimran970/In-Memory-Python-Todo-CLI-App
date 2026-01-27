'use client';

import { useState, memo, useCallback } from 'react';

interface TagInputProps {
  tags: string[];
  onChange: (tags: string[]) => void;
  disabled?: boolean;
  placeholder?: string;
  maxTags?: number;
}

function TagInput({
  tags,
  onChange,
  disabled = false,
  placeholder = 'Add tag...',
  maxTags = 10,
}: TagInputProps) {
  const [input, setInput] = useState('');

  const addTag = useCallback(() => {
    const tag = input.trim().toLowerCase();
    if (tag && !tags.includes(tag) && tags.length < maxTags) {
      onChange([...tags, tag]);
      setInput('');
    }
  }, [input, tags, onChange, maxTags]);

  const removeTag = useCallback((tagToRemove: string) => {
    onChange(tags.filter(t => t !== tagToRemove));
  }, [tags, onChange]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addTag();
    } else if (e.key === 'Backspace' && input === '' && tags.length > 0) {
      removeTag(tags[tags.length - 1]);
    }
  };

  return (
    <div className="w-full">
      <label className="block text-sm font-medium text-gray-700 mb-1.5">
        Tags
      </label>
      <div className={`flex flex-wrap gap-1.5 p-2 rounded-lg border border-gray-300 focus-within:ring-4 focus-within:ring-indigo-100 focus-within:border-indigo-600 transition-all duration-200 ${disabled ? 'opacity-50 bg-gray-50' : 'bg-white'}`}>
        {tags.map((tag) => (
          <span
            key={tag}
            className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-indigo-100 text-indigo-700"
          >
            #{tag}
            {!disabled && (
              <button
                type="button"
                onClick={() => removeTag(tag)}
                className="ml-0.5 text-indigo-500 hover:text-indigo-800 font-bold"
              >
                x
              </button>
            )}
          </span>
        ))}
        {tags.length < maxTags && (
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            onBlur={addTag}
            placeholder={tags.length === 0 ? placeholder : ''}
            disabled={disabled}
            className="flex-1 min-w-[100px] outline-none text-sm py-1 bg-transparent"
          />
        )}
      </div>
      <p className="mt-1 text-xs text-gray-500">{tags.length}/{maxTags} tags. Press Enter to add.</p>
    </div>
  );
}

export default memo(TagInput);
