import { useEffect, useState } from "react";
import { fetchOffers } from "./api";

function OffersTable() {
    const [offers, setOffers] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchOffers()
            .then(data => {
                setOffers(data);
                setLoading(false);
            })
            .catch(err => {
                console.error(err);
                setLoading(false);
            });
    }, []);

    if (loading) return <div>Loading offers...</div>;

    return (
        <table>
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
                    <td><a href={offer.link} target="_blank" rel="noopener noreferrer">Visit</a></td>
                    <td>{offer.scraped_at}</td>
                </tr>
            ))}
            </tbody>
        </table>
    );
}

export default OffersTable;
