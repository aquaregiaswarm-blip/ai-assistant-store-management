import type { SuggestedQuery } from '../../types';

interface SuggestedQueriesProps {
  queries: SuggestedQuery[];
  onSelect: (query: string) => void;
}

export default function SuggestedQueries({ queries, onSelect }: SuggestedQueriesProps) {
  return (
    <div className="flex flex-wrap justify-center gap-2 max-w-md">
      {queries.slice(0, 6).map((query, index) => (
        <button
          key={index}
          onClick={() => onSelect(query.text)}
          className="px-3 py-1.5 text-xs bg-gray-100 hover:bg-swig-pink-light hover:text-swig-pink-dark text-gray-600 rounded-full transition-colors"
        >
          {query.text}
        </button>
      ))}
    </div>
  );
}
