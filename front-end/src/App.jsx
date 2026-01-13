
import React, { useState } from 'react';
import { Send } from 'lucide-react';
import './App.css';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isChatOpen, setIsChatOpen] = useState(false);
  

  const handleSend = async () => {
  if (!input.trim()) return;

  const userMessage = { text: input, isBot: false };
  setMessages((prev) => [...prev, userMessage]);
  setInput("");

  const thinkingMessage = { text: "Le guide réfléchit...", isBot: true, thinking: true };
  setMessages((prev) => [...prev, thinkingMessage]);

  try {
    const response = await fetch('http://localhost:5000/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: userMessage.text }),
    });

    const data = await response.json();

    setMessages((prev) =>
          prev.map((msg) =>
            msg.thinking
              ? { text: data.bot, isBot: true }
              : msg
          )
        );

  } catch (error) {
    console.error("Erreur de connexion", error);
 
       setMessages((prev) =>
      prev.map((msg) =>
        msg.thinking
          ? { text: "Erreur de connexion 😢", isBot: true }
          : msg
      )
    );

  }
};

  return (
    <div className="app-container">
      {/* 1. BARRE DE NAVIGATION (NAVBAR) */}
      <nav className="navbar">
        <div className="nav-logo">Sentiers Libres</div>
        <ul className="nav-links">
          <li><a href="#accueil">Accueil</a></li>
          <li><a href="#conseils">Nos conseils</a></li>
          <li><a href="#rando">Randonnées</a></li>
          <li><a href="#articles">Articles</a></li>
        </ul>
      </nav>

      {/* 2. SECTION ACCROCHE*/}
      <header className="hero-header">
        <div className="hero-overlay">
          <div className="hero-header-content">
            <h2 className="hero-main-title">Partez à la découverte des plus beaux sentiers.</h2>
            <p className="hero-intro">
              Explorez des randonnées adaptées à votre niveau, vos envies et votre rythme.
            </p>
          </div>
        </div>
      </header>

      {/* 3. SECTION PRINCIPALE (ASSISTANT IA) */}
      <div className="main-content">
        <div className="hero-left">
          <h1>Trouvez votre randonnée idéale avec notre assistant intelligent</h1>
          <p>Indiquez votre niveau, votre région, vos envies et laissez vous guider</p>
            <div 
            className="chat-input-area"
            onClick={() => setIsChatOpen(true)}
            style={{ cursor: "pointer" }}
          >
            <input 
              type="text"
              placeholder="Je recherche une randonnée en Bretagne..."
              disabled
              style={{ pointerEvents: "none" }}
            />
          </div>
        </div>

        <div className="hero-right-image">
          <img src="/OIPP.jpg" alt="Paysage de montagne" />
        </div>
      </div>

      {/* 4. SECTION RANDONNÉES INCONTOURNABLES */}
      <section className="trending-section">
        <div className="section-header">
          <h2>Randonnées incontournables</h2>
          <p>Des parcours testés et approuvés pour une immersion garantie.</p>
        </div>

        <div className="cards-grid">
          <div className="card rando-card">
            <img src="/Jarak.png" alt="JARAK" className="full-card-img" />
          </div>

          <div className="card rando-card">
            <img src="/Auvergne.png" alt="Volcans d'Auvergne" className="full-card-img" />
          </div>

          <div className="card rando-card">
            <img src="/Pyrenees.png" alt="Pyrénées Orientales" className="full-card-img" />
          </div>
        </div>
      </section>

      {/* 5. SECTION ARTICLES */}
      <section className="articles-section">
        <div className="section-header">
          <h2>Articles</h2>
          <p>À lire pour mieux préparer vos aventures</p>
        </div>

        <div className="articles-grid">
          <article className="article-card">
            <img src="/Image Article 1.jpg" alt="Marcher vers l'inattendu" />
            <span className="article-date">05 mai 2025</span>
            <h3>Marcher vers l'inattendu</h3>
            <span className="category-badge">Exploration</span>
            <p>Il y a des chemins qui ne se contentent pas de nous mener quelque part. Ils nous transforment.</p>
            <button className="read-more-btn">Lire l'article →</button>
          </article>

          <article className="article-card">
            <img src="/Image Article 2.jpg" alt="Préparer l'essentiel" />
            <span className="article-date">05 mai 2025</span>
            <h3>Préparer l'essentiel</h3>
            <span className="category-badge">Organisation</span>
            <p>Avant de partir, il y a ce moment suspendu où chaque objet compte. Une carte, une boussole...</p>
            <button className="read-more-btn">Lire l'article →</button>
          </article>

          <article className="article-card">
            <img src="/Image Article 3.jpg" alt="Le luxe du minimal" />
            <span className="article-date">05 mai 2025</span>
            <h3>Le luxe du minimal</h3>
            <span className="category-badge">Camping</span>
            <p>Quand le feu crépite et que la forêt s'éveille doucement, on comprend que le confort n'a rien à voir.</p>
            <button className="read-more-btn">Lire l'article →</button>
          </article>
        </div>
      </section>

          {isChatOpen && (
      <div className="chat-overlay">
        <div className="chat-widget">

          {/* HEADER */}
          <div className="chat-header">
            <h3>Assistant randonnée</h3>
            <button onClick={() => setIsChatOpen(false)}>✕</button>
          </div>

          {/* MESSAGES */}
          <div className="chat-messages">
            {messages.length === 0 && (
              <div className="bot-reply">
                Bonjour 😊 Je serai votre guide pour trouver votre randonnée idéale.
              </div>
            )}

            {messages.map((msg, index) => (
              <div
                key={index}
                className={msg.isBot ? "bot-reply" : "user-query"}
              >
                {msg.text}
              </div>
            ))}
          </div>

          {/* INPUT */}
          <div className="chat-input">
            <input
              type="text"
              placeholder="Posez votre question..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSend()}
            />
            <button onClick={handleSend}>Envoyer</button>
          </div>

        </div>
      </div>
    )}
    </div>
  );
}

export default App;