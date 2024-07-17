// Wait for the DOM to be fully loaded before running any code
document.addEventListener('DOMContentLoaded', function() {
    const pdfUploadForm = document.getElementById('pdf-upload-form');
  
    // Handle form submission
    pdfUploadForm.addEventListener('submit', function(event) {
      event.preventDefault(); // Prevent the default form submission
  
      const formData = new FormData(pdfUploadForm); // Create a FormData object from the form
      fetch('/upload_pdf', {
        method: 'POST',
        body: formData,
      })
      .then(response => response.json())
      .then(data => {
        // Handle the response from the server
        console.log(data); // Log the response for debugging
        alert('PDF Uploaded Successfully!'); // Show an alert or update UI as needed
  
        // After uploading, initiate a chat session
        initiateChatSession();
      })
      .catch(error => {
        console.error('Error:', error);
        alert('Error uploading PDF. Please try again.'); // Show an alert on error
      });
    });
  
    function initiateChatSession() {
      fetch('/initiate_chat', {
        method: 'POST',
      })
      .then(response => response.json())
      .then(data => {
        // Handle the response from the server
        console.log(data); // Log the response for debugging
        if (data.response) {
          document.getElementById('response').innerText = `Hello dear user, ${data.response}`;
        } else {
          document.getElementById('response').innerText = 'Chat initialization failed.';
        }
      })
      .catch(error => {
        console.error('Error:', error);
        alert('Error initiating chat. Please try again.'); // Show an alert on error
      });
    }
  });

  
  
