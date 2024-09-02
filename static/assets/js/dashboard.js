document.querySelectorAll('.sidebar a').forEach(item => {
    item.addEventListener('click', function() {
        document.querySelector('.sidebar a.active').classList.remove('active');
        this.classList.add('active');
        document.querySelectorAll('main > div').forEach(section => section.classList.add('hidden'));
        if (this.id === 'overview') {
            document.getElementById('overview-section').classList.remove('hidden');
        } else if (this.id === 'uploads') {
            document.getElementById('uploads-section').classList.remove('hidden');
        } else if (this.id === 'openings') {
            document.getElementById('openings-section').classList.remove('hidden');
        }
        else if (this.id === 'applications') {
            document.getElementById('myapplications-section').classList.remove('hidden');
        }
        else if (this.id === 'submissions') {
            document.getElementById('autoapply-section').classList.remove('hidden');
        }
    });
});

document.querySelector('.upload-box').addEventListener('click', function() {
    document.getElementById('dropzone-file').click();
});

document.getElementById('dropzone-file').addEventListener('change', function(event) {
    const form = document.getElementById('upload-form');
    const formData = new FormData(form);
    document.getElementById('loading-indicator').classList.remove('hidden');
    document.getElementById('loading-indicator').style.display='flex';
    fetch('http://127.0.0.1:5000/upload', {
        method: 'POST',
        body: formData,
        mode: 'cors'
    }).then(response => {
        if (response.ok) {
            return response.json();
        }
        throw new Error('File upload failed');
    }).then(data => {
        console.log(data);
        document.getElementById('loading-indicator').classList.add('hidden');
        document.getElementById('loading-indicator').style.display='none';
        // Show success message
        const uploadBox = document.querySelector('.upload-box');
        uploadBox.innerHTML = `
            <div class="upload-content">
                <svg class="w-8 h-8 mb-4 text-green-500 dark:text-green-400" aria-hidden="true"
                    xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 20 16">
                    <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M13 13h3a3 3 0 0 0 0-6h-.025A5.56 5.56 0 0 0 16 6.5A5.5 5.5 0 0 0 5.207 5.021C5.137 5.017 5.071 5 5 5a4 4 0 0 0 0 8h2.167M10 15V6m0 0L8 8m2-2 2 2"/>
                </svg>
                <p class="mb-2 text-sm text-green-500 dark:text-green-400"><span class="font-semibold">File uploaded successfully!</span></p>
                <p class="text-xs text-green-500 dark:text-green-400">Your file has been uploaded.</p>
            </div>
        `;
        setTimeout(() => {
            window.location.reload();
        }, 2000);
    }).catch(error => {
        console.error(error);
        document.getElementById('loading-indicator').classList.add('hidden');
        document.getElementById('loading-indicator').style.display='none';
        const uploadBox = document.querySelector('.upload-box');
        uploadBox.innerHTML = `
            <div class="upload-content">
                <svg class="w-8 h-8 mb-4 text-red-500 dark:text-red-400" aria-hidden="true"
                    xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 20 16">
                    <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M13 13h3a3 3 0 0 0 0-6h-.025A5.56 5.56 0 0 0 16 6.5A5.5 5.5 0 0 0 5.207 5.021C5.137 5.017 5.071 5 5 5a4 4 0 0 0 0 8h2.167M10 15V6m0 0L8 8m2-2 2 2"/>
                </svg>
                <p class="mb-2 text-sm text-red-500 dark:text-red-400"><span class="font-semibold">File upload failed!</span></p>
                <p class="text-xs text-red-500 dark:text-red-400">Please try again.</p>
            </div>
        `;
    });
});

function populateList(elementId, items) {
    const listElement = document.getElementById(elementId);
    if (!listElement || !Array.isArray(items)) return;

    listElement.innerHTML = items.map(item => `<li>${item}</li>`).join('');
}

function populateUserData(user) {
    console.log(user);
    document.getElementById('name').textContent = `Name: ${user.name || 'N/A'}`;
    document.getElementById('email').textContent = `Email: ${user.email_id || 'N/A'}`;
    document.getElementById('github').innerHTML = `GitHub: ${user.github_portfolio}`;
    document.getElementById('linkedin').innerHTML = `LinkedIn: ${user.linkedin_id}`;

    const projects = user.projects || [];
    document.getElementById('projects').innerHTML = projects.map(project => `
        <li>
            <strong>Project ${project.project_number}:</strong> ${project.explanation}
        </li>
    `).join('');

    populateList('technical-skills', user.technical_skills);
    populateList('soft-skills', user.soft_skills);
    const education = user.education || [];
    document.getElementById('education').innerHTML = education.map(ed => `
        <li>
            <strong>${ed.degree || 'N/A'}</strong> from ${ed.institution || 'N/A'} (GPA: ${ed.gpa || '-'})
        </li>
    `).join('');
}
const jobsPerPage = 10;
let currentJobIndex = 0;
// Replace this with your actual job data

function populateJobTable(jobs, startIndex, endIndex) {
    const jobTableBody = document.getElementById('job-table').querySelector('tbody');
    for (let i = startIndex; i < endIndex && i < jobs.length; i++) {
        const job = jobs[i];
        const row = document.createElement('tr');

        const titleCell = document.createElement('td');
        titleCell.textContent = job.title || 'N/A';
        row.appendChild(titleCell);

        const companyCell = document.createElement('td');
        companyCell.textContent = job.company || 'N/A';
        row.appendChild(companyCell);

        const locationCell = document.createElement('td');
        locationCell.textContent = job.location || 'N/A';
        row.appendChild(locationCell);

        const applyCell = document.createElement('td');
        const applyButton = document.createElement('button');
        applyButton.textContent = 'Apply';
        // Add CSS classes to the button
        applyButton.classList.add('font-medium', 'text-blue-600', 'dark:text-blue-500', 'hover:underline');
        applyButton.onclick = () => {
            window.location.href = job.job_url;
        };
        applyCell.appendChild(applyButton);
        row.appendChild(applyCell);

        jobTableBody.appendChild(row);
    }
}

function populateAppliedTable(appliedJobs) {
    const appliedTableBody = document.getElementById('applied-table').querySelector('tbody');
    appliedTableBody.innerHTML = ''; // Clear existing rows

    appliedJobs.forEach(job => {
        const row = document.createElement('tr');

        const titleCell = document.createElement('td');
        titleCell.textContent = job.title || 'N/A';
        row.appendChild(titleCell);

        const companyCell = document.createElement('td');
        companyCell.textContent = job.role || 'N/A';
        row.appendChild(companyCell);

        const dateCell = document.createElement('td');
        dateCell.textContent = job.date || 'N/A'; // Ensure date is properly formatted
        row.appendChild(dateCell);

        const linkCell = document.createElement('td');
        const link = document.createElement('a');
        link.textContent = 'View Job';
        link.href = job.url;
        link.target = '_blank'; // Open link in new tab
        linkCell.appendChild(link);
        row.appendChild(linkCell);
        appliedTableBody.appendChild(row);
    });
}

document.getElementById('load-more-btn').addEventListener('click', () => {
    currentJobIndex += jobsPerPage;
    populateJobTable(jobData, currentJobIndex - jobsPerPage, currentJobIndex);
});


document.addEventListener('DOMContentLoaded', () => {
    // Replace 'user' with your actual user data
    populateUserData(user);
    populateJobTable(jobData, currentJobIndex, jobsPerPage);
    console.log(appliedData)
    populateAppliedTable(appliedData);
    document.getElementById('overview-section').classList.remove('hidden');
});
