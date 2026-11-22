import { useState, type FormEvent } from "react";

type Place = {
  name: string;
  admin1?: string | null;
  country?: string | null;
  country_code?: string | null;
  latitude: number;
  longitude: number;
  timezone?: string | null;
};

type AirQuality = {
  location: { latitude: number; longitude: number; timezone?: string | null };
  current: {
    observed_at: string;
    aqi: number;
    aqi_scale: string;
    category: string;
    pollutants: { key: string; label: string; value: number; unit: string }[];
  };
  source: { name: string; url: string; model: string; data_type: string };
  caveat: string;
};

const API_BASE = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000").replace(/\/$/, "");

function App() {
  const [query, setQuery] = useState("");
  const [places, setPlaces] = useState<Place[]>([]);
  const [selectedPlace, setSelectedPlace] = useState<Place | null>(null);
  const [air, setAir] = useState<AirQuality | null>(null);
  const [searching, setSearching] = useState(false);
  const [loadingAir, setLoadingAir] = useState(false);
  const [error, setError] = useState("");

  async function searchCity(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (query.trim().length < 2) return;
    setSearching(true);
    setError("");
    setPlaces([]);
    setAir(null);
    setSelectedPlace(null);
    try {
      const response = await fetch(`${API_BASE}/api/locations/search?name=${encodeURIComponent(query.trim())}`);
      if (!response.ok) throw new Error("City search is temporarily unavailable. Please try again.");
      const data: { results: Place[] } = await response.json();
      setPlaces(data.results || []);
      if (!data.results?.length) setError("No matching cities found. Try a nearby larger city or check the spelling.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to search for that city.");
    } finally {
      setSearching(false);
    }
  }

  async function loadAir(place: Place) {
    setSelectedPlace(place);
    setPlaces([]);
    setLoadingAir(true);
    setError("");
    setAir(null);
    try {
      const params = new URLSearchParams({
        latitude: String(place.latitude),
        longitude: String(place.longitude),
      });
      const response = await fetch(`${API_BASE}/api/air-quality?${params.toString()}`);
      if (!response.ok) {
        const payload = await response.json().catch(() => null);
        throw new Error(payload?.detail || "Air-quality data is temporarily unavailable.");
      }
      setAir(await response.json() as AirQuality);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load air-quality data.");
    } finally {
      setLoadingAir(false);
    }
  }

  const categoryClass = air?.current.category.toLowerCase().replace(/[^a-z]+/g, "-") || "";

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
          <p className="hero-description">
            Your air has a story. Understand what is around you, discover small
            changes that matter, and make confident choices for the people you care about.
          </p>
          <form className="city-search" onSubmit={searchCity}>
            <label htmlFor="city">Explore air quality by city</label>
            <div className="search-row">
              <input
                id="city"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Search a city (e.g. Hyderabad)"
                minLength={2}
                maxLength={80}
                autoComplete="off"
              />
              <button className="primary-button" type="submit" disabled={searching || query.trim().length < 2}>
                {searching ? "Searching…" : "Search"} <span>↗</span>
              </button>
            </div>
            <p className="privacy-note">City search only — no device location permission required.</p>
          </form>
          {places.length > 0 && (
            <div className="place-results" aria-label="Matching cities">
              {places.map((place, index) => (
                <button className="place-option" key={`${place.name}-${place.latitude}-${index}`} onClick={() => loadAir(place)}>
                  <span><strong>{place.name}</strong><small>{[place.admin1, place.country].filter(Boolean).join(", ")}</small></span>
                  <span aria-hidden="true">↗</span>
                </button>
              ))}
            </div>
          )}
          {error && <p className="error-message" role="alert">{error}</p>}
        </div>
        <div className="hero-art" role="img" aria-label="Abstract illustration of clean air and a leaf">
          <div className="orbit orbit-one" /><div className="orbit orbit-two" /><div className="sun-disc" />
          <div className="leaf-shape">✳</div>
          <div className="art-caption"><span>01 / 03</span><span>SMALL STEPS. CLEARER DAYS.</span></div>
          <div className="floating-card"><span className="floating-icon">✦</span><div><strong>Clarity starts here</strong><small>Understand. Act. Breathe.</small></div></div>
        </div>
      </section>

      {(loadingAir || air || selectedPlace) && (
        <section className="air-panel" aria-live="polite">
          <div className="panel-heading">
            <div><p className="eyebrow">YOUR CITY SNAPSHOT</p><h2>{selectedPlace ? [selectedPlace.name, selectedPlace.admin1, selectedPlace.country].filter(Boolean).join(", ") : "Loading air data"}</h2></div>
            {air && <span className={`category-pill ${categoryClass}`}>{air.current.category}</span>}
          </div>
          {loadingAir && <p className="loading-message">Fetching the latest modeled conditions…</p>}
          {air && (
            <>
              <div className="aqi-overview">
                <div className={`aqi-number ${categoryClass}`}><strong>{air.current.aqi}</strong><span>{air.current.aqi_scale}</span></div>
                <div className="aqi-context"><strong>{air.current.category}</strong><p>Current model estimate · {air.current.observed_at || "Time not provided by source"}</p><p>Selected location: {air.location.latitude.toFixed(3)}, {air.location.longitude.toFixed(3)}</p></div>
              </div>
              <div className="pollutant-grid">
                {air.current.pollutants.map((pollutant) => (
                  <article className="pollutant-card" key={pollutant.key}>
                    <span>{pollutant.label}</span><strong>{Number(pollutant.value).toFixed(1)}</strong><small>{pollutant.unit}</small>
                  </article>
                ))}
              </div>
              <div className="source-note">
                <strong>Source & limitations</strong>
                <p>{air.source.data_type} {air.source.model}. This is a US EPA AQI-scale estimate, not India's CPCB National AQI or a personal exposure reading.</p>
                <p>Updated for the model time shown above. For severe conditions, check official local monitoring and public-health advisories.</p>
                <a href={air.source.url} target="_blank" rel="noreferrer">Open data source ↗</a>
              </div>
            </>
          )}
        </section>
      )}

      <section className="data-note">
        <span className="note-icon">i</span>
        <p><strong>Know what the number means.</strong> This first version uses modeled air-quality data and clearly labels its US AQI scale. It does not claim to show official CPCB station readings.</p>
        <span className="note-label">TRANSPARENT BY DESIGN</span>
      </section>

      <section className="explore-section" id="explore">
        <div className="section-heading">
          <div><p className="eyebrow">A HEALTHIER EVERYDAY</p><h2>Good air choices, <em>made simpler.</em></h2></div>
          <p>Useful guidance for real life — not just another number on a screen.</p>
        </div>
        <div className="feature-grid">
          <article className="feature-card"><div className="feature-top"><span className="feature-icon">◉</span><span className="feature-index">01</span></div><p className="feature-tag">AIR INTELLIGENCE</p><h3>Know your air</h3><p className="feature-description">Explore city-level pollutant estimates with data source, timestamp, and scale clearly shown.</p></article>
          <article className="feature-card"><div className="feature-top"><span className="feature-icon">⌂</span><span className="feature-index">02</span></div><p className="feature-tag">INDOOR AIR</p><h3>Make home a cleaner-air space</h3><p className="feature-description">Get practical indoor guidance shaped by outdoor conditions and your household.</p></article>
          <article className="feature-card"><div className="feature-top"><span className="feature-icon">↗</span><span className="feature-index">03</span></div><p className="feature-tag">CLEANER ROUTINES</p><h3>Choose a smarter way to move</h3><p className="feature-description">Explore lower-emission travel options without losing sight of time and convenience.</p></article>
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
