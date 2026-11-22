import { useState, type FormEvent } from "react";
import "./visual-refresh.css";

type Place = {
  name: string;
  admin1?: string | null;
  country?: string | null;
  country_code?: string | null;
  latitude: number;
  longitude: number;
  timezone?: string | null;
};

type IndiaStationResponse = {
  city: string; source: string; source_url: string; data_type: string;
  national_aqi: number | null; national_aqi_note: string;
  stations: { state:string; city:string; station:string; latitude:number|null; longitude:number|null;
    observed_at:string; age_hours:number; freshness:"fresh"|"stale";
    pollutants:{key:string;label:string;value:number;unit:string}[] }[];
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
    setIndiaStations(null);setIndiaError("");
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

  const [household,setHousehold]=useState("general");
  const [hasPurifier,setHasPurifier]=useState(false);
  const [guidance,setGuidance]=useState<any>(null);
  const [assistantQuestion,setAssistantQuestion]=useState("");
  const [assistantAnswer,setAssistantAnswer]=useState<any>(null);
  const [busy,setBusy]=useState(false);
  const [distance,setDistance]=useState("8");
  const [trips,setTrips]=useState("10");
  const [alternative,setAlternative]=useState("metro");
  const [impact,setImpact]=useState<any>(null);
  const [community,setCommunity]=useState<any>(null);
  const [communityBusy,setCommunityBusy]=useState(false);
  const [alertThreshold,setAlertThreshold]=useState("100");
  const [indiaStations,setIndiaStations]=useState<IndiaStationResponse|null>(null);
  const [indiaLoading,setIndiaLoading]=useState(false);
  const [indiaError,setIndiaError]=useState("");


  async function loadIndiaStations(){
    if(!selectedPlace)return;
    setIndiaLoading(true);setIndiaError("");setIndiaStations(null);
    try{
      const response=await fetch(`${API_BASE}/api/india/stations?city=${encodeURIComponent(selectedPlace.name)}`);
      const payload=await response.json().catch(()=>null);
      if(!response.ok)throw new Error(payload?.detail||"Official station data is unavailable.");
      setIndiaStations(payload as IndiaStationResponse);
      if(!payload?.stations?.length)setIndiaError("No station readings were returned for this city. Try a larger nearby city.");
    }catch(error){setIndiaError(error instanceof Error?error.message:"Unable to load Indian station data.");}
    finally{setIndiaLoading(false);}
  }

  async function buildPlan(){
    if(!air)return;
    setBusy(true);
    try{const r=await fetch(`${API_BASE}/api/guidance/daily`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({aqi:air.current.aqi,context:{household,has_air_purifier:hasPurifier}})});if(!r.ok)throw new Error("Guidance unavailable");setGuidance(await r.json());}
    catch(e){setError(e instanceof Error?e.message:"Guidance unavailable");}finally{setBusy(false);}
  }
  async function ask(event:FormEvent<HTMLFormElement>){
    event.preventDefault();if(assistantQuestion.trim().length<2)return;setBusy(true);
    try{const r=await fetch(`${API_BASE}/api/assistant/chat`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({message:assistantQuestion,aqi:air?.current.aqi??null,city:selectedPlace?.name??null,context:{household,has_air_purifier:hasPurifier}})});if(!r.ok)throw new Error("Assistant unavailable");setAssistantAnswer(await r.json());}
    catch(e){setAssistantAnswer({answer:e instanceof Error?e.message:"Please try again.",mode:"error"});}finally{setBusy(false);}
  }

  async function loadCommunityBrief(){
    if(!air)return;
    setCommunityBusy(true);
    try{
      const r=await fetch(`${API_BASE}/api/community/brief`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({aqi:air.current.aqi,household})});
      if(!r.ok)throw new Error("Community brief unavailable");
      setCommunity(await r.json());
    }catch(e){setError(e instanceof Error?e.message:"Community brief unavailable");}
    finally{setCommunityBusy(false);}
  }
  async function calc(event:FormEvent<HTMLFormElement>){
    event.preventDefault();
    try{const r=await fetch(`${API_BASE}/api/impact/estimate`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({distance_km:Number(distance),trips_per_week:Number(trips),weeks:4,alternative})});if(!r.ok)throw new Error("Check commute inputs");setImpact(await r.json());}
    catch(e){setImpact({error:e instanceof Error?e.message:"Calculation failed"});}
  }

  const categoryClass = air?.current.category.toLowerCase().replace(/[^a-z]+/g, "-") || "";

  return (
    <main className="page-shell">
      <nav className="topbar">
        <a className="brand" href="/" aria-label="BreatheWise AI home">
          <span className="brand-mark">b.</span>
          <span>BreatheWise<span className="brand-ai"> AI</span></span>
        </a>
        <div className="topbar-right"><nav className="top-links" aria-label="Main navigation"><a href="#explore">Explore</a><a href="#personal-plan">My air plan</a><a href="#community">Community</a></nav><span className="nav-note"><span className="status-dot" /> LIVE AIR COMPANION</span></div>
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

      {selectedPlace&&(
        <section className="india-station-panel" aria-live="polite">
          <div className="panel-heading">
            <div><p className="eyebrow">INDIA · OFFICIAL MONITORING NETWORK</p><h2>Station observations</h2></div>
            <button className="secondary-button" onClick={loadIndiaStations} disabled={indiaLoading}>{indiaLoading?"Loading…":"Check Indian stations ↗"}</button>
          </div>
          <p className="india-note">Separate from the modeled US AQI estimate above. These are hourly station pollutant averages from the Government of India OGD resource; they are not a personal exposure reading.</p>
          {indiaLoading&&<p className="loading-message">Looking for monitoring stations in {selectedPlace.name}…</p>}
          {indiaError&&<p className="india-error" role="status">{indiaError}</p>}
          {indiaStations&&<>
            <p className="india-note"><strong>{indiaStations.source}</strong> · {indiaStations.stations.length} station(s) returned. <a href={indiaStations.source_url} target="_blank" rel="noreferrer">Dataset details ↗</a></p>
            <p className="india-note">{indiaStations.national_aqi_note}</p>
            <div className="station-grid">{indiaStations.stations.map(station=>(
              <article className="station-card" key={station.state+station.city+station.station}>
                <div className="station-heading"><div><strong>{station.station}</strong><small>{station.city}, {station.state}</small></div><span className={station.freshness==="fresh"?"freshness fresh":"freshness stale"}>{station.freshness==="fresh"?"Fresh":"Stale"} · {station.age_hours}h</span></div>
                <small>Last update: {station.observed_at}</small>
                <div className="station-pollutants">{station.pollutants.map(p=><div key={p.key}><span>{p.label}</span><strong>{p.value.toFixed(1)}</strong><small>{p.unit}</small></div>)}</div>
              </article>
            ))}</div>
          </>}
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
      <section className="explore-section interactive-tools" id="personal-plan">
        <div className="section-heading"><div><p className="eyebrow">PERSONALIZED AIR ACTIONS</p><h2>Your household, <em>your air plan.</em></h2></div><p>Practical guidance based on your selected city estimate and household context.</p></div>
        <div className="tool-card">
          <div className="tool-controls">
            <label>Who are you planning for?<select value={household} onChange={e=>setHousehold(e.target.value)}><option value="general">General household</option><option value="children">Children</option><option value="older_adults">Older adults</option><option value="respiratory_sensitive">Respiratory-sensitive member</option></select></label>
            <label className="check-label"><input type="checkbox" checked={hasPurifier} onChange={e=>setHasPurifier(e.target.checked)}/> I have an air purifier</label>
            <button className="primary-button" onClick={buildPlan} disabled={!air||busy}>{busy?"Preparing…":"Build my daily plan ↗"}</button>
          </div>
          {!air&&<p className="privacy-note">Search for a city above to unlock AQI-aware recommendations.</p>}
          {guidance&&<div className="guidance-result"><h3>{guidance.category} · Daily plan</h3><p>{guidance.summary}</p>{guidance.actions.map((x:any)=><article className="guidance-item" key={x.title}><strong>{x.title} <small>· {x.when}</small></strong><p>{x.action}</p><small>{x.why}</small></article>)}<p className="privacy-note">{guidance.safety_note}</p></div>}
        </div>
        <div className="tool-grid">
          <article className="tool-card"><p className="feature-tag">GENAI AIR ASSISTANT</p><h3>Ask BreatheWise</h3><form className="stack-form" onSubmit={ask}><label htmlFor="assistant-question">What would you like help with?</label><textarea id="assistant-question" value={assistantQuestion} onChange={e=>setAssistantQuestion(e.target.value)} maxLength={1200} placeholder="How can I reduce indoor pollution today?"/><button className="primary-button" disabled={busy||assistantQuestion.trim().length<2}>Ask assistant ↗</button></form>{assistantAnswer&&<div className="assistant-answer"><p>{assistantAnswer.answer}</p><small>Mode: {assistantAnswer.mode}. {assistantAnswer.notice||""}</small></div>}</article>
          <article className="tool-card"><p className="feature-tag">LOWER-EMISSION COMMUTE</p><h3>Estimate a travel switch</h3><form className="stack-form" onSubmit={calc}><label>One-way distance (km)<input type="number" min="0.1" max="500" step="0.1" value={distance} onChange={e=>setDistance(e.target.value)} required/></label><label>One-way trips per week<input type="number" min="1" max="21" value={trips} onChange={e=>setTrips(e.target.value)} required/></label><label>Alternative mode<select value={alternative} onChange={e=>setAlternative(e.target.value)}><option value="metro">Metro</option><option value="bus">Bus</option><option value="carpool">Carpool</option><option value="cycle">Cycle</option><option value="walk">Walk</option></select></label><button className="primary-button">Estimate four-week impact ↗</button></form>{impact&&(impact.error?<p role="alert">{impact.error}</p>:<div className="impact-result"><strong>{impact.estimated_kg_co2e_avoided} kg CO₂e</strong><p>Estimated emissions avoided over four weeks versus a single-occupancy car.</p><small>{impact.methodology} {impact.limitations}</small></div>)}</article>
        </div>
      </section>
      <section className="explore-section community-section" id="community">
        <div className="section-heading"><div><p className="eyebrow">BEYOND ONE HOUSEHOLD</p><h2>Cleaner air is <em>a community effort.</em></h2></div><p>Turn a city snapshot into practical, privacy-conscious steps for shared spaces.</p></div>
        <div className="tool-grid">
          <article className="tool-card">
            <p className="feature-tag">COMMUNITY PREPAREDNESS</p><h3>Build a neighbourhood action brief</h3>
            <p className="privacy-note">Uses the selected modeled AQI and household category. No names, addresses or health records are collected.</p>
            <button className="primary-button" onClick={loadCommunityBrief} disabled={!air||communityBusy}>{communityBusy?"Preparing…":"Generate community brief ↗"}</button>
            {!air&&<p className="privacy-note">Search for a city to generate a brief.</p>}
            {community&&<div className="guidance-result"><h3>{community.response_level.replaceAll("_"," ")}</h3>{community.actions.map((x:any)=><article className="guidance-item" key={x.title}><strong>{x.title}</strong><p>{x.action}</p></article>)}<p className="privacy-note">{community.source_note}</p></div>}
          </article>
          <article className="tool-card">
            <p className="feature-tag">ON-SCREEN AQI THRESHOLD</p><h3>Set a personal check-in level</h3>
            <label htmlFor="aqi-threshold">Show a reminder when the selected city's modeled AQI reaches</label>
            <select id="aqi-threshold" value={alertThreshold} onChange={e=>setAlertThreshold(e.target.value)}><option value="50">50 · Above Good</option><option value="100">100 · Above Moderate</option><option value="150">150 · Above Unhealthy for sensitive groups</option><option value="200">200 · Above Unhealthy</option></select>
            {air&&air.current.aqi>=Number(alertThreshold)?<p className="threshold-alert" role="status">Your selected threshold is reached. Consider reviewing your daily plan and checking official local advisories.</p>:<p className="privacy-note">{air?"The selected city's current model estimate is below this threshold.":"Search for a city to evaluate your threshold."}</p>}
            <p className="privacy-note">This is an on-screen check when you view the app, not a background or push notification. Refresh the city data to check again.</p>
          </article>
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
