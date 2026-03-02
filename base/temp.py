card.innerHTML = `
            <div class="chat-left">
                <div class="avatar">
                    ${chat.type === "group" ? "G" : chat.name[0]}
                </div>
                <div class="chat-info">
                    <h4>${chat.name}</h4>
                    <p>${chat.lastMessage}</p>
                </div>
            </div>

            <div class="chat-right">
                <div class="timestamp">${chat.timestamp}</div>
                ${chat.unread > 0 ? `<div class="unread-badge">${chat.unread}</div>` : ""}
            </div>
        `;

                card.addEventListener("click", () => {
                    window.location.href = `/message/${chat.id}/`;
                });
