export const fetchOffers = async () => {
    try {
        const res = await fetch("http://127.0.0.1:5000/offers");
        return await res.json();
    } catch (err) {
        console.error("Failed to fetch offers:", err);
        return [];
    }
};
