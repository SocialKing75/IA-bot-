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
      {/* 1. BARRE DE NAVIGATION (HAUT) */}
      <nav className="navbar">
        <div className="nav-logo-text">Sentiers Libres</div> 
        <ul className="nav-links">
          <li><a href="#accueil">Accueil</a></li>
          <li><a href="#conseils">Nos conseils</a></li>
          <li><a href="#rando">Randonnées</a></li>
          <li><a href="#articles">Articles</a></li>
        </ul>
      </nav>

      {/* 2. SECTION ACCROCHE */}
      <header className="hero-header" id="accueil">
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
      <div className="main-content" id="conseils">
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
      <section className="trending-section" id="rando">
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

      {/* 5. SECTION ARTICLES - AVEC LIENS CLIQUABLES */}
      <section className="articles-section" id="articles">
        <div className="section-header">
          <h2>Articles</h2>
          <p>À lire pour mieux préparer vos aventures</p>
        </div>

        <div className="articles-grid">
          <article className="article-card">
            <img src="/Image Article 1.jpg" alt="Marcher vers l’inattendu" />
            <span className="article-date">04 décembre 2025</span>
            <h3>Marcher vers l’inattendu</h3>
            <span className="category-badge">Exploration</span>
            <p>Cela fait un moment que je souhaitais tenter la randonnée sur glacier.Après plus d’un an en Islande, j’ai enfin testé cette activité d’aventure.</p>
            <button 
              className="read-more-btn"
              onClick={() => window.open("https://guidetoiceland.is/fr/contactez-des-blogueurs-en-islande/emilie-pasquet/la-randonnee-sur-glacier-en-islande", "_blank")}
            >
              Lire l'article →
            </button>
          </article>

          <article className="article-card">
            <img src="/Image Article 2.jpg" alt="Préparer l’essentiel" />
            <span className="article-date">25 novembre 2025</span>
            <h3>Préparer l'essentiel</h3>
            <span className="category-badge">Organisation</span>
            <p>Que l’on arpente les sentiers enneigés en plein cœur de l’hiver ou que l’on profite des journées fraîches de mi-saison,  bien s’équiper reste la clé..</p>
            <button 
              className="read-more-btn"
              onClick={() => window.open("https://www.mon-sejour-en-montagne.com/tests/10-equipements-incontournables-pour-profiter-de-la-randonnee-meme-en-plein-hiver/", "_blank")}
            >
              Lire l'article →
            </button>
          </article>

          <article className="article-card">
            <img src="/Image Article 3.jpg" alt="Les cinq plus beaux endroits pour faire du camping" />
            <span className="article-date">31 mars 2025</span>
            <h3>Les cinq plus beaux endroits pour faire du camping</h3>
            <span className="category-badge">Camping</span>
            <p>C’est indéniable, le camping sauvage demande de l’énergie. Ainsi qu’un certain portefeuille, si vous ne pouvez pas louer ou emprunter... </p>
            <button 
              className="read-more-btn"
              onClick={() => window.open("https://www.nationalgeographic.fr/voyage/guide-conseils-trekking-randonnees-les-cinq-plus-beaux-endroits-pour-faire-du-camping-sauvage-en-europe", "_blank")}
            >
              Lire l'article →
            </button>
          </article>
        </div>
      </section>

      {/* 6. PIED DE PAGE (BAS) */}
      <footer className="footer">
        <div className="footer-content">
          <div className="footer-column logo-col">
            <img src="/Logo Sentiers Libres.png" alt="Sentiers Libres" className="footer-logo-img" />
          </div>
          <div className="footer-column links-col">
            <h3>Plan du site</h3>
            <div className="footer-links-grid">
              <div className="footer-links-left">
                <a href="#accueil">Accueil</a>
                <a href="#conseils">Nos conseils</a>
                <a href="#rando">Randonnées incontournables</a>
              </div>
              <div className="footer-links-right">
                <a href="#articles">Articles</a>
              </div>
            </div>
          </div>
          <div className="footer-column social-col">
            <h3>Suivez-nous sur nos réseaux !</h3>
            <div className="social-icons">
              <a href="https://linkedin.com" target="_blank" rel="noreferrer">
                <img src="/Logo Linkedin.png" alt="" className="social-icon-img" />
              </a>
              <a href="https://instagram.com" target="_blank" rel="noreferrer">
                <img src="/Logo Instagram.png" alt="" className="social-icon-img" />
              </a>
              <a href="https://facebook.com" target="_blank" rel="noreferrer">
                <img src="/Logo Facebook.png" alt="" className="social-icon-img" />
              </a>
            </div>
          </div>
        </div>
        <div className="footer-bottom">
          <p>© Copyright 2026 | <a href="#">Mentions légales</a> | Tous droits réservés | Propulsé par Sentiers Libres®</p>
        </div>
      </footer>

      {/* MODAL CHAT OVERLAY */}
      {isChatOpen && (
        <div className="chat-overlay">
          <div className="chat-widget">
            <div className="chat-header">
              <h3>Assistant randonnée</h3>
              <button onClick={() => setIsChatOpen(false)}>✕</button>
            </div>
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