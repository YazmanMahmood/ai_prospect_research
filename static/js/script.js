function showTimeoutMessage() {
    const timeoutMessage = document.getElementById('timeout-message');
    if (timeoutMessage) {
        timeoutMessage.style.display = 'block';
    }
}

document.getElementById('scrape-form').addEventListener('submit', async function (event) {
    event.preventDefault();
    const url = document.getElementById('website-url').value;
    const results = document.getElementById('results');
    const loader = document.getElementById('loader');
    const timeoutMessage = document.getElementById('timeout-message');
    
    // Hide results and show loader
    results.style.display = 'none';
    loader.style.display = 'block';
    timeoutMessage.style.display = 'none';  // Reset timeout message
    
    // Set timeout to show message after 15 seconds
    const timeoutId = setTimeout(() => {
        showTimeoutMessage();
    }, 15000);

    updateLoadingSteps();

    try {
        console.log("Sending request to /scrape endpoint with URL:", url);
        
        // First, get the main analysis
        const mainResponse = await fetch('/scrape', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url })
        });

        console.log("Response received from /scrape endpoint.");
        const mainData = await mainResponse.json();
        console.log("Main data received:", mainData);

        // Then, get the competitor analysis
        console.log("Sending request to /analyze_competitors endpoint");
        const competitorResponse = await fetch('/analyze_competitors', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url })
        });

        const competitorData = await competitorResponse.json();
        console.log("Competitor data received:", competitorData);

        // Clear timeout if request completes
        clearTimeout(timeoutId);
        
        if (mainResponse.ok) {
            // Format and display the article text
            const articleText = mainData.summary || 'No article available.';
            const formattedArticle = articleText
                .split('\n')
                .map(line => {
                    line = line.trim();
                    // Remove asterisks from the line
                    line = line.replace(/\*/g, '');
                    
                    // Check for main headers (all caps)
                    if (line.match(/^[A-Z][A-Z\s]+$/)) {
                        return `<div class="article-main-header">${line}</div>`;
                    }
                    // Check for secondary headers (Title Case followed by colon)
                    else if (line.match(/^[A-Z][a-zA-Z\s]+:$/)) {
                        return `<div class="article-sub-header">${line}</div>`;
                    }
                    // Check for bullet points
                    else if (line.startsWith('•') || line.startsWith('-')) {
                        return `<div class="article-bullet">${line.substring(1).trim()}</div>`;
                    }
                    // Regular paragraph
                    else if (line) {
                        return `<p class="article-paragraph">${line}</p>`;
                    }
                    return '';
                })
                .filter(line => line)
                .join('');

            document.getElementById('article-text').innerHTML = formattedArticle;

            // Format and display contact info
            const contactInfo = document.getElementById('contact-info');
            if (mainData.contact_info && (mainData.contact_info.emails.length > 0 || mainData.contact_info.phones.length > 0)) {
                const contactHtml = `
                    <div class="contact-section">
                        ${mainData.contact_info.emails.length > 0 ? `
                            <div class="contact-group">
                                <div class="contact-label">
                                    <i class="fas fa-envelope"></i>
                                    <span>Email Addresses</span>
                                </div>
                                <ul class="contact-list">
                                    ${mainData.contact_info.emails.map(email => `
                                        <li>
                                            <a href="mailto:${email}" target="_blank">
                                                ${email}
                                            </a>
                                        </li>
                                    `).join('')}
                                </ul>
                            </div>
                        ` : ''}
                        
                        ${mainData.contact_info.phones.length > 0 ? `
                            <div class="contact-group">
                                <div class="contact-label">
                                    <i class="fas fa-phone"></i>
                                    <span>Phone Numbers</span>
                                </div>
                                <ul class="contact-list">
                                    ${mainData.contact_info.phones.map(phone => `
                                        <li>
                                            <a href="tel:${phone.replace(/[^\d+]/g, '')}">
                                                ${phone}
                                            </a>
                                        </li>
                                    `).join('')}
                                </ul>
                            </div>
                        ` : ''}
                    </div>
                `;
                contactInfo.innerHTML = contactHtml;
            } else {
                contactInfo.innerHTML = '<p class="no-data">No contact information available.</p>';
            }

            // Populate social links
            const socialLinks = document.getElementById('social-links');
            socialLinks.innerHTML = '';
            if (mainData.social_links && Object.keys(mainData.social_links).length > 0) {
                for (const [platform, link] of Object.entries(mainData.social_links)) {
                    const li = document.createElement('li');
                    li.innerHTML = `<a href="${link}" target="_blank">${platform}</a>`;
                    socialLinks.appendChild(li);
                }
            } else {
                socialLinks.innerHTML = '<li>No social links available.</li>';
            }

            // Populate keywords
            const keywords = document.getElementById('keywords');
            keywords.innerHTML = '';
            if (mainData.keywords && mainData.keywords.length > 0) {
                mainData.keywords.forEach(keyword => {
                    const li = document.createElement('li');
                    li.textContent = `${keyword.keyword}: ${keyword.count}`;
                    keywords.appendChild(li);
                });
            } else {
                keywords.innerHTML = '<li>No keywords available.</li>';
            }

            // Populate industry category
            document.getElementById('industry-category').innerText = 
                mainData.industry_category || 'No industry category available.';

            // Populate key personnel
            const keyPersonnel = document.getElementById('key-personnel');
            keyPersonnel.innerHTML = '';
            if (mainData.key_personnel && mainData.key_personnel.length > 0) {
                mainData.key_personnel.forEach(person => {
                    const li = document.createElement('li');
                    li.textContent = person;
                    keyPersonnel.appendChild(li);
                });
            } else {
                keyPersonnel.innerHTML = '<li>No key personnel information available.</li>';
            }

            // Populate competitor analysis
            const competitorInfo = document.getElementById('competitor-info');
            if (competitorData.status === 'success' && competitorData.competitor_analysis) {
                console.log("Displaying competitor analysis");
                const formattedCompetitors = competitorData.competitor_analysis
                    .split('\n')
                    .map(line => {
                        line = line.trim();
                        if (line === 'TOP COMPETITORS:') {
                            return `<div class="competitor-header">${line}</div>`;
                        } else if (line.match(/^\d\./)) {
                            return `<div class="competitor-item">${line}</div>`;
                        }
                        return line;
                    })
                    .filter(line => line) // Remove empty lines
                    .join('');
                
                competitorInfo.innerHTML = formattedCompetitors;
            } else {
                console.log("No competitor analysis available");
                competitorInfo.innerHTML = '<p class="no-data">No competitor analysis available.</p>';
            }

            // Populate traffic data
            const trafficData = document.getElementById('traffic-data');
            if (mainData.traffic_data) {
                console.log("Displaying traffic data");
                trafficData.innerText = mainData.traffic_data;
            } else {
                console.log("No traffic data available");
                trafficData.innerText = 'No traffic data available.';
            }

            // Hide loader and show results
            loader.style.display = 'none';
            results.style.display = 'block';
        } else {
            console.error("Error response from server:", mainData.error || 'Unknown error');
            alert(mainData.error || 'An error occurred while generating insights. Please try again.');
        }
    } catch (error) {
        // Clear timeout on error
        clearTimeout(timeoutId);
        console.error("Network or processing error:", error);
        loader.style.display = 'none';
        
        // Show error message in results container
        results.style.display = 'block';
        document.getElementById('article-text').innerHTML = `
            <div class="error-message">
                <i class="fas fa-exclamation-circle"></i>
                <p>Sorry, we encountered an error while analyzing this website.</p>
                <p class="error-details">Error: ${error.message || 'Unknown error occurred'}</p>
                <button onclick="location.reload()" class="retry-button">
                    <i class="fas fa-redo"></i> Try Again
                </button>
            </div>
        `;
    }
});

function updateLoadingSteps() {
    const steps = document.querySelectorAll('.progress-steps .step');
    const loadingText = document.querySelector('.loading-text .text');
    const texts = ['Scraping Website', 'Analyzing Content', 'Generating Insights'];
    let currentStep = 0;

    function nextStep() {
        if (currentStep < steps.length) {
            // Update steps
            steps.forEach((step, index) => {
                if (index < currentStep) {
                    step.classList.add('completed');
                    step.classList.remove('active');
                } else if (index === currentStep) {
                    step.classList.add('active');
                    step.classList.remove('completed');
                } else {
                    step.classList.remove('completed', 'active');
                }
            });

            // Update loading text
            loadingText.textContent = texts[currentStep];

            currentStep++;
            if (currentStep < steps.length) {
                setTimeout(nextStep, 2000);
            }
        }
    }

    nextStep();
}
