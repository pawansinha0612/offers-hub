import React from 'react';

export default function OfferCard({ offer, search }) {
    const cashbackValue = parseFloat(offer.cashback);
    let badgeColor = '';
    let badgeStyle = {
        padding: '0.25rem 0.5rem', // smaller padding
        fontWeight: 'bold',
        borderRadius: '0.25rem',
        display: 'inline-block',
        fontSize: '0.85rem', // smaller text
    };


    let cardBaseStyle = {
        transition: 'transform 0.2s, box-shadow 0.2s',
        cursor: 'pointer',
        marginBottom: '1rem',
        border: '1px solid #e0e0e0',
        borderRadius: '0.25rem',
    };

    if (cashbackValue >= 20) {
        badgeColor = '#28a745'; // green
        badgeStyle = {
            ...badgeStyle,
            backgroundColor: badgeColor,
            color: 'white',
            animation: 'pulse 1s infinite alternate'
        };
        cardBaseStyle = {
            ...cardBaseStyle,
            boxShadow: '0 0 15px 2px rgba(40,167,69,0.5)', // green glow
        };
    } else if (cashbackValue >= 10) {
        badgeColor = '#007bff'; // blue
        badgeStyle = { ...badgeStyle, backgroundColor: badgeColor, color: 'white' };
    } else {
        badgeColor = '#ffc107'; // yellow
        badgeStyle = { ...badgeStyle, backgroundColor: badgeColor, color: 'black' };
    }

    // Highlight matched search text
    const highlightMatch = (text, query) => {
        if (!query) return text;
        const regex = new RegExp(`(${query})`, 'gi');
        return text.split(regex).map((part, i) =>
            regex.test(part) ? <mark key={i}>{part}</mark> : part
        );
    };

    const cardHoverStyle = {
        transform: 'translateY(-5px)',
        boxShadow: cashbackValue >= 20
            ? '0 0 25px 4px rgba(40,167,69,0.7)' // intensified glow on hover
            : '0 10px 20px rgba(0,0,0,0.15)'
    };

    return (
        <>
            <style>
                {`
                    @keyframes pulse {
                        0% { transform: scale(1); }
                        50% { transform: scale(1.05); }
                        100% { transform: scale(1); }
                    }
                `}
            </style>

            <div className="col-md-4">
                <div
                    className="card h-100 shadow-sm border-0"
                    style={cardBaseStyle}
                    onMouseEnter={e => Object.assign(e.currentTarget.style, cardHoverStyle)}
                    onMouseLeave={e => Object.assign(e.currentTarget.style, cardBaseStyle)}
                >
                    <div className="card-body d-flex flex-column justify-content-between">
                        <div>
                            <h5 className="card-title">
                                <a
                                    href={offer.link}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    style={{ textDecoration: 'none', color: 'black' }}
                                >
                                    {highlightMatch(offer.store, search)}
                                </a>
                            </h5>
                            <span style={badgeStyle}>
                                Cashback: {offer.cashback}%
                            </span>
                        </div>
                        <p className="card-text text-muted small mt-3">
                            Scraped on: {offer.scraped_at || 'N/A'}
                        </p>
                    </div>
                </div>
            </div>
        </>
    );
}
