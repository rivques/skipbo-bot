import React, { useEffect } from 'react';
import './App.css';
import Game from './components/Game';
import HelpIcon from './components/HelpIcon';

function App() {
  useEffect(() => {
    document.title = 'Skip-Bo Bot';
  }, []);
  return (
    <div className="App">
      <HelpIcon />
      <Game />
    </div>
  );
}

export default App;
