document.getElementById('emailForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = new FormData(e.target);

    const response = await fetch('/send-email', {
        method: 'POST',
        body: formData,
    });

    if (response.ok) {
        const successMessages = document.getElementById('successMessages');
        successMessages.innerHTML = ''; // Clear any existing success messages

        // Parse success messages as JSON from the response body
        const successMessagesData = await response.json();

        // Display individual success messages for each contact
        successMessagesData.forEach((message) => {
            const successMessage = document.createElement('p');
            successMessage.textContent = message;
            successMessages.appendChild(successMessage);
        });

        e.target.reset();
    } else {
        alert('Error sending emails');
    }
});

document.querySelector('input[name="contactsFile"]').addEventListener('change', (e) => {
    const fileInput = e.target;
    const allowedExtensions = /(\.txt)$/i;
    if (!allowedExtensions.exec(fileInput.value)) {
        alert('Please select a .txt file for contacts.');
        fileInput.value = '';
    }
});
