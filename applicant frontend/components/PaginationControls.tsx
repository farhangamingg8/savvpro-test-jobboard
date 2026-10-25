interface Props {
  page: number;
  perPage: number;
  total: number;
  onPageChange: (page: number) => void;
}

export function PaginationControls({ page, perPage, total, onPageChange }: Props) {
  const pages = Math.max(1, Math.ceil(total / perPage));
  if (total <= perPage) return null;
  return (
    <div className="pagination" aria-label="Pagination">
      <button className="button button-secondary" disabled={page <= 1} onClick={() => onPageChange(page - 1)}>
        ← Previous
      </button>
      <span>Page <strong>{page}</strong> of {pages}</span>
      <button className="button button-secondary" disabled={page >= pages} onClick={() => onPageChange(page + 1)}>
        Next →
      </button>
    </div>
  );
}

