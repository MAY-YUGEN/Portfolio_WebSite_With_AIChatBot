// This file is used for back to top button

console.log(".js for back to top button is running.")

const backToTop = document.querySelector(".back-to-top");
const observerTarget = document.querySelector("header");

if (backToTop && observerTarget) {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (!entry.isIntersecting) {
                backToTop.classList.add("show");
            } else {
                backToTop.classList.remove("show");
            }
        });
    });

    observer.observe(observerTarget);

    window.addEventListener("scroll", function () {
        if (window.scrollY > 100) {
            backToTop.classList.add("show");
        } else {
            backToTop.classList.remove("show");
        }
    });

    // Scroll to top when clicked
    backToTop.addEventListener("click", function () {
        window.scrollTo({ top: 0, behavior: "smooth" });
    });

} else {
    console.error("Back-to-top button or observer target not found.");
}