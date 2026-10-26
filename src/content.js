// Film timing and every word on the page.

export const FRAMES = 535;

// chapter windows in film progress (0..1), matching the dissolves in tools/compose-film.sh
export const WINDOWS = [[0, .1], [.12, .24], [.26, .37], [.39, .62], [.64, .74], [.76, .87], [.89, .98]];

export const frameUrl = (set, i) => `${import.meta.env.BASE_URL}frames/${set}/${String(i).padStart(4, '0')}.jpg`;

export const PHONE = { href: 'tel:+233532900914', label: '053 290 0914' };
export const WHATSAPP = "https://wa.me/233532900914?text=Hello%2C%20I%27d%20like%20to%20book%20a%20fitting";
export const EMAIL = 'william202075@gmail.com';
export const PORTFOLIO = 'https://portfolio-8jmo.onrender.com/';

export const HERO = {
  frame: 40,
  alt: 'A man in a dark coat walking down a lamp-lit street at night',
  label: 'Bespoke Tailoring  ·  Six Chapters',
};

export const CHAPTERS = [
  {
    id: 'shirt', frame: 110, num: '01', label: 'The Shirt',
    alt: 'A man buttoning a crisp white dress shirt',
    lines: ['A Shirt of', 'Pure Cotton'],
    text: 'Two-fold poplin, cut to your measure. A collar that holds its line under a tie and sits flat without one.',
    meta: [['Cloth', '2-fold poplin'], ['Collar', 'Cutaway']],
  },
  {
    frame: 190, num: '02', label: 'The Waistcoat',
    alt: 'A man fastening the buttons of a checked waistcoat',
    lines: ['Cut Close', 'to the Body'],
    text: 'Six buttons, the last left open. Backed in silk and adjusted at the waist so it never rides up when you sit.',
    meta: [['Front', 'Single-breasted'], ['Back', 'Silk']],
  },
  {
    frame: 245, num: '03', label: 'The Canvas',
    alt: 'A tailor marking cloth with chalk, then fitting a jacket on a client',
    lines: ['Built on', 'Full Canvas'],
    text: 'Horsehair canvas stitched by hand from shoulder to hem. Over time it shapes itself to the person wearing it.',
    meta: [['Construction', 'Hand-padded'], ['Lapel', 'Rolled']],
  },
  {
    frame: 385, num: '04', label: 'The Fit',
    alt: 'A man buttoning his dark suit jacket',
    lines: ['Made to', 'Be Worn'],
    text: 'Three fittings, then the suit is yours. Built for the way you stand, sit and reach, not for a hanger.',
    meta: [['Fittings', 'Three'], ['Pattern', 'Kept on file']],
  },
  {
    id: 'colour', className: 'colour', frame: 445, num: '05', label: 'The Cloth',
    alt: 'Three men in black and grey suits on a flight of steps',
    lines: ['A Language', 'of Colour'],
    text: 'Over two thousand bunches to choose from. Each one says something different in a room.',
    swatches: [['Midnight', 'Super 130s'], ['Grey', 'Flannel'], ['Charcoal', 'Worsted']],
  },
  {
    frame: 505, num: '06', label: 'The Finish',
    alt: 'Close-up of a man fastening the cufflink on his shirt cuff',
    lines: ['The Last', 'Quarter-Inch'],
    text: 'Working buttonholes, stitched by hand. A quarter-inch of shirt cuff showing below the sleeve. The details nobody notices until they are missing.',
    meta: [['Cuff', '4 working holes'], ['Sleeve', '¼ inch of shirt']],
  },
];
