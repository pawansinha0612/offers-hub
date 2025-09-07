// frontend/src/OffersTable.js
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

    if (loading)
        return <div className="text-center py-10 text-gray-500">Loading offers...</div>;

    if (!offers.length)
        return <div className="text-center py-10 text-gray-500">No offers available.</div>;

    return (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6 p-6">
            {offers.map((offer, idx) => (
                <div
                    key={idx}
                    className="bg-white rounded-lg shadow-md p-5 hover:shadow-xl transition duration-300"
                >
                    <h3 className="text-lg font-semibold mb-2">{offer.store}</h3>
                    <p className="text-gray-700 mb-2">
                        <span className="font-medium">Cashback:</span> {offer.cashback}%
                    </p>
                    <p className="mb-2">
                        <a
                            href={offer.link}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-600 hover:underline font-medium"
                        >
                            Visit Store
                        </a>
                    </p>
                    <p className="text-gray-400 text-sm">
                        Scraped: {new Date(offer.scraped_at).toLocaleString()}
                    </p>
                </div>
            ))}
        </div>
    );
}

export default OffersTable;
