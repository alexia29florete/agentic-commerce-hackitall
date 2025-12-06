document.addEventListener("DOMContentLoaded", () => {

    // ---------- LOCATIE O SINGURA DATA ----------
    const savedLocation = sessionStorage.getItem("location");
    if (savedLocation) {
        const data = JSON.parse(savedLocation);
        document.getElementById("location").innerHTML = `
            Te afli în: <b>${data.city}</b>, <b>${data.country}</b>
        `;
    } else {
        navigator.geolocation.getCurrentPosition(
            async (pos) => {
                const lat = pos.coords.latitude;
                const lon = pos.coords.longitude;

                document.getElementById("location").innerText = "Detectez locația...";

                try {
                    const resp = await fetch("/location", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ lat, lon })
                    });

                    const data = await resp.json();
                    document.getElementById("location").innerHTML = `
                        Te afli în: <b>${data.city}</b>, <b>${data.country}</b>
                    `;

                    sessionStorage.setItem("location", JSON.stringify(data));
                } catch(e) {
                    console.error("Eroare la preluarea locației:", e);
                    document.getElementById("location").innerText = "Locație indisponibilă";
                }
            },
            (err) => {
                document.getElementById("location").innerText = "Permisiune pentru locație refuzată!";
            },
            { enableHighAccuracy: true }
        );
    }

    // ---------- SEARCH PRODUSE RAPID ----------
    document.getElementById("searchBtn").onclick = () => {
        const query = document.getElementById("searchInput").value;
        if(!query) return;

        const products = [
            {name: `${query} Local 1`, price: "20 EUR"},
            {name: `${query} Local 2`, price: "25 EUR"},
            {name: `${query} Premium`, price: "45 EUR"}
        ];

        localStorage.setItem("products", JSON.stringify(products));

        document.getElementById("results").innerHTML = products.map((p,i) => `
            <div class="product">
                <b>${p.name}</b> - ${p.price} 
                <a href="/customize/${i}" class="star" style="cursor:pointer;">💬</a>
            </div>
        `).join("");
    };

    // ---------- BUTON „Caută altele” ----------
    document.getElementById("newSearchBtn").onclick = () => {
        document.getElementById("searchInput").value = "";
        document.getElementById("results").innerHTML = "";
    };

});
