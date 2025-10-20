from flask import Flask, render_template_string, request, jsonify
import requests
import datetime
import json

app = Flask(__name__)
BASE_URL = "http://localhost:8000"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🌍 VoyageAI - Smart Travel Planner</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Poppins', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #1a1a1a;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }

        header {
            text-align: center;
            padding: 60px 20px 40px;
            color: white;
        }

        header h1 {
            font-size: 3.5rem;
            font-weight: 700;
            margin-bottom: 15px;
            text-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }

        header p {
            font-size: 1.3rem;
            font-weight: 300;
            opacity: 0.95;
        }

        .main-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 24px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            margin-bottom: 30px;
        }

        .section-title {
            font-size: 2rem;
            font-weight: 700;
            color: #667eea;
            margin-bottom: 10px;
        }

        .section-subtitle {
            font-size: 1.1rem;
            color: #666;
            margin-bottom: 30px;
        }

        .form-group {
            margin-bottom: 25px;
        }

        .form-input {
            width: 100%;
            padding: 16px 20px;
            font-size: 1rem;
            border: 2px solid #e0e7ff;
            border-radius: 12px;
            font-family: 'Poppins', sans-serif;
            transition: all 0.3s ease;
        }

        .form-input:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.1);
        }

        .submit-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 16px 40px;
            font-size: 1.1rem;
            font-weight: 600;
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }

        .submit-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 25px rgba(102, 126, 234, 0.5);
        }

        .submit-btn:active {
            transform: translateY(0);
        }

        .submit-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }

        .spinner {
            display: none;
            text-align: center;
            padding: 40px;
            color: #667eea;
            font-size: 1.2rem;
        }

        .spinner.active {
            display: block;
        }

        .spinner-icon {
            border: 4px solid #f3f4f6;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .results-section {
            display: none;
            margin-top: 40px;
        }

        .results-section.active {
            display: block;
        }

        .result-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 16px;
            margin-bottom: 30px;
            text-align: center;
        }

        .result-header h2 {
            font-size: 2rem;
            margin-bottom: 10px;
        }

        .result-timestamp {
            opacity: 0.9;
            font-size: 0.95rem;
        }

        .days-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 25px;
            margin-bottom: 30px;
        }

        .day-card {
            background: white;
            border-radius: 16px;
            padding: 25px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            border-left: 5px solid #667eea;
        }

        .day-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 30px rgba(102, 126, 234, 0.2);
        }

        .day-card-header {
            display: flex;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 15px;
            border-bottom: 2px solid #f3f4f6;
        }

        .day-number {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.3rem;
            font-weight: 700;
            margin-right: 15px;
            flex-shrink: 0;
        }

        .day-title {
            font-size: 1.4rem;
            font-weight: 600;
            color: #1a1a1a;
        }

        .day-content {
            color: #4b5563;
            line-height: 1.8;
            font-size: 0.95rem;
        }

        .day-content ul {
            margin-left: 20px;
            margin-top: 10px;
        }

        .day-content li {
            margin-bottom: 8px;
        }

        .day-content p {
            margin-bottom: 10px;
        }

        .content-box {
            background: white;
            border-radius: 16px;
            padding: 25px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            line-height: 1.8;
            color: #4b5563;
        }

        .content-box p {
            margin-bottom: 10px;
        }

        .footer {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 16px;
            padding: 30px;
            text-align: center;
            margin-top: 40px;
        }

        .footer-content {
            color: #666;
            font-size: 0.95rem;
            line-height: 1.8;
        }

        .developer-info {
            margin-top: 20px;
            padding-top: 20px;
            border-top: 2px solid #f3f4f6;
        }

        .developer-info h3 {
            color: #667eea;
            font-size: 1.2rem;
            margin-bottom: 10px;
        }

        .contact-info {
            display: flex;
            justify-content: center;
            gap: 30px;
            flex-wrap: wrap;
            margin-top: 15px;
        }

        .contact-item {
            color: #4b5563;
            font-weight: 500;
        }

        .email-btn {
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 30px;
            border-radius: 10px;
            text-decoration: none;
            margin-top: 15px;
            font-weight: 600;
            transition: all 0.3s ease;
        }

        .email-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }

        .error-message {
            background: #fee2e2;
            color: #dc2626;
            padding: 20px;
            border-radius: 12px;
            margin-top: 20px;
            border-left: 4px solid #dc2626;
        }

        .debug-info {
            background: #f3f4f6;
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
            font-family: monospace;
            font-size: 0.85rem;
            max-height: 200px;
            overflow-y: auto;
        }

        @media (max-width: 768px) {
            header h1 {
                font-size: 2.5rem;
            }

            .days-grid {
                grid-template-columns: 1fr;
            }

            .main-card {
                padding: 25px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🌍 VoyageAI</h1>
            <p>Your smart travel assistant — plan smarter, travel happier.</p>
        </header>

        <div class="main-card">
            <h2 class="section-title">✨ Plan Your Perfect Trip</h2>
            <p class="section-subtitle">Describe your dream vacation, and VoyageAI will craft a personalized plan for you in seconds.</p>

            <form id="travelForm">
                <div class="form-group">
                    <input 
                        type="text" 
                        id="userInput" 
                        class="form-input" 
                        placeholder="e.g. Plan a 5-day trip to Switzerland with scenic train rides and lakeside hotels"
                        required
                    >
                </div>
                <button type="submit" class="submit-btn" id="submitBtn">Generate Plan ✈️</button>
            </form>

            <div class="spinner" id="loadingSpinner">
                <div class="spinner-icon"></div>
                <div>🤔 VoyageAI is crafting your travel plan...</div>
            </div>

            <div class="results-section" id="resultsSection">
                <div class="result-header">
                    <h2>📋 Your Personalized Travel Plan</h2>
                    <div class="result-timestamp" id="timestamp"></div>
                </div>
                <div id="planContent"></div>
            </div>
        </div>

        <div class="footer">
            <div class="footer-content">
                <em>This plan was generated by VoyageAI. Please verify travel details, timings, and costs before booking.</em>
            </div>
            <div class="developer-info">
                <h3>👨‍💻 Developer Information</h3>
                <div class="contact-info">
                    <div class="contact-item">Ansh Kedia</div>
                    <div class="contact-item">📞 +91-8758838722</div>
                </div>
                <a href="mailto:anshkedia.04@gmail.com" class="email-btn">📧 Contact via Email</a>
            </div>
        </div>
    </div>

    <script>
        const form = document.getElementById('travelForm');
        const spinner = document.getElementById('loadingSpinner');
        const resultsSection = document.getElementById('resultsSection');
        const planContent = document.getElementById('planContent');
        const timestamp = document.getElementById('timestamp');
        const submitBtn = document.getElementById('submitBtn');

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const userInput = document.getElementById('userInput').value.trim();
            if (!userInput) return;

            // Show loading
            spinner.classList.add('active');
            resultsSection.classList.remove('active');
            submitBtn.disabled = true;

            try {
                console.log('Sending request with:', userInput);
                
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ question: userInput })
                });

                console.log('Response status:', response.status);
                console.log('Response headers:', response.headers);
                
                const data = await response.json();
                console.log('Response data:', data);
                console.log('Answer type:', typeof data.answer);
                console.log('Answer value:', data.answer);

                if (response.ok) {
                    if (data.answer && data.answer.trim()) {
                        // Update timestamp
                        const now = new Date();
                        timestamp.textContent = `Generated: ${now.toLocaleDateString()} at ${now.toLocaleTimeString()}`;

                        // Parse and display content
                        displayPlan(data.answer);
                        resultsSection.classList.add('active');
                    } else {
                        planContent.innerHTML = `
                            <div class="error-message">
                                ❌ Received empty response from backend.
                                <div class="debug-info">
                                    Response: ${JSON.stringify(data, null, 2)}
                                </div>
                            </div>
                        `;
                        resultsSection.classList.add('active');
                    }
                } else {
                    planContent.innerHTML = `
                        <div class="error-message">
                            ❌ ${data.error || 'Failed to generate plan. Please try again.'}
                            <div class="debug-info">
                                Status: ${response.status}<br>
                                Response: ${JSON.stringify(data, null, 2)}
                            </div>
                        </div>
                    `;
                    resultsSection.classList.add('active');
                }
            } catch (error) {
                console.error('Error:', error);
                planContent.innerHTML = `
                    <div class="error-message">
                        ⚠️ Connection Error: ${error.message}
                        <div class="debug-info">
                            Please ensure:<br>
                            1. FastAPI backend is running on port 8000<br>
                            2. CORS is properly configured<br>
                            3. Check browser console for details
                        </div>
                    </div>
                `;
                resultsSection.classList.add('active');
            } finally {
                spinner.classList.remove('active');
                submitBtn.disabled = false;
            }
        });

        function displayPlan(content) {
            console.log('Displaying plan with content length:', content.length);
            console.log('First 200 chars:', content.substring(0, 200));
            
            if (!content || content.trim() === '') {
                planContent.innerHTML = '<div class="error-message">❌ No content to display</div>';
                return;
            }

            // Parse content to extract day-by-day plans
            const lines = content.split('\n');
            const days = [];
            let otherContent = '';
            let currentDay = null;
            let dayContent = '';

            const dayPattern = /^(Day\s+\d+|DAY\s+\d+|day\s+\d+)/i;

            for (let line of lines) {
                const trimmedLine = line.trim();
                
                if (dayPattern.test(trimmedLine)) {
                    // Save previous day if exists
                    if (currentDay) {
                        days.push({ title: currentDay, content: dayContent.trim() });
                        dayContent = '';
                    }
                    currentDay = trimmedLine;
                } else if (currentDay) {
                    // We're in a day section
                    dayContent += line + '\n';
                } else if (trimmedLine) {
                    // Content before any days
                    otherContent += line + '\n';
                }
            }

            // Save last day
            if (currentDay) {
                days.push({ title: currentDay, content: dayContent.trim() });
            }

            console.log('Found days:', days.length);
            console.log('Other content length:', otherContent.length);

            // Display other content first
            if (otherContent.trim()) {
                planContent.innerHTML = `<div class="content-box">${formatContent(otherContent)}</div>`;
            } else {
                planContent.innerHTML = '';
            }

            // Create day cards
            if (days.length > 0) {
                let daysHtml = '<div class="days-grid">';
                days.forEach(day => {
                    daysHtml += createDayCard(day.title, day.content);
                });
                daysHtml += '</div>';
                planContent.innerHTML += daysHtml;
            } else if (!otherContent.trim()) {
                // If no days detected and no other content, display all as formatted content
                planContent.innerHTML = `<div class="content-box">${formatContent(content)}</div>`;
            }
        }

        function createDayCard(dayTitle, content) {
            const dayNumber = dayTitle.match(/\d+/)?.[0] || '?';
            return `
                <div class="day-card">
                    <div class="day-card-header">
                        <div class="day-number">${dayNumber}</div>
                        <div class="day-title">${escapeHtml(dayTitle)}</div>
                    </div>
                    <div class="day-content">
                        ${formatContent(content)}
                    </div>
                </div>
            `;
        }

        function formatContent(text) {
            if (!text) return '<p>No content available.</p>';
            
            // Escape HTML first
            text = text.replace(/</g, '&lt;').replace(/>/g, '&gt;');
            
            // Convert markdown-style formatting to HTML
            text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
            text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');
            
            // Convert bullet points
            const lines = text.split('\n');
            let formatted = '';
            let inList = false;

            for (let line of lines) {
                line = line.trim();
                if (line.startsWith('- ') || line.startsWith('• ') || line.startsWith('* ')) {
                    if (!inList) {
                        formatted += '<ul>';
                        inList = true;
                    }
                    formatted += `<li>${line.substring(2)}</li>`;
                } else {
                    if (inList) {
                        formatted += '</ul>';
                        inList = false;
                    }
                    if (line) {
                        formatted += `<p>${line}</p>`;
                    }
                }
            }

            if (inList) {
                formatted += '</ul>';
            }

            return formatted || '<p>No content available.</p>';
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/generate', methods=['POST'])
def generate_plan():
    try:
        data = request.get_json()
        print("="*50)
        print(f"Flask received request: {data}")
        
        user_question = data.get('question', '')
        
        if not user_question:
            print("ERROR: No question provided")
            return jsonify({'error': 'No question provided'}), 400
        
        # Call FastAPI backend
        payload = {"question": user_question}
        print(f"Calling FastAPI backend at {BASE_URL}/query")
        print(f"Payload: {payload}")
        
        response = requests.post(
            f"{BASE_URL}/query", 
            json=payload, 
            timeout=120,  # Increased timeout for agent processing
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"FastAPI response status: {response.status_code}")
        print(f"FastAPI response headers: {dict(response.headers)}")
        
        # Log raw response
        response_text = response.text
        print(f"FastAPI raw response (first 500 chars): {response_text[:500]}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"Parsed JSON response: {json.dumps(result, indent=2)[:500]}")
                
                answer = result.get("answer", "")
                print(f"Answer type: {type(answer)}")
                print(f"Answer length: {len(answer) if answer else 0}")
                print(f"Answer preview (first 200 chars): {answer[:200] if answer else 'EMPTY'}")
                
                if not answer or answer.strip() == "":
                    print("WARNING: Empty answer received from backend")
                    return jsonify({
                        'error': 'Backend returned empty response',
                        'debug': {
                            'received_data': result,
                            'answer_value': answer
                        }
                    }), 500
                
                print(f"Sending answer back to frontend (length: {len(answer)})")
                return jsonify({'answer': answer})
                
            except json.JSONDecodeError as e:
                print(f"ERROR: Failed to parse JSON: {e}")
                print(f"Raw response: {response_text}")
                return jsonify({
                    'error': f'Invalid JSON response from backend: {str(e)}',
                    'raw_response': response_text[:500]
                }), 500
        else:
            error_msg = f'Backend returned status {response.status_code}: {response_text}'
            print(f"ERROR: {error_msg}")
            return jsonify({'error': error_msg}), response.status_code
            
    except requests.exceptions.ConnectionError as e:
        error_msg = f'Cannot connect to backend server at {BASE_URL}. Make sure FastAPI is running.'
        print(f"CONNECTION ERROR: {error_msg}")
        print(f"Exception: {str(e)}")
        return jsonify({'error': error_msg}), 503
    except requests.exceptions.Timeout as e:
        error_msg = 'Request to backend timed out after 120 seconds.'
        print(f"TIMEOUT ERROR: {error_msg}")
        print(f"Exception: {str(e)}")
        return jsonify({'error': error_msg}), 504
    except Exception as e:
        error_msg = f'Unexpected error: {str(e)}'
        print(f"UNEXPECTED ERROR: {error_msg}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': error_msg}), 500
    finally:
        print("="*50)

if __name__ == '__main__':
    print("="*60)
    print("Starting Flask app on http://localhost:5000")
    print("Make sure FastAPI backend is running on http://localhost:8000")
    print("="*60)
    app.run(debug=True, port=5000, use_reloader=False)