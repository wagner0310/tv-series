import { useState, useCallback } from 'react';
import { SearchPage } from './pages/SearchPage';
import { ShowDetailPage } from './pages/ShowDetailPage';

type View = { type: 'search' } | { type: 'show'; showId: number };

function App() {
  const [currentView, setCurrentView] = useState<View>({ type: 'search' });

  const handleSelectShow = useCallback((showId: number) => {
    setCurrentView({ type: 'show', showId });
    window.scrollTo(0, 0);
  }, []);

  const handleBack = useCallback(() => {
    setCurrentView({ type: 'search' });
  }, []);

  return (
    <div className="min-h-screen bg-(--color-bg-primary)]">
      {currentView.type === 'search' ? (
        <SearchPage onSelectShow={handleSelectShow} />
      ) : (
        <ShowDetailPage showId={currentView.showId} onBack={handleBack} />
      )}
    </div>
  );
}

export default App;
