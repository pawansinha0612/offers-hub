import React, { useEffect, useState } from "react";
import { fetchOffers } from "./api";

function App() {
    const [offers, setOffers] = useState([]);

    useEffect(() => {
        fetchOffers()
            .then(data => setOffers(data))
            .catch(err => console.error("Failed to fetch offers:", err));
    }, []);

    return (
        <div style={{ padding: "20px" }}>
            <h1>Offers-Hub Dashboard</h1>

            <table border="1" cellPadding="10" style={{ marginTop: "20px" }}>
                <thead>
                <tr>
                    <th>Store</th>
                    <th>Cashback (%)</th>
                    <th>Link</th>
                </tr>
                </thead>
                <tbody>
                {offers.map((offer, idx) => (
                    <tr key={idx}>
                        <td>{offer.Store}</td>
                        <td>{offer["Cashback (%)"]}</td>
                        <td>
                            <a href={offer.Link} target="_blank" rel="noreferrer">Visit</a>
                        </td>
                    </tr>
                ))}
                </tbody>
            </table>
        </div>
    );
}

export default App;
