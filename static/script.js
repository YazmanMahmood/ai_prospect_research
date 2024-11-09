document.getElementById('scrape-form').addEventListener('submit', async function (event) {
    event.preventDefault();
    const url = document.getElementById('website-url').value;
    const results = document.getElementById('results');
    results.style.display = 'none';

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

        if (mainResponse.ok) {
            // Populate the article text
            document.getElementById('article-text').innerText = mainData.summary || 'No article available.';

            // Populate contact info
            document.getElementById('contact-info').innerText = mainData.contact_info
                ? JSON.stringify(mainData.contact_info, null, 2)
                : 'No contact information available.';

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
                competitorInfo.innerText = competitorData.competitor_analysis;
            } else {
                console.log("No competitor analysis available");
                competitorInfo.innerText = 'No competitor analysis available.';
            }

            results.style.display = 'block';
        } else {
            console.error("Error response from server:", mainData.error || 'Unknown error');
            alert(mainData.error || 'An error occurred while generating insights. Please try again.');
        }
    } catch (error) {
        console.error("Network or processing error:", error);
        alert('A network error occurred. Please check your input and try again.');
    }
});
