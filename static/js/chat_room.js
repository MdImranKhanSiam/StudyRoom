    console.log('here')
    
    
    
    const current_user_id = {{ request.user.id }};
    const default_user_photo_url = "{% static 'image/other/default-avatar.jpg' %}";
    const roomId = {{ room.id }};

    document.addEventListener("DOMContentLoaded", () => {
        loadMessages();
    });
    
    let page = 1;
    let loading = false;
    let hasNext = true;

    const chatBox = document.getElementById('chat-box');

    chatBox.addEventListener('scroll', () => {
        if (chatBox.scrollTop === 0) {
            loadMessages(true);
        }
    });

    async function loadMessages(loadOlder = false) {
        if (loading || (!hasNext && loadOlder)) return;
        loading = true;

        try {
            const response = await fetch(`/messages/${roomId}/?page=${page}`);
            const data = await response.json();

            if (loadOlder) {
                const oldScrollHeight = chatBox.scrollHeight;

                data.messages.forEach(msg => {
                prependMessage(msg);
                });

                chatBox.scrollTop = chatBox.scrollHeight - oldScrollHeight;
            } else {
                data.messages.forEach(msg => {
                    prependMessage(msg);
                });

                chatBox.scrollTop = chatBox.scrollHeight;
            }

            hasNext = data.has_next;
            page++;
        } catch (error) {
            console.error('Failed to load messages:', error);
        } finally {
            loading = false;
        }
    } 

    
    function prependMessage(msg, functionType='normal') {
        const div = document.createElement('div');
        const avatar_url = default_user_photo_url;
        const message_class = Number(msg.sender_id) === Number(current_user_id) ? 'me' : 'other';

        div.innerHTML = `
            <div class="users-message">
                <span class="users-message-img">
                    <a href="#">
                        <img src="${avatar_url}" alt="avatar">
                    </a>
                </span>

                <div class="message ${message_class}">
                    <small>
                        <a href="#" class="message-user-name">@${msg.sender_name}</a>
                        • ${msg.timestamp}
                    </small>
                    ${msg.content}
                </div>
            </div>
        `;

        if (functionType==='new_message') {
            chatBox.appendChild(div);

            const distanceFromBottom = chatBox.scrollHeight - chatBox.scrollTop - chatBox.clientHeight;

            if (distanceFromBottom < 300) {
                chatBox.scrollTop = chatBox.scrollHeight;
            }
        } else {
            chatBox.prepend(div);
        }
    }

    function newMessage(msg) {
        const div = document.createElement('div');
        div.innerHTML = `
            ${msg.sender_id} -> ${msg.sender_name}: ${msg.content} <small>Sent at ${msg.timestamp}</small>
        `;
        chatBox.appendChild(div);

        const distanceFromBottom = chatBox.scrollHeight - chatBox.scrollTop - chatBox.clientHeight;

        if (distanceFromBottom < 300) {
            chatBox.scrollTop = chatBox.scrollHeight;
        }
    }




    let typingUsers = {};      // { user_id: {name, avatar} }
    let typingTimeouts = {};   // { user_id: timeoutID }

    function showTypingBubble(user) {
    const userId = user.user_id; 

    // Add or update the typing user
    typingUsers[userId] = {
        name: user.name || 'Someone',
        avatar: user.avatar || default_user_photo_url
    };

    // Clear previous timeout for this user
    if (typingTimeouts[userId]) clearTimeout(typingTimeouts[userId]);

    // Set timeout to remove after 2s
    typingTimeouts[userId] = setTimeout(() => {
        delete typingUsers[userId];
        updateTypingIndicators();
    }, 2000);

    updateTypingIndicators();
}

function updateTypingIndicators() {
    
    document.querySelectorAll('.typing-bubble').forEach(b => b.remove());

    const typingUserIds = Object.keys(typingUsers);

    if (typingUserIds.length === 0) return;

    if (typingUserIds.length <= 3) {
        // Show each typing user as a bubble
        typingUserIds.forEach(id => {
            const user = typingUsers[id];
            const bubble = document.createElement('div');
            bubble.classList.add('users-message', 'typing-bubble');
            bubble.style.display = 'inline-flex';
            bubble.style.marginRight = '8px';

            bubble.innerHTML = `
                <span class="users-message-img">
                    <img src="${user.avatar}" alt="avatar" style="width:50px; height:50px">
                </span>
                <div class="message other">
                    <small>
                        <a href="#" class="message-user-name">@${user.name}</a>
                    </small>
                    <div class="typing-dots">
                        <span></span><span></span><span></span>
                    </div>
                </div>
            `;
            chatBox.appendChild(bubble);
        });
    } else {
        // Show a single bubble for multiple people
        const bubble = document.createElement('div');
        bubble.classList.add('users-message', 'typing-bubble');
        bubble.innerHTML = `
            <div class="message other">
                <small>Multiple people are typing...</small>
                <div class="typing-dots">
                    <span></span><span></span><span></span>
                </div>
            </div>
        `;
        chatBox.appendChild(bubble);
    }

    // Scroll to bottom
    // chatBox.scrollTop = chatBox.scrollHeight;
}










    let socket;

    // wss if for production
    const wsScheme = window.location.protocol === "https:" ? "wss" : "ws";

    function initWebSocket() {
        const url = `${wsScheme}://${window.location.host}/ws/chat/${roomId}/`;

        if (socket && socket.readyState === WebSocket.OPEN) return;

        socket = new WebSocket(url);

        socket.onmessage = function(e) {
            const data = JSON.parse(e.data);

            if(data.type === 'message') {
                the_data = {
                        'sender_id' : data.message.sender_id,
                        'sender_name' : data.message.sender_name,
                        'content' : data.message.content,
                        'timestamp' : data.message.timestamp
                    }
                
                prependMessage(the_data, 'new_message');
            }

            if(data.type === 'typing') {
                // console.log(`${data.user} is typing...`);
                if (data.user_id !== current_user_id) {
                    showTypingBubble({
                        user_id: data.user_id,
                        name: data.user,
                    // avatar: data.avatar // optional, can come from backend
                    });
                }
            }
        }

        function sendMessage() {
            socket.send(
                JSON.stringify({
                    'type' : 'message',
                    'message' : input.value
                })
            );

            input.value='';
        }
        let lastTypingSent = 0;
        const input = document.getElementById('msg_input');
        const sendButton = document.getElementById('send-button');

        input.addEventListener('input', () => {
            const now = Date.now();

            if (now - lastTypingSent > 500) {
                socket.send(
                    JSON.stringify({ 
                        type: 'typing' 
                    })
                );
                lastTypingSent = now;
            }
        });

        input.addEventListener('keydown', e => {
            if(e.key==='Enter') {
                sendMessage();
            }
        });

        sendButton.addEventListener('click', e => {
            sendMessage();
        });
    }

    initWebSocket();

    window.addEventListener('beforeunload', () => {
        if(socket) socket.close();
    });

