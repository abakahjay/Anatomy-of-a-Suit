// The Outstead star, used in the nav, loader, closing section and footer.
export default function Mark({ stroke = 'currentColor', width = 1.2 }) {
  return (
    <svg className="mark" viewBox="0 0 18 18" fill="none" stroke={stroke} strokeWidth={width} aria-hidden="true">
      <path d="M9 1v16M1 9h16M3.3 3.3l11.4 11.4M14.7 3.3 3.3 14.7" />
    </svg>
  );
}
