window.onload = function() {
    // Get all the messages
    var messages = document.querySelectorAll('.alert');
    messages.forEach(function(message) {
        setTimeout(function() {
            message.style.display = 'none';
        }, 5000);  // 5000 milliseconds (5 seconds)
    });
};


// Char room Scripts Begin


// Function to show the context menu
function showContextMenu(event, messageId) {
    event.preventDefault();
    event.stopPropagation();

    // Get the context menu
    const contextMenu = document.getElementById('context-menu');

    // Set the message ID for later use
    contextMenuMessageId = messageId;

    // Get position to show the menu
    const { clientX: x, clientY: y } = event;
    const { innerWidth: width, innerHeight: height } = window;

    // Prevent the context menu from overflowing
    const menuWidth = contextMenu.offsetWidth;
    const menuHeight = contextMenu.offsetHeight;
    const xPos = x + menuWidth > width ? x - menuWidth : x;
    const yPos = y + menuHeight > height ? y - menuHeight : y;

    // Check if the logged-in user is the sender
    const messageElement = document.getElementById('message-' + messageId);
    const messageUserId = messageElement.getAttribute('data-user-id');
    const currentUserId = "{{ request.user.id }}"; 
    console.log(messageUserId);

    // Show or hide Edit/Delete options based on user
    const editOption = document.getElementById('edit-option');
    const deleteOption = document.getElementById('delete-option');
    if (messageUserId === currentUserId) {
        editOption.style.display = 'block';
        deleteOption.style.display = 'block';
    } else {
        editOption.style.display = 'none';
        deleteOption.style.display = 'none';
    }

    // Display the context menu
    contextMenu.style.top = `${yPos}px`;
    contextMenu.style.left = `${xPos}px`;
    contextMenu.style.display = 'block';
}

// Handle edit option click
document.getElementById('edit-option').addEventListener('click', () => {
    const editForm = document.getElementById('editMessageForm');

    // Get the message content
    const message = document.getElementById('message-' + contextMenuMessageId);
    const messageContent = message.querySelector('.message-content').textContent.trim();

    // Set the content in the modal form
    const editContentInput = document.getElementById('edit-message-content');
    editContentInput.value = messageContent;

    // Correctly replace the '0' with the actual message ID in the form action
    const formAction = "{% url 'edit_message' room_id=chat_room.id message_id=0 %}".replace('0', contextMenuMessageId);
    editForm.action = formAction;

    const editModal = new bootstrap.Modal(document.getElementById('editMessageModal'));
    editModal.show();
    document.getElementById('context-menu').style.display = 'none';
});

// Handle reply option click
document.getElementById('reply-option').addEventListener('click', () => {
    const replyInput = document.getElementById('reply-to-input');
    replyInput.value = contextMenuMessageId;
    const messageInput = document.getElementById('message-input');
    messageInput.focus();
    document.getElementById('context-menu').style.display = 'none';
});

// Handle mention option click
document.getElementById('mention-option').addEventListener('click', () => {
    const message = document.getElementById('message-' + contextMenuMessageId);
    const messageUser = message.querySelector('.username').textContent.trim();
    const messageInput = document.getElementById('message-input');
    messageInput.value += '@' + messageUser + ' ';
    messageInput.focus();
    document.getElementById('context-menu').style.display = 'none';
});

// Handle delete option click
document.getElementById('delete-option').addEventListener('click', () => {
    // Open the delete confirmation modal
    const deleteModal = new bootstrap.Modal(document.getElementById('deleteConfirmationModal'));
    deleteModal.show();

    // Close the context menu
    document.getElementById('context-menu').style.display = 'none';
});

// Handle confirm delete action
document.getElementById('confirm-delete-button').addEventListener('click', () => {
    // Send delete request via AJAX or redirect to delete view
    window.location.href = "{% url 'delete_message' 0 %}".replace('0', contextMenuMessageId);
});

// Hide the context menu when clicking elsewhere
document.addEventListener('click', () => {
    const contextMenu = document.getElementById('context-menu');
    contextMenu.style.display = 'none';
});

// Chatroom Scripts End