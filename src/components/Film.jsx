import { CHAPTERS, HERO, frameUrl } from '../content.js';

// Without JS or with reduced motion, each chapter is a normal section over its key frame.
// With .scrub on <html>, one sticky canvas plays the frames as you scroll and the chapters overlay it.
export default function Film() {
  return (
    <div className="film">
      <div className="stage"><canvas aria-hidden="true" /></div>
      <div className="chapters"><div className="chapters-in">
        <section className="ch hero" data-ch="0">
          <img className="key" src={frameUrl('desktop', HERO.frame)} alt={HERO.alt} />
          <div className="hero-t">
            <span className="label">{HERO.label}</span>
            <h1>
              <span className="lm"><span>The</span></span>
              <span className="lm"><span>Anatomy</span></span>
              <span className="lm"><em>of a Suit</em></span>
            </h1>
          </div>
          <div className="scroll-cue"><span className="label">Scroll</span><i /></div>
        </section>
        {CHAPTERS.map((c, i) => <Chapter key={c.num} {...c} index={i + 1} />)}
      </div></div>
    </div>
  );
}

function Chapter({ id, className, index, frame, alt, num, label, lines, text, meta, swatches }) {
  return (
    <section className={className ? `ch ${className}` : 'ch'} id={id} data-ch={index}>
      <img className="key" src={frameUrl('desktop', frame)} alt={alt} loading="lazy" />
      <div className="copy">
        <span className="num">{num}</span><span className="label">{label}</span>
        <h2>{lines.map(l => <span className="lm" key={l}><span>{l}</span></span>)}</h2>
        <p>{text}</p>
        {meta && (
          <div className="meta">
            {meta.map(([k, v]) => <div key={k}>{k}<strong>{v}</strong></div>)}
          </div>
        )}
      </div>
      {swatches && (
        <div className="swatches" aria-hidden="true">
          {swatches.map(([k, v]) => <div key={k}>{k}<em>{v}</em></div>)}
        </div>
      )}
    </section>
  );
}
