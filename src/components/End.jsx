import Mark from './Mark.jsx';
import { EMAIL, PHONE, PORTFOLIO, WHATSAPP } from '../content.js';

const ext = { target: '_blank', rel: 'noopener noreferrer' };

export default function End() {
  return (
    <section className="end" id="fitting">
      <div className="end-c">
        <Mark stroke="#c9aa6b" width={1} />
        <span className="label">The Atelier</span>
        <h2>Tailoring<br /><em>for the few.</em></h2>
        <p>We take a small number of commissions each season so every suit gets the hours it needs. Fittings are by appointment.</p>
        <a className="btn" href={WHATSAPP} {...ext}>Book a fitting on WhatsApp</a>
      </div>
      <footer>
        <div className="foot">
          <div><a className="brand" href="#top"><Mark />Outstead</a></div>
          <div><h4>Garment</h4><a href="#shirt">Shirt</a><a href="#colour">Cloth</a><a href="#fitting">Fittings</a></div>
          <div><h4>Atelier</h4><a href="#fitting">Appointments</a><a href="#fitting">Alterations</a></div>
          <div>
            <h4>Contact</h4>
            <a href={PHONE.href}>{PHONE.label}</a>
            <a href={WHATSAPP} {...ext}>WhatsApp</a>
            <a href={`mailto:${EMAIL}`}>{EMAIL}</a>
          </div>
        </div>
        <p className="credits">
          <span>© 2026 Outstead. Film made from footage on <a href="https://www.pexels.com/license/" {...ext}>Pexels</a>.</span>
          <span>Website by <a href={PORTFOLIO} {...ext}>Abakah Joshua</a></span>
        </p>
      </footer>
    </section>
  );
}
