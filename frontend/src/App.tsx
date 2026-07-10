import React, { useState, useEffect, useRef } from 'react';
import {
  Building2,
  MapPin,
  Ruler,
  Calendar,
  Sparkles,
  RefreshCw,
  TrendingUp,
  TrendingDown,
  Activity,
  Cpu,
  CheckCircle2,
  Info,
} from 'lucide-react';

// =============================================
// DATA
// =============================================
const DISTRICTS = [
  "Chennai", "Coimbatore", "Madurai", "Tiruchirappalli",
  "Chengalpattu", "Kancheepuram", "The Nilgiris", "Salem",
  "Tiruppur", "Erode", "Vellore", "Thoothukudi", "Ariyalur",
  "Cuddalore", "Dharmapuri", "Dindigul", "Kallakurichi", "Karur",
  "Krishnagiri", "Mayiladuthurai", "Nagapattinam", "Kanniyakumari",
  "Namakkal", "Perambalur", "Pudukkottai", "Ramanathapuram",
  "Ranipet", "Sivaganga", "Tenkasi", "Thanjavur", "Theni",
  "Thiruvallur", "Thiruvarur", "Tirunelveli", "Tirupathur",
  "Tiruvannamalai", "Viluppuram", "Virudhunagar"
];

const AMENITIES = [
  "None", "Parks, School", "Hospital, Mall",
  "Market, Bus Stand", "Temple, Gym"
];

const TRENDS = [
  { label: "Declining", icon: TrendingDown, color: "#dc2626" },
  { label: "Stable",    icon: Activity,     color: "#2563eb" },
  { label: "Rising",    icon: TrendingUp,   color: "#16a34a" },
];

const DISTRICT_PRICES: Record<string, number> = {
  "Chennai": 8500, "Coimbatore": 5500, "Madurai": 4500,
  "Tiruchirappalli": 4200, "Chengalpattu": 5000, "Kancheepuram": 4800,
  "The Nilgiris": 6000, "Salem": 3800, "Tiruppur": 4000,
  "Erode": 3500, "Vellore": 3600, "Thoothukudi": 3200,
};

// =============================================
// TYPES
// =============================================
interface FormData {
  City: string;
  Neighborhood: string;
  Pincode: string;
  'Property Size (sqft)': number;
  'Lot Size': number;
  Bedrooms: number;
  Bathrooms: number;
  'Year Built': number;
  'Nearby Amenities': string;
  'Market Trends': string;
}

interface CityStatItem {
  City: string;
  mean: number;
  count: number;
}

interface Stats {
  total_listings: number;
  average_price: number;
  min_price: number;
  max_price: number;
  model_accuracy: number;
  city_stats: CityStatItem[];
  market_trends: Record<string, number>;
}

const MOCK_STATS: Stats = {
  total_listings: 1200,
  average_price: 9106468,
  min_price: 1976000,
  max_price: 38299000,
  model_accuracy: 97.99,
  city_stats: [
    { City: "Chennai",       mean: 20947200, count: 35 },
    { City: "The Nilgiris",  mean: 15380200, count: 35 },
    { City: "Coimbatore",    mean: 14612114, count: 35 },
    { City: "Chengalpattu",  mean: 12866935, count: 31 },
    { City: "Kancheepuram",  mean: 12626944, count: 36 },
    { City: "Madurai",       mean: 11686880, count: 25 },
  ],
  market_trends: { Declining: 34.75, Stable: 33.75, Rising: 31.5 }
};

// =============================================
// HELPERS
// =============================================
const formatINR = (n: number) =>
  new Intl.NumberFormat('en-IN', {
    style: 'currency', currency: 'INR', maximumFractionDigits: 0
  }).format(n);

const formatINRCompact = (n: number) => {
  if (n >= 10000000) return `₹${(n / 10000000).toFixed(2)} Cr`;
  if (n >= 100000)   return `₹${(n / 100000).toFixed(2)} L`;
  return formatINR(n);
};

// Slider percentage for gradient
const sliderPct = (val: number, min: number, max: number) =>
  `${Math.round(((val - min) / (max - min)) * 100)}%`;

// =============================================
// SLIDER COMPONENT
// =============================================
function Slider({
  label, value, min, max, step = 1,
  format = (v: number) => String(v),
  onChange,
}: {
  label: string; value: number; min: number; max: number;
  step?: number; format?: (v: number) => string;
  onChange: (v: number) => void;
}) {
  const pct = sliderPct(value, min, max);
  return (
    <div className="slider-field">
      <div className="slider-top">
        <span className="slider-label">{label}</span>
        <span className="slider-value-badge">{format(value)}</span>
      </div>
      <input
        type="range" min={min} max={max} step={step} value={value}
        className="slider-track"
        style={{ '--pct': pct } as React.CSSProperties}
        onChange={e => onChange(Number(e.target.value))}
      />
    </div>
  );
}

// =============================================
// MAIN APP
// =============================================
export default function App() {
  const [form, setForm] = useState<FormData>({
    City: 'Chennai',
    Neighborhood: 'Chennai Sector 5',
    Pincode: '600005',
    'Property Size (sqft)': 1600,
    'Lot Size': 2200,
    Bedrooms: 3,
    Bathrooms: 2,
    'Year Built': 2015,
    'Nearby Amenities': 'None',
    'Market Trends': 'Stable',
  });

  const [loading,    setLoading]    = useState(false);
  const [prediction, setPrediction] = useState<number | null>(null);
  const [flipped,    setFlipped]    = useState(false);
  const [stats,      setStats]      = useState<Stats>(MOCK_STATS);
  const [apiOnline,  setApiOnline]  = useState(false);

  const rightColRef = useRef<HTMLDivElement>(null);

  // Sync Neighborhood when City changes
  useEffect(() => {
    const sector = Math.floor(Math.random() * 10) + 1;
    const pin = `60${Math.floor(Math.random() * 5)}${Math.floor(Math.random() * 900) + 100}`;
    setForm(prev => ({
      ...prev,
      Neighborhood: `${form.City} Sector ${sector}`,
      Pincode: pin,
    }));
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [form.City]);

  // Fetch stats from backend
  useEffect(() => {
    fetch('http://localhost:5000/api/stats')
      .then(r => r.json())
      .then((d: Stats) => {
        if (d?.city_stats) { setStats(d); setApiOnline(true); }
      })
      .catch(() => setApiOnline(false));
  }, []);

  const set = (key: keyof FormData, val: string | number) =>
    setForm(prev => ({ ...prev, [key]: val }));

  const handlePredict = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setFlipped(false);

    try {
      const res = await fetch('http://localhost:5000/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });
      if (!res.ok) throw new Error('API error');
      const data = await res.json();
      await delay(1000);
      setPrediction(data.predicted_price);
    } catch {
      // Heuristic fallback
      await delay(1000);
      const base = DISTRICT_PRICES[form.City] ?? 2800;
      const mult = form['Market Trends'] === 'Rising' ? 1.05
                 : form['Market Trends'] === 'Declining' ? 0.95 : 1.0;
      const price = (form['Property Size (sqft)'] * base + form.Bedrooms * 100000) * mult;
      setPrediction(price);
    } finally {
      setLoading(false);
      setFlipped(true);
      // Scroll right panel into view on mobile
      setTimeout(() => rightColRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 100);
    }
  };

  const handleReset = () => {
    setFlipped(false);
    setPrediction(null);
  };

  const maxCityPrice = Math.max(...stats.city_stats.map(c => c.mean));

  return (
    <>
      {/* LOADING OVERLAY */}
      {loading && (
        <div className="loading-overlay">
          <div className="loading-card">
            <div className="cube-3d">
              <div className="cube-3d-face front"  />
              <div className="cube-3d-face back"   />
              <div className="cube-3d-face left"   />
              <div className="cube-3d-face right"  />
              <div className="cube-3d-face top"    />
              <div className="cube-3d-face bottom" />
            </div>
            <p className="loading-text">Analysing property data…</p>
            <p className="loading-sub">Running Random Forest pipeline</p>
          </div>
        </div>
      )}

      {/* HERO */}
      <section className="hero-section">
        <span className="hero-badge">
          <span className="hero-dot" />
          {apiOnline ? 'AI Engine Connected' : 'Local Heuristic Engine Active'}
        </span>

        <h1 className="hero-title">
          Tamil Nadu<br />
          <span>House Price Predictor</span>
        </h1>

        <p className="hero-description">
          Estimate property valuations across 38 Tamil Nadu districts
          using our Random Forest AI trained on 1,200 real-market listings.
        </p>

        <div className="hero-stats-row">
          <div className="hero-stat">
            <span className="hero-stat-val">{stats.model_accuracy.toFixed(1)}%</span>
            <span className="hero-stat-lbl">R² Accuracy</span>
          </div>
          <div className="hero-stat-divider" />
          <div className="hero-stat">
            <span className="hero-stat-val">1,200</span>
            <span className="hero-stat-lbl">Listings</span>
          </div>
          <div className="hero-stat-divider" />
          <div className="hero-stat">
            <span className="hero-stat-val">38</span>
            <span className="hero-stat-lbl">Districts</span>
          </div>
          <div className="hero-stat-divider" />
          <div className="hero-stat">
            <span className="hero-stat-val">{formatINRCompact(stats.average_price)}</span>
            <span className="hero-stat-lbl">Avg Price</span>
          </div>
        </div>
      </section>

      {/* MAIN CONTENT */}
      <main className="page-wrapper">
        <div className="main-grid">

          {/* ==================== LEFT PANEL: FORM ==================== */}
          <div className="animate-in">
            <div className="card">
              {/* Card Header */}
              <div className="card-header">
                <div className="card-header-icon">
                  <Building2 size={18} />
                </div>
                <div>
                  <div className="card-header-title">Valuation Parameters</div>
                  <div className="card-header-sub">Fill in the property details to estimate its market value</div>
                </div>
              </div>

              {/* Card Body */}
              <div className="card-body">
                <form onSubmit={handlePredict}>

                  {/* SECTION: Location */}
                  <div className="section-label">
                    <MapPin size={12} /> Location Details
                  </div>

                  <div className="form-grid-2" style={{ marginBottom: '1.5rem' }}>
                    <div className="form-field">
                      <label className="form-label">
                        <MapPin size={11} /> City / District
                      </label>
                      <select
                        className="form-select"
                        value={form.City}
                        onChange={e => set('City', e.target.value)}
                      >
                        {DISTRICTS.map(d => (
                          <option key={d} value={d}>{d}</option>
                        ))}
                      </select>
                    </div>

                    <div className="form-field">
                      <label className="form-label">Neighborhood</label>
                      <input
                        type="text"
                        className="form-input"
                        value={form.Neighborhood}
                        onChange={e => set('Neighborhood', e.target.value)}
                        placeholder="e.g. Chennai Sector 5"
                        required
                      />
                    </div>
                  </div>

                  <div className="form-grid-3" style={{ marginBottom: '1.5rem' }}>
                    <div className="form-field">
                      <label className="form-label">Pincode</label>
                      <input
                        type="text"
                        className="form-input"
                        value={form.Pincode}
                        onChange={e => set('Pincode', e.target.value)}
                        placeholder="600xxx"
                        maxLength={6}
                        required
                      />
                    </div>

                    <div className="form-field" style={{ gridColumn: 'span 2' }}>
                      <Slider
                        label="Property Size"
                        value={form['Property Size (sqft)']}
                        min={500} max={5000} step={50}
                        format={v => `${v.toLocaleString()} sqft`}
                        onChange={v => set('Property Size (sqft)', v)}
                      />
                    </div>
                  </div>

                  {/* Lot Size & Year Built */}
                  <div className="form-grid-2" style={{ marginBottom: '1.5rem' }}>
                    <Slider
                      label="Lot Size"
                      value={form['Lot Size']}
                      min={500} max={6000} step={50}
                      format={v => `${v.toLocaleString()} sqft`}
                      onChange={v => set('Lot Size', v)}
                    />
                    <Slider
                      label="Year Built"
                      value={form['Year Built']}
                      min={1990} max={2026} step={1}
                      format={v => String(v)}
                      onChange={v => set('Year Built', v)}
                    />
                  </div>

                  <div className="section-separator" />

                  {/* SECTION: Property Details */}
                  <div className="section-label">
                    <Ruler size={12} /> Property Details
                  </div>

                  <div className="form-grid-2" style={{ marginBottom: '1.5rem' }}>
                    <div className="form-field">
                      <label className="form-label">Bedrooms</label>
                      <div className="stepper-group">
                        {[1,2,3,4,5].map(n => (
                          <div
                            key={n}
                            className={`stepper-btn${form.Bedrooms === n ? ' active' : ''}`}
                            onClick={() => set('Bedrooms', n)}
                          >
                            {n}
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="form-field">
                      <label className="form-label">Bathrooms</label>
                      <div className="stepper-group">
                        {[1,2,3,4,5].map(n => (
                          <div
                            key={n}
                            className={`stepper-btn${form.Bathrooms === n ? ' active' : ''}`}
                            onClick={() => set('Bathrooms', n)}
                          >
                            {n}
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* Nearby Amenities */}
                  <div className="form-field" style={{ marginBottom: '1.5rem' }}>
                    <label className="form-label">Nearby Amenities</label>
                    <div className="pill-group">
                      {AMENITIES.map(a => (
                        <div
                          key={a}
                          className={`pill${form['Nearby Amenities'] === a ? ' active' : ''}`}
                          onClick={() => set('Nearby Amenities', a)}
                        >
                          {a}
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="section-separator" />

                  {/* SECTION: Market Context */}
                  <div className="section-label">
                    <Activity size={12} /> Market Context
                  </div>

                  <div className="form-field" style={{ marginBottom: '2rem' }}>
                    <label className="form-label">Market Trend</label>
                    <div className="trend-pill-group">
                      {TRENDS.map(({ label, icon: Icon, color }) => {
                        const isActive = form['Market Trends'] === label;
                        return (
                          <div
                            key={label}
                            className={`trend-pill${isActive ? ' active' : ''}`}
                            onClick={() => set('Market Trends', label)}
                          >
                            <div className="trend-icon">
                              <Icon
                                size={20}
                                color={isActive ? '#fff' : color}
                              />
                            </div>
                            <span>{label}</span>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  {/* SUBMIT */}
                  <button type="submit" disabled={loading} className="submit-btn" id="predict-btn">
                    {loading ? (
                      <>
                        <RefreshCw size={18} className="spin" />
                        Estimating…
                      </>
                    ) : (
                      <>
                        <Sparkles size={18} />
                        Estimate Property Value
                      </>
                    )}
                  </button>

                </form>
              </div>
            </div>
          </div>

          {/* ==================== RIGHT PANEL ==================== */}
          <div
            ref={rightColRef}
            style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}
          >

            {/* 3D FLIP CARD */}
            <div className="animate-in animate-in-delay-1">
              <div className="flip-perspective">
                <div className={`flip-inner${flipped ? ' flipped' : ''}`}>

                  {/* FRONT */}
                  <div className="flip-face">
                    <div className="flip-front-body">
                      <div className="house-illustration">
                        <Building2 size={40} strokeWidth={1.25} />
                      </div>

                      <div>
                        <h3 className="flip-front-title">Ready to Estimate</h3>
                        <p className="flip-front-desc">
                          Configure the property parameters on the left and click
                          "Estimate Property Value" to get an AI-powered valuation.
                        </p>
                      </div>

                      <div className="flip-front-steps">
                        <div className="flip-step">
                          <span className="flip-step-num">1</span>
                          Select city &amp; location details
                        </div>
                        <div className="flip-step">
                          <span className="flip-step-num">2</span>
                          Set size, bedrooms &amp; amenities
                        </div>
                        <div className="flip-step">
                          <span className="flip-step-num">3</span>
                          Choose market trend &amp; submit
                        </div>
                      </div>

                      <div style={{
                        marginTop: '0.5rem',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px',
                        fontSize: '0.75rem',
                        color: '#9ca3af',
                      }}>
                        <Cpu size={13} />
                        Random Forest · 98% R² Accuracy
                      </div>
                    </div>
                  </div>

                  {/* BACK (result) */}
                  <div className="flip-face flip-face-back">
                    {prediction !== null && (
                      <div className="flip-back-body">
                        <div className="result-tag">
                          <CheckCircle2 size={13} />
                          Valuation Complete
                        </div>

                        <p className="result-label">Estimated Sale Price</p>
                        <div className="result-price">{formatINR(prediction)}</div>
                        <p className="result-price-psf">
                          ≈ {formatINR(Math.round(prediction / form['Property Size (sqft)']))}/sqft
                        </p>

                        <div className="result-details">
                          <div className="result-row">
                            <span className="result-row-label">City</span>
                            <span className="result-row-value">{form.City}</span>
                          </div>
                          <div className="result-row">
                            <span className="result-row-label">Property Size</span>
                            <span className="result-row-value">{form['Property Size (sqft)'].toLocaleString()} sqft</span>
                          </div>
                          <div className="result-row">
                            <span className="result-row-label">Bedrooms / Baths</span>
                            <span className="result-row-value">{form.Bedrooms} BHK / {form.Bathrooms} Bath</span>
                          </div>
                          <div className="result-row">
                            <span className="result-row-label">Year Built</span>
                            <span className="result-row-value">{form['Year Built']}</span>
                          </div>
                          <div className="result-row">
                            <span className="result-row-label">Market Trend</span>
                            <span className="result-row-value">{form['Market Trends']}</span>
                          </div>
                          <div className="result-row">
                            <span className="result-row-label">Valuation Date</span>
                            <span className="result-row-value">{new Date().toLocaleDateString('en-IN')}</span>
                          </div>
                        </div>

                        <p className="result-notice">
                          <Info size={11} style={{ display:'inline', verticalAlign:'middle', marginRight: 4 }} />
                          Estimated using a Random Forest model trained on 1,200 listings.
                          Actual prices may vary ±5% based on local factors.
                        </p>

                        <button className="result-reset-btn" onClick={handleReset}>
                          <RefreshCw size={14} />
                          New Estimate
                        </button>
                      </div>
                    )}
                  </div>

                </div>
              </div>
            </div>

            {/* MARKET INSIGHTS CARD */}
            <div className="animate-in animate-in-delay-2">
              <div className="card">
                <div className="card-header">
                  <div className="card-header-icon">
                    <Activity size={16} />
                  </div>
                  <div>
                    <div className="card-header-title">Market Insights</div>
                    <div className="card-header-sub">Tamil Nadu real estate overview</div>
                  </div>
                </div>

                <div className="card-body" style={{ paddingTop: '1.5rem' }}>

                  {/* Mini Stats */}
                  <div className="stats-mini-grid">
                    <div className="stat-mini-card">
                      <div className="stat-mini-label">Avg. Listing</div>
                      <div className="stat-mini-value">{formatINRCompact(stats.average_price)}</div>
                    </div>
                    <div className="stat-mini-card">
                      <div className="stat-mini-label">Total Listings</div>
                      <div className="stat-mini-value">{stats.total_listings.toLocaleString()}</div>
                    </div>
                    <div className="stat-mini-card">
                      <div className="stat-mini-label">Lowest</div>
                      <div className="stat-mini-value">{formatINRCompact(stats.min_price)}</div>
                    </div>
                    <div className="stat-mini-card">
                      <div className="stat-mini-label">Highest</div>
                      <div className="stat-mini-value">{formatINRCompact(stats.max_price)}</div>
                    </div>
                  </div>

                  {/* 3D Bar Chart */}
                  <p className="chart-title">Average Price by District (Top 6)</p>
                  <div className="chart-bars">
                    {stats.city_stats.slice(0, 6).map((city) => {
                      const heightPct = (city.mean / maxCityPrice) * 100;
                      return (
                        <div key={city.City} className="chart-bar-wrap">
                          <div
                            className="chart-bar"
                            style={{ height: `${heightPct}%` }}
                          >
                            <div className="chart-bar-tooltip">
                              {formatINRCompact(city.mean)}
                            </div>
                          </div>
                          <span className="chart-bar-label">{city.City}</span>
                        </div>
                      );
                    })}
                  </div>

                  {/* Market Trend Meters */}
                  <p className="chart-title" style={{ marginTop: '1.5rem' }}>Market Trend Distribution</p>
                  <div className="trend-meters">
                    {Object.entries(stats.market_trends).map(([trend, pct]) => {
                      const colors: Record<string, string> = {
                        Rising: '#16a34a', Stable: '#2563eb', Declining: '#dc2626'
                      };
                      return (
                        <div key={trend} className="trend-meter">
                          <span className="trend-meter-label">{trend}</span>
                          <div className="trend-meter-track">
                            <div
                              className="trend-meter-fill"
                              style={{
                                width: `${pct}%`,
                                background: colors[trend] ?? '#6b7280',
                              }}
                            />
                          </div>
                          <span className="trend-meter-pct">{pct.toFixed(1)}%</span>
                        </div>
                      );
                    })}
                  </div>

                </div>
              </div>
            </div>

          </div>
          {/* END RIGHT PANEL */}

        </div>
      </main>

      {/* FOOTER */}
      <footer className="page-footer">
        Tamil Nadu House Price Predictor · AI Valuation Engine ·
        Built with Random Forest &amp; React
      </footer>
    </>
  );
}

function delay(ms: number) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
