import { useEffect, useState } from "react";
import { fetchOffers } from "./api";
import "./App.css"; // import styles

function OffersTable() {
    const [offers, setOffers] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchOffers()
            .then((data) => {
                setOffers(data);
                setLoading(false);
            })
            .catch((err) => {
                console.error(err);
                setLoading(false);
            });
    }, []);

    if (loading)
        return <div className="loading">Loading offers...</div>;

    if (!offers.length)
        return <div className="loading">No offers found.</div>;

    return (
        <div className="table-container">
            <table className="offers-table">
                <thead>
                <tr>
                    <th>Store</th>
                    <th>Cashback (%)</th>
                    <th>Link</th>
                    <th>Scraped At</th>
                </tr>
                </thead>
                <tbody>
                {offers.map((offer, idx) => (
                    <tr key={idx}>
                        <td>{offer.store}</td>
                        <td>{offer.cashback}</td>
                        <td>
                            <a
                                href={offer.link}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="visit-btn"
                            >
                                Visit
                            </a>
                        </td>
                        <td>{new Date(offer.scraped_at).toLocaleString()}</td>
                    </tr>
                ))}
                </tbody>
            </table>
        </div>
    );
}

export default OffersTable;
