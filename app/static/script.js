// Listens for Edit button click to update action URL to add the trip ID of the edit form in the modal and modal title
document.addEventListener('DOMContentLoaded', () => {  
    document.querySelectorAll('button[data-action="edit"]').forEach(button => {
        button.addEventListener('click', (event) => {
            event.preventDefault(); // Prevent form submission
            document.getElementById("editModalTitleLabel").textContent = `Edit trip ${button.getAttribute('data-job-id')}`;
            document.editForm.action = `/edit_job/${button.getAttribute('data-job-id')}`;
        });
    });
});

