export default function RunwayAIStylist() {
  // Static data - in Streamlit, replace with your Python variables
  const analysis = {
    style: "Contemporary Minimalist",
    type: "Silk Blouse",
    styleConf: 92,
    typeConf: 87,
  };

  const outfits = [
    {
      type: "Top",
      name: "Ivory Silk Charmeuse Blouse",
      brand: "The Row",
      price: "$1,290",
      img: "https://images.unsplash.com/photo-1598554747436-c9293d6a588f?w=800&h=1200&fit=crop",
    },
    {
      type: "Bottom",
      name: "High-Waisted Wool Trousers",
      brand: "Loro Piana",
      price: "$2,450",
      img: "https://images.unsplash.com/photo-1594938298603-c8148c4dae35?w=800&h=1200&fit=crop",
    },
    {
      type: "Shoes",
      name: "Patent Leather Pumps",
      brand: "Manolo Blahnik",
      price: "$795",
      img: "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?w=800&h=1200&fit=crop",
    },
  ];

  return (
    <>
      {/* HERO SECTION */}
      <section className="hero">
        <p className="hero-tag">The Future of Personal Style</p>
        <h1 className="hero-title">RUNWAY</h1>
        <div className="hero-divider">
          <span className="line" />
          <span className="hero-ai">AI</span>
          <span className="line" />
        </div>
        <h2 className="hero-subtitle">Stylist</h2>
        <p className="hero-desc">
          One garment. Infinite possibilities.
          <br />
          Let artificial intelligence curate your look.
        </p>
      </section>

      {/* UPLOAD SECTION */}
      <section className="section upload-section">
        <span className="section-num">01</span>
        <div className="section-grid">
          <div className="section-text">
            <p className="chapter">Chapter One</p>
            <h2 className="section-title">
              The <em>Upload</em>
            </h2>
            <div className="divider" />
            <p className="section-desc">
              Every great ensemble begins with a single piece. Drop your chosen
              garment into the frame, and watch as our AI deconstructs its
              essence.
            </p>
          </div>
          <div className="upload-area">
            <div className="upload-box">
              <div className="upload-icon">+</div>
              <p className="upload-text">Drop Image Here</p>
              <p className="upload-hint">or click to select</p>
            </div>
          </div>
        </div>
      </section>

      {/* ANALYSIS SECTION */}
      <section className="section analysis-section">
        <span className="section-num right">02</span>
        <p className="chapter">Chapter Two</p>
        <h2 className="section-title">
          The <em>Analysis</em>
        </h2>

        <div className="analysis-grid">
          <div className="analysis-item">
            <p className="analysis-label">Detected Aesthetic</p>
            <p className="analysis-value">{analysis.style}</p>
            <div className="progress-bar">
              <div
                className="progress-fill"
                style={{ width: `${analysis.styleConf}%` }}
              />
            </div>
            <p className="confidence">{analysis.styleConf}%</p>
          </div>

          <div className="analysis-item">
            <p className="analysis-label">Garment Classification</p>
            <p className="analysis-value">{analysis.type}</p>
            <div className="progress-bar">
              <div
                className="progress-fill accent"
                style={{ width: `${analysis.typeConf}%` }}
              />
            </div>
            <p className="confidence accent">{analysis.typeConf}%</p>
          </div>
        </div>
      </section>

      {/* OUTFIT CARDS */}
      <section className="section ensemble-section">
        <span className="section-num">03</span>
        <p className="chapter">Chapter Three</p>
        <h2 className="section-title">
          The <em>Ensemble</em>
        </h2>

        <div className="outfit-grid">
          {outfits.map((item, i) => (
            <div key={i} className="outfit-card">
              <img src={item.img} alt={item.name} className="outfit-img" />
              <div className="outfit-overlay">
                <p className="outfit-type">{item.type}</p>
                <h3 className="outfit-name">{item.name}</h3>
                <p className="outfit-brand">{item.brand}</p>
                <p className="outfit-price">{item.price}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* NOTES SECTION */}
      <section className="section notes-section">
        <span className="section-num right">04</span>
        <div className="section-grid">
          <div className="section-text">
            <p className="chapter">Chapter Four</p>
            <h2 className="section-title">
              The <em>Notes</em>
            </h2>
          </div>
          <div className="quote-area">
            <blockquote className="quote">
              <span className="quote-mark">&ldquo;</span>
              The silk blouse creates an elegant foundation with its fluid
              drape. High-waisted trousers elongate the silhouette. Patent
              leather pumps add editorial polish—perfect for both boardroom and
              evening.
              <span className="quote-mark end">&rdquo;</span>
            </blockquote>
            <p className="quote-attr">— AI Styling Intelligence</p>
          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="footer">
        <p>RUNWAY AI STYLIST</p>
        <p className="footer-sub">Issue No. 01 · Spring/Summer</p>
      </footer>
    </>
  );
}
