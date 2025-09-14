// frontend/src/api.js

export async function fetchOffers() {
    try {
        const res = await fetch("https://offers-hub.onrender.com/offers");
        if (!res.ok) throw new Error("Backend request failed");

        const data = await res.json();

        // If backend returns too few offers, fallback to static JSON
        if (!Array.isArray(data) || data.length < 50) {
            console.warn(
                `Backend returned only ${data.length} offers. Falling back to static offers.json`
            );
            return fetchStaticOffers();
        }

        return data;
    } catch (error) {
        console.error("Error fetching from backend:", error);
        return fetchStaticOffers();
    }
}

async function fetchStaticOffers() {
    const res = await fetch("/offers.json"); // This should be in public/offers.json
    if (!res.ok) throw new Error("Failed to fetch static offers.json");
    return res.json();
}
