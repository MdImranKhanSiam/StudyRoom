
/* DESKTOP RENDER */
const desktopContainer = document.getElementById("desktopUsers");

users.forEach(user => {
    const card = document.createElement("div");
    card.className = "user-card";

    card.innerHTML = `
        <div class="user-left">
            <img src="${user.avatar}" class="user-avatar">
            <div>
                <div class="user-name">${user.name}</div>
                <div class="user-username">${user.username}</div>
            </div>
        </div>
        <button class="follow-btn">Follow</button>
    `;

    desktopContainer.appendChild(card);
});

/* MOBILE RENDER */
const mobileContainer = document.getElementById("mobileUsers");

users.forEach(user => {
    const card = document.createElement("div");
    card.className = "mobile-user-card";

    card.innerHTML = `
        <div style="display:flex; align-items:center; gap:12px;">
            <img src="${user.avatar}" class="user-avatar">
            <div>
                <div class="user-name">${user.name}</div>
                <div class="user-username">${user.username}</div>
            </div>
        </div>
        <button class="follow-btn">Follow</button>
    `;

    mobileContainer.appendChild(card);
});




document.addEventListener("DOMContentLoaded", function () {
    const button = document.querySelector(".panel-btn");
    button.classList.add("active")
});

const buttons = document.querySelectorAll(".panel-btn");


buttons.forEach(button => {
    button.addEventListener("click", function () {
        // Remove active from all
        buttons.forEach(btn => btn.classList.remove("active"));

        // Add active to clicked one
        this.classList.add("active");
    });
});