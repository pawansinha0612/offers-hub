export const fetchOffers = async () => {
    try {

        const res = await fetch("https://offers-hub.onrender.com/offers")
        return await res.json();
    } catch (err) {
        console.error("Failed to fetch offers:", err);
        return [];
    }
};
