const highlights = [
  { icon: "◉", title: "Know your air", description: "Understand AQI and key pollutants with clear source and timestamp information.", tag: "LIVE DATA · COMING NEXT" },
  { icon: "⌂", title: "Make home a cleaner-air space", description: "Get practical indoor guidance shaped by outdoor conditions and your household.", tag: "INDOOR AIR" },
  { icon: "↗", title: "Choose a smarter way to move", description: "Explore lower-emission travel options without losing sight of time and convenience.", tag: "CLEANER ROUTINES" },
];

function App() {
  return (
    <main className="page-shell">
      <nav className="topbar">
        <a className="brand" href="/" aria-label="BreatheWise AI home">
          <span className="brand-mark">b.</span>
          <span>BreatheWise<span className="brand-ai"> AI</span></span>
        </a>
        <span className="nav-note"><span className="status-dot" /> YOUR EVERYDAY AIR COMPANION</span>
      </nav>
      <section className="hero">
        <div className="hero-copy">
          <p className="eyebrow"><span /> AIR QUALITY, MADE PERSONAL</p>
          <h1>Breathe better.<br /><em>Live smarter.</em></h1>
          <p className="hero-description">Your air has a story. Understand what is around you, discover small changes that matter, and make confident choices for the people you care about.</p>
          <div className="hero-actions">
            <a className="primary-button" href="#explore">Explore your air <span>↗</span></a>
            <span className="privacy-note">No account needed to explore the starter experience.</span>
          </div>
        </div>
        <div className="hero-art" role="img" aria-label="Abstract illustration of clean air and a leaf">
          <div className="orbit orbit-one" /><div className="orbit orbit-two" /><div className="sun-disc" />
          <div className="leaf-shape">✳</div>
          <div className="art-caption"><span>01 / 03</span><span>SMALL STEPS. CLEARER DAYS.</span></div>
          <div className="floating-card"><span className="floating-icon">✦</span><div><strong>Clarity starts here</strong><small>Understand. Act. Breathe.</small></div></div>
        </div>
      </section>
      <section className="data-note">
        <span className="note-icon">i</span>
        <p><strong>Getting connected to your air.</strong> Live readings are not enabled yet. This starter build does not display invented AQI values; verified local data will appear here once a provider is integrated.</p>
        <span className="note-label">TRANSPARENT BY DESIGN</span>
      </section>
      <section className="explore-section" id="explore">
        <div className="section-heading">
          <div><p className="eyebrow">A HEALTHIER EVERYDAY</p><h2>Good air choices, <em>made simpler.</em></h2></div>
          <p>Useful guidance for real life — not just another number on a screen.</p>
        </div>
        <div className="feature-grid">
          {highlights.map((item, index) => (
            <article className="feature-card" key={item.title}>
              <div className="feature-top"><span className="feature-icon">{item.icon}</span><span className="feature-index">0{index + 1}</span></div>
              <p className="feature-tag">{item.tag}</p><h3>{item.title}</h3>
              <p className="feature-description">{item.description}</p><span className="card-arrow">↗</span>
            </article>
          ))}
        </div>
      </section>
      <footer>
        <a className="brand footer-brand" href="/"><span className="brand-mark">b.</span><span>BreatheWise<span className="brand-ai"> AI</span></span></a>
        <span>Built for clearer choices and healthier communities.</span><span className="footer-year">EST. 2026 · OPEN SOURCE</span>
      </footer>
    </main>
  );
}
export default App;
