// frontend/src/api.js

// Fetch offers from your backend
export async function fetchOffers() {
    const res = await fetch("https://your-backend.onrender.com/offers"); // <-- your deployed backend URL
    if (!res.ok) throw new Error("Failed to fetch offers");
    return res.json(); // Returns array of offers: { store, cashback, link, scraped_at }
}
