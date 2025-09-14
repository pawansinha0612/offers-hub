import React, { useEffect, useState } from 'react';
import offersData from './offers.json';

function App() {
    const [offers, setOffers] = useState([]);
    const [search, setSearch] = useState('');

    useEffect(() => {
        setOffers(offersData);
    }, []);

    // Helpers to extract numbers properly
    const parseCashbackValue = (cashback) => {
        if (!cashback) return 0;
        return parseFloat(cashback.replace(/[^0-9.]/g, '')) || 0;
    };

    const isPercentage = (cashback) => cashback.includes('%');
    const isDollar = (cashback) => cashback.includes('$');

    // Split offers into percentage and dollar types
    const percentOffers = offers.filter(o => isPercentage(o.cashback));
    const dollarOffers = offers.filter(o => isDollar(o.cashback));

    // Sort separately
    const topPercentOffers = [...percentOffers]
        .sort((a, b) => parseCashbackValue(b.cashback) - parseCashbackValue(a.cashback))
        .slice(0, 3);

    const topDollarOffers = [...dollarOffers]
        .sort((a, b) => parseCashbackValue(b.cashback) - parseCashbackValue(a.cashback))
        .slice(0, 3);

    const filteredOffers = offers.filter(offer =>
        offer.store.toLowerCase().includes(search.toLowerCase())
    );

    const getCashbackColor = (cashback) => {
        if (isDollar(cashback)) return 'purple'; // $ offers highlighted differently
        const cb = parseCashbackValue(cashback);
        if (cb >= 20) return 'green';
        if (cb >= 10) return 'blue';
        return 'orange';
    };

    const OfferCard = ({ offer }) => (
        <div className="col-12 col-sm-6 col-lg-4">
            <div
                className="card h-100 shadow-lg border-primary offer-card"
                style={{
                    borderWidth: '2px',
                    backgroundColor: '#f8f9fa',
                    transition: 'transform 0.2s, box-shadow 0.2s',
                    cursor: 'pointer',
                }}
                onMouseEnter={e => {
                    e.currentTarget.style.transform = 'translateY(-5px) scale(1.03)';
                    e.currentTarget.style.boxShadow = '0 8px 25px rgba(0,0,0,0.2)';
                }}
                onMouseLeave={e => {
                    e.currentTarget.style.transform = 'translateY(0) scale(1)';
                    e.currentTarget.style.boxShadow = '0 2px 10px rgba(0,0,0,0.1)';
                }}
            >
                <div className="card-body d-flex flex-column">
                    <h5 className="card-title">{offer.store}</h5>
                    <span
                        className="badge text-white mb-2"
                        style={{
                            backgroundColor: getCashbackColor(offer.cashback),
                            fontSize: '0.9rem',
                            padding: '5px 10px',
                        }}
                    >
                        {offer.cashback} Cashback
                    </span>
                    <a
                        href={offer.link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="btn btn-primary mt-auto"
                    >
                        Visit Store
                    </a>
                    <p
                        className="card-text text-muted mt-2"
                        style={{ fontSize: '0.85rem' }}
                    >
                        Scraped on: {offer.scraped_at || 'N/A'}
                    </p>
                </div>
            </div>
        </div>
    );

    return (
        <div className="container my-5">
            {/* Header */}
            <header className="text-center mb-5">
                <h1>🔥 Consolidated Offers Hub</h1>
                <p className="lead">All the best cashback & deals in one place!</p>
            </header>

            {/* Search Bar */}
            <div className="mb-5">
                <input
                    type="text"
                    className="form-control"
                    placeholder="Search by store..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                />
            </div>

            {/* Featured Offers */}
            <section className="mb-5">
                <h3 className="mb-4">⭐ Featured Offers</h3>

                {/* Percentage Offers */}
                {topPercentOffers.length > 0 && (
                    <>
                        <h5 className="mb-3">Top % Cashback</h5>
                        <div className="row g-4 mb-4">
                            {topPercentOffers.map((offer, index) => (
                                <OfferCard key={index} offer={offer} />
                            ))}
                        </div>
                    </>
                )}

                {/* Dollar Offers */}
                {topDollarOffers.length > 0 && (
                    <>
                        <h5 className="mb-3">Top $ Cashback</h5>
                        <div className="row g-4">
                            {topDollarOffers.map((offer, index) => (
                                <OfferCard key={index} offer={offer} />
                            ))}
                        </div>
                    </>
                )}
            </section>

            {/* All Offers */}
            <section>
                <h3 className="mb-4">All Offers</h3>
                <div className="row g-4">
                    {filteredOffers.length === 0 && (
                        <p className="text-center">No offers found.</p>
                    )}
                    {filteredOffers.map((offer, index) => (
                        <OfferCard key={index} offer={offer} />
                    ))}
                </div>
            </section>

            {/* Footer */}
            <footer className="text-center mt-5 mb-3 text-muted">
                © 2025 Consolidated Offers Hub. All rights reserved.
            </footer>
        </div>
    );
}

export default App;
