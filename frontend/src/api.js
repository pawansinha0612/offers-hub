export const fetchOffers = () =>
    fetch("https://offers-hub.onrender.com/offers")
        .then(res => res.json());
