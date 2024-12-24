
    const deleteJob = (jobId) => {
            fetch('/delete_job/' + jobId, {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                }
            });
    };
    
    const editJob = (jobId) => {
            const newTime = prompt("Enter new time in HH:MM format:");
            if (newTime) {
                fetch('/edit_job/' + jobId, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: 'new_time=' + encodeURIComponent(newTime)
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        location.reload();
                    }
                });
            }
    };


document.addEventListener('DOMContentLoaded', () => {
    // Get the form element
    const form = document.getElementById('uploadForm');

    // Add an event listener for the form's submit event
    form.addEventListener('submit', (event) => {
    // Prevent the default form submission behavior
    event.preventDefault(); 

    // Create a FormData object to collect the form data
    const formData = new FormData(form);

    // Make a fetch request to the new endpoint
    fetch('/upload', {
        method: 'POST',
        body: formData,
    })
        .then(response => {
        // Handle the response from the server
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        //  Do something on success
        location.reload()
        })
        .catch(error => {
        // Handle any errors
        console.error('Error:', error);
        });
    });

    document.querySelectorAll('button[data-action="delete"]').forEach(button => {
        button.addEventListener('click', (event) => {
            event.preventDefault(); // Prevent form submission
            deleteJob(button.getAttribute('data-job-id'));
        });
    });

    document.querySelectorAll('button[data-action="edit"]').forEach(button => {
        button.addEventListener('click', (event) => {
            event.preventDefault(); // Prevent form submission
            editJob(button.getAttribute('data-job-id'));
        });
    });
});

