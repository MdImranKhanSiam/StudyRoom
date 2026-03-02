const searchInput = document.getElementById("user-search");
const resultsDiv = document.getElementById("search-results");
const selectedDiv = document.getElementById("selected-users");
const membersInput = document.getElementById("members-input");
const loader = document.getElementById("loader");
const roomForm = document.getElementById("roomForm");

let selectedUsers = {};

searchInput.addEventListener("input", async function () {
    const username = this.value.trim();

    if( username.length < 2 ) {
        resultsDiv.innerHTML = "";
        loader.style.display = "none";
        return;
    }

    loader.style.display = "inline";

    const searched_users = await fetch(`/search_users/?username=${username}`);
    const users = await searched_users.json();
    loader.style.display = "none";
    resultsDiv.innerHTML = "";
    
    users.forEach(user => {
        if (selectedUsers[user.id]) return;

        const div = document.createElement("div");
        div.innerHTML = `
            <span>
                ${user.username}
            </span>
            <button style="
                
                background-color:#3CB371; color:white; border:none; border-radius:6px; padding:10px 15px; cursor:pointer;"
                onmouseover="this.style.backgroundColor='#2E8B57'"
                onmouseout="this.style.backgroundColor='#3CB371'

            " type="button">Add</button><br><br>
        `;

        div.querySelector("button").onclick = () => addUser(user);
        resultsDiv.appendChild(div);
    });
});

function addUser(user) {
    selectedUsers[user.id] = user.username;
    const div = document.createElement("div");
    div.id = `selected-${user.id}`;
    div.innerHTML = `
        ${user.username}
        <button style="
            background-color:#FF6347; color:white; border:none; border-radius:6px; padding:10px 15px; cursor:pointer;"
            onmouseover="this.style.backgroundColor='#E5533D'"
            onmouseout="this.style.backgroundColor='#FF6347'
        " type="button">Remove</button><br><br>
    `;

    div.querySelector("button").onclick = () => removeUser(user.id);
    selectedDiv.appendChild(div);
    updateHiddenInput();
}

function removeUser(userId) {
    delete selectedUsers[userId];
    document.getElementById(`selected-${userId}`).remove();
    updateHiddenInput();
}

function updateHiddenInput() {
    membersInput.value = Object.keys(selectedUsers).join(",");
}

function showError(message) {
    const errorBox = document.getElementById("floatingError");

    errorBox.textContent = message;
    errorBox.classList.add("show");

    setTimeout(() => {
        errorBox.classList.remove("show");
    }, 3000);

}

roomForm.addEventListener("submit", function(e) {
    if (Object.keys(selectedUsers).length === 0) {
        e.preventDefault();
        showError("Please select at least one member to create a room");
    }
});