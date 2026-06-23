const form = document.querySelector("form");
const loader = document.getElementById("loader");

if (form && loader) {
    form.addEventListener("submit", () => {
        loader.style.display = "block";
    });
}


const darkBtn = document.getElementById("dark-btn");

if (darkBtn) {
    darkBtn.addEventListener(
        "click",
        () => {
            document.body.classList.toggle(
                "dark-mode"
            );
        }
    );
}