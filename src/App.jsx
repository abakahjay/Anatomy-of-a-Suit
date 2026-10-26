import { useRef } from 'react';
import { Loader, Nav, Rail } from './components/Chrome.jsx';
import Film from './components/Film.jsx';
import End from './components/End.jsx';
import useScrollFilm from './hooks/useScrollFilm.js';

export default function App() {
  const root = useRef(null);
  useScrollFilm(root);
  return (
    <div ref={root}>
      <Loader />
      <Nav />
      <Rail />
      <main id="top">
        <Film />
        <End />
      </main>
    </div>
  );
}
