export async function fetchOffers() {
    try {
        const res = await fetch("/offers.json", { cache: "no-store" });
        if (!res.ok) throw new Error("Failed to fetch offers.json");

        const data = await res.json();
        return data;
    } catch (err) {
        console.error("Error fetching static offers:", err);
        return [];
    }
}
