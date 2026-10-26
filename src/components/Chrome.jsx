import Mark from './Mark.jsx';
import { WINDOWS } from '../content.js';

// loader: counts real frame loads (the film hook writes to it directly, 535 updates would be wasted renders)
export function Loader() {
  return (
    <div className="loader" aria-hidden="true">
      <div className="loader-in">
        <Mark stroke="#ece6da" width={1} />
        <div className="loader-bar"><i /></div>
        <div className="loader-pct">0%</div>
      </div>
    </div>
  );
}

export function Nav() {
  return (
    <header className="nav">
      <a className="brand" href="#top" aria-label="Outstead, home">
        <Mark />
        Outstead
      </a>
      <nav className="nav-r">
        <a className="l" href="#shirt">The Garment</a>
        <a className="l" href="#colour">The Cloth</a>
        <a className="btn" href="#fitting">Book a fitting</a>
      </nav>
    </header>
  );
}

export function Rail() {
  return (
    <aside className="rail" aria-hidden="true">
      {WINDOWS.map((_, i) => (
        <span key={i} data-r={i} className={i === 0 ? 'on' : undefined}>{String(i).padStart(2, '0')}</span>
      ))}
    </aside>
  );
}
