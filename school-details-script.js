// Get the URL query parameters
const urlParams = new URLSearchParams(window.location.search);

fetch('json/schoolData.json')
    .then(response => response.json())
    .then(data => {
        const schoolId = urlParams.get('school'); // Replace with dynamic ID retrieval
        const school = data[schoolId];

        // Update page content
        document.getElementById('school-name').textContent = school.name;
        document.getElementById('school-image').src = school.image_url;
        document.getElementById('projects-in-progress').textContent = school.projects_in_progress;
        document.getElementById('projects-completed').textContent = school.projects_completed;

        // Render category breakdown chart using Chart.js
        // Render category breakdown chart using Chart.js
        const ctx = document.getElementById('category-chart').getContext('2d');
        new Chart(ctx, {
            type: 'pie', // or 'doughnut' for donut chart
            data: {
                labels: school.categories.map(c => c.category),
                datasets: [{
                    data: school.categories.map(c => c.count),
                    backgroundColor: ['#3498db', '#e74c3c']
                }]
            },
            options: {
                responsive: false, // Disable responsive to keep fixed size
                maintainAspectRatio: false // You can also disable this if the aspect ratio should not be preserved
            }
        });


        // Render project cards
        const projectCardsContainer = document.getElementById('project-cards');
        school.projects.forEach(project => {
            const projectCard = document.createElement('div');
            projectCard.className = 'project-card';
            projectCard.innerHTML = `
                <img src="${project.thumbnail}" alt="Project Thumbnail">
                <div>
                    <h3>${project.name}</h3>
                    <p>Category: ${project.category}</p>
                    <p>${project.goal}</p>
                </div>
            `;
            projectCard.onclick = () => loadProjectDetails(project);
            projectCardsContainer.appendChild(projectCard);
        });

        function loadProjectDetails(project) {
            document.getElementById('project-title').textContent = project.name;
            document.getElementById('project-objective').textContent = project.objective;
            document.getElementById('project-duration').textContent = project.duration;
            document.getElementById('project-recommended').textContent = project.recommended_for.join(', ');

            const stepsList = document.getElementById('project-steps');
            stepsList.innerHTML = '';
            project.steps.forEach(step => {
                const stepItem = document.createElement('li');
                stepItem.textContent = step;
                stepsList.appendChild(stepItem);
            });
        }

        // Load initial project details (first project)
        if (school.projects.length > 0) {
            loadProjectDetails(school.projects[0]);
        }
})
     .catch(error => console.error('Error fetching the school data:', error));