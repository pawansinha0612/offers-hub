import React, { useEffect, useState } from "react";
import { fetchOffers } from "./api";

function App() {
    const [offers, setOffers] = useState([]);
    const [filterCategory, setFilterCategory] = useState("All");

    useEffect(() => {
        fetchOffers().then(data => setOffers(data));
    }, []);

    const allCategories = ["All", ...new Set(offers.map(o => o.Category))];
    const filteredOffers = filterCategory === "All"
        ? offers
        : offers.filter(o => o.Category === filterCategory);

    return (
        <div style={{ padding: "20px" }}>
            <h1>Offers-Hub Dashboard</h1>

            <label>Filter by Category: </label>
            <select onChange={e => setFilterCategory(e.target.value)}>
                {allCategories.map(c => <option key={c}>{c}</option>)}
            </select>

            <table border="1" cellPadding="10" style={{ marginTop: "20px" }}>
                <thead>
                <tr>
                    <th>Cashback (%)</th>
                    {/*<th>Existing User Cashback</th>*/}
                    <th>Link</th>
                    <th>Store</th>
                    {/*<th>Category</th>*/}
                </tr>
                </thead>
                <tbody>
                {filteredOffers.map((offer, idzx) => (
                    <tr key={idx}>
                        <td>{offer["Cashback (%)"]}</td>
                        {/*<td>{offer["Existing User Cashback"]}</td>*/}
                        <td>
                            <a href={offer.Link} target="_blank" rel="noreferrer">Visit</a>
                        </td>
                        <td>{offer.Store}</td>
                        {/*<td>{offer.Category}</td>*/}
                    </tr>
                ))}
                </tbody>
            </table>
        </div>
    );
}

export default App;
