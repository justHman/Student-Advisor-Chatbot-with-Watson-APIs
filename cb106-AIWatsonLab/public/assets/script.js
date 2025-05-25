async function uploadAudio() {
    const audioInput = document.getElementById('audioInput').files[0];
    const transcriptP = document.getElementById('transcript');
    if (!audioInput) {
        transcriptP.textContent = 'Please select an audio file.';
        return;
    }
    const formData = new FormData();
    formData.append('audio', audioInput);

    transcriptP.textContent = 'Uploading and transcribing...';
    try {
        const response = await fetch('/api/stt', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();
        if (response.ok) {
            transcriptP.textContent = result.transcript || 'No transcript returned.';
        } else {
            transcriptP.textContent = 'Error: ' + (result.error || 'Unknown error');
        }
    } catch (error) {
        transcriptP.textContent = 'Error: ' + error.message;
    }
}

async function sendMessage() {
    const text = document.getElementById('chatInput').value;
    const chatResponseP = document.getElementById('chatResponse');
    if (!text.trim()) {
        chatResponseP.textContent = 'Please enter a message.';
        return;
    }
    chatResponseP.textContent = 'Sending...';
    try {
        const response = await fetch('/api/message', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        });
        const result = await response.json();
        if (response.ok) {
            const responseText = result[0]?.text || (Array.isArray(result) && result.length > 0 && result[0].message) || result.error || 'No response text.';
            chatResponseP.textContent = responseText;
        } else {
             chatResponseP.textContent = 'Error: ' + (result.error || 'Unknown error from Assistant');
        }
    } catch (error) {
        chatResponseP.textContent = 'Error: ' + error.message;
    }
}

async function synthesizeSpeech() {
    const text = document.getElementById('ttsInput').value;
    const audioOutput = document.getElementById('audioOutput');
    const chatResponseP = document.getElementById('chatResponse'); // Use chatResponse for errors

    if (!text.trim()) {
        chatResponseP.textContent = 'Please enter text to synthesize.';
        return;
    }
    chatResponseP.textContent = 'Synthesizing...';
    try {
        const response = await fetch('/api/tts', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        });
        if (response.ok) {
            const blob = await response.blob();
            const url = URL.createObjectURL(blob);
            audioOutput.src = url;
            audioOutput.play();
            chatResponseP.textContent = 'Audio generated.';
        } else {
            const result = await response.json();
            chatResponseP.textContent = 'Error: ' + (result.error || 'Failed to synthesize speech');
        }
    } catch (error) {
        chatResponseP.textContent = 'Error: ' + error.message;
    }
}

async function getCourses() {
    const courseId = document.getElementById('courseInput').value;
    const courseListUl = document.getElementById('courseList');
    courseListUl.innerHTML = '<li>Loading courses...</li>';
    try {
        const response = await fetch(`/courses?id=${encodeURIComponent(courseId)}`);
        const result = await response.json();
        courseListUl.innerHTML = ''; // Clear loading/previous
        if (response.ok && result.courses) {
            if (result.courses.length > 0) {
                result.courses.forEach(course => {
                    const li = document.createElement('li');
                    li.textContent = `${course.name}: ${course.description}`;
                    courseListUl.appendChild(li);
                });
            } else {
                courseListUl.innerHTML = '<li>No courses found.</li>';
            }
        } else {
            courseListUl.innerHTML = '<li>Error: ' + (result.error || 'Failed to fetch courses') + '</li>';
        }
    } catch (error) {
        courseListUl.innerHTML = '<li>Error: ' + error.message + '</li>';
    }
}