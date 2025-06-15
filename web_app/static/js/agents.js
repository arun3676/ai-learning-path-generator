// Agents interface JavaScript
const API_BASE_URL = '/agents'; // Updated to match the backend route

// Initialize agents
const agents = {
    research: {
        isActive: false,
        currentTask: null,
        progress: 0
    },
    teaching: {
        isActive: false,
        currentTask: null,
        progress: 0
    }
};

// Chat interface
const chatMessages = document.getElementById('chatMessages');
const chatInput = document.getElementById('chatInput');

// Progress indicators
const researchProgress = document.getElementById('researchProgress');
const teachingProgress = document.getElementById('teachingProgress');

// Status indicators
const researchStatus = document.getElementById('researchStatus');
const teachingStatus = document.getElementById('teachingStatus');

// Update progress
function updateProgress(agentType, progress) {
    const progressBar = agentType === 'research' ? researchProgress : teachingProgress;
    progressBar.style.width = `${progress}%`;
}

// Update status
function updateStatus(agentType, status) {
    const statusElement = agentType === 'research' ? researchStatus : teachingStatus;
    statusElement.textContent = status;
}

// Add message to chat
function addMessage(content, isUser = false) {
    const message = document.createElement('div');
    message.className = `message ${isUser ? 'user-message' : 'agent-message'}`;
    message.textContent = content;
    chatMessages.appendChild(message);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Send message to agents
async function sendMessage() {
    const message = chatInput.value.trim();
    if (!message) return;

    // Add user message to chat
    addMessage(message, true);
    chatInput.value = '';

    try {
        // Send to server
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message })
        });

        const data = await response.json();
        addMessage(data.response);
    } catch (error) {
        addMessage('Sorry, I encountered an error. Please try again.');
    }
}

// Start research
async function startResearch() {
    console.log('startResearch function called');
    const topic = prompt('What topic would you like to research?');
    if (!topic) {
        console.log('Research cancelled by user or no topic entered.');
        return;
    }
    console.log(`Topic selected: ${topic}`);

    try {
        console.log('Updating research status to Researching...');
        updateStatus('research', 'Researching...');
        updateProgress('research', 0);

        const apiUrl = `${API_BASE_URL}/research`;
        console.log(`Sending POST request to: ${apiUrl}`);
        const requestBody = JSON.stringify({ topic });
        console.log(`Request body: ${requestBody}`);

        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: requestBody
        });

        console.log(`Response status: ${response.status}`);
        const responseText = await response.text(); // Get raw text first
        console.log(`Raw response text: ${responseText}`);
        
        let data;
        try {
            data = JSON.parse(responseText); // Try to parse as JSON
        } catch (parseError) {
            console.error('Failed to parse response as JSON:', parseError);
            console.error('Response was not valid JSON. Check server logs for errors.');
            addMessage('Error: Received invalid data from server.');
            updateStatus('research', 'Error: Invalid server response');
            return;
        }

        console.log('Parsed response data:', data);

        if (response.ok && data.success) {
            updateStatus('research', 'Research complete!');
            updateProgress('research', 100);
            addMessage(`Research findings: ${JSON.stringify(data.findings || [], null, 2)}`);
            if (data.sources && data.sources.length > 0) {
                addMessage(`Sources: ${JSON.stringify(data.sources, null, 2)}`);
            }
            if (data.related_topics && data.related_topics.length > 0) {
                addMessage(`Related Topics: ${JSON.stringify(data.related_topics, null, 2)}`);
            }
        } else {
            console.error('Research request failed or server returned an error:', data.error || 'Unknown error');
            updateStatus('research', `Error: ${data.error || 'Failed'}`);
            addMessage(`Sorry, research failed: ${data.message || data.error || 'Please try again.'}`);
        }

    } catch (error) {
        console.error('Error during startResearch fetch operation:', error);
        updateStatus('research', 'Network Error or other issue');
        addMessage('Sorry, research failed due to a network error or other issue. Please check your connection and try again.');
    }
}

// Create learning path
async function createLearningPath() {
    const topic = prompt('What topic would you like to learn about?');
    if (!topic) return;

    const expertiseLevel = prompt('What is your expertise level? (beginner/intermediate/advanced)');
    if (!expertiseLevel) return;

    const learningStyle = prompt('What is your preferred learning style? (visual/auditory/kinesthetic)');
    if (!learningStyle) return;

    try {
        updateStatus('teaching', 'Creating learning path...');
        updateProgress('teaching', 0);

        const response = await fetch(`${API_BASE_URL}/create-path`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                topic,
                expertise_level: expertiseLevel,
                learning_style: learningStyle
            })
        });

        const data = await response.json();
        updateStatus('teaching', 'Learning path created!');
        updateProgress('teaching', 100);
        addMessage(`Learning path created: ${JSON.stringify(data.path, null, 2)}`);
    } catch (error) {
        updateStatus('teaching', 'Error occurred');
        addMessage('Sorry, failed to create learning path. Please try again.');
    }
}

// View research history
async function viewResearchHistory() {
    try {
        const response = await fetch(`${API_BASE_URL}/research/history`);
        const data = await response.json();
        addMessage(`Research history: ${JSON.stringify(data.history, null, 2)}`);
    } catch (error) {
        addMessage('Sorry, failed to load research history.');
    }
}

// View learning paths
async function viewPaths() {
    try {
        const response = await fetch(`${API_BASE_URL}/paths`);
        const data = await response.json();
        addMessage(`Learning paths: ${JSON.stringify(data.paths, null, 2)}`);
    } catch (error) {
        addMessage('Sorry, failed to load learning paths.');
    }
}

// Auto-scroll chat
chatMessages.scrollTop = chatMessages.scrollHeight;

// Initialize chat input
if (chatInput) {
    chatInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            sendMessage();
        }
    });
}

// Add event listeners when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM fully loaded and parsed');

    const startResearchButton = document.getElementById('startResearchBtn');
    if (startResearchButton) {
        console.log('Attaching click listener to startResearchBtn');
        startResearchButton.addEventListener('click', startResearch);
    } else {
        console.error('startResearchBtn not found');
    }

    const viewHistoryButton = document.getElementById('viewHistoryBtn');
    if (viewHistoryButton) {
        console.log('Attaching click listener to viewHistoryBtn');
        viewHistoryButton.addEventListener('click', viewResearchHistory);
    } else {
        console.error('viewHistoryBtn not found');
    }

    const createPathButton = document.getElementById('createPathBtn');
    if (createPathButton) {
        console.log('Attaching click listener to createPathBtn');
        createPathButton.addEventListener('click', createLearningPath);
    } else {
        console.error('createPathBtn not found');
    }

    const viewPathsButton = document.getElementById('viewPathsBtn');
    if (viewPathsButton) {
        console.log('Attaching click listener to viewPathsBtn');
        viewPathsButton.addEventListener('click', viewPaths);
    } else {
        console.error('viewPathsBtn not found');
    }

    const sendMessageButton = document.getElementById('sendMessageBtn');
    if (sendMessageButton) {
        console.log('Attaching click listener to sendMessageBtn');
        sendMessageButton.addEventListener('click', sendMessage);
    } else {
        console.error('sendMessageBtn not found');
    }
});
