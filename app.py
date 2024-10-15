from flask import Flask, request, jsonify, render_template_string
from base64 import b64decode, b64encode

app = Flask(__name__)

@app.route('/decode', methods=['POST'])
def decode():
    data = request.json
    encoding_type = data.get('encodingType')
    b64 = data.get('base64String')

    try:
        # Decode the Base64 string
        bytes_data = b64decode(b64, validate=True)

        if encoding_type == 'pdf':
            # Validate PDF signature
            if bytes_data[0:4] != b'%PDF':
                return jsonify({'error': 'Invalid PDF file'}), 400
            # Return the decoded PDF content as Base64
            return jsonify({
                'decodedContent': b64encode(bytes_data).decode('utf-8'),
                'error': None
            })
        elif encoding_type in ['html', 'xml']:
            # Validate HTML/XML by decoding to string
            decoded_text = bytes_data.decode('utf-8', errors='replace')
            return jsonify({
                'decodedContent': decoded_text,
                'error': None
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/')
def index():
    return render_template_string('''
    <html>
        <head>
            <style>
                #base64String {
                    width: 100%;
                }
            </style>
        </head>
        <body>
            <h1>Base64 Document Converter</h1>
            <form id="converterForm">
                <label for="encodingType">Encoding Type:</label>
                <select id="encodingType" name="encodingType">
                    <option value="pdf">PDF</option>
                    <option value="html">HTML</option>
                    <option value="xml">XML</option>
                </select><br><br>
                <textarea id="base64String" placeholder="Enter Base64 string" rows="10" cols="50"></textarea><br><br>
                <button type="submit">Convert</button>
            </form>
            <h2>Result:</h2>
            <iframe id="pdfViewer" style="display:none; width:100%; height:600px;"></iframe>
            <div id="htmlViewer" style="display:none;"></div>
            <div id="xmlViewer" style="display:none;"></div>
            <pre id="result"></pre>

            <script>
                document.getElementById('converterForm').addEventListener('submit', async (e) => {
                    e.preventDefault();
                    const encodingType = document.getElementById('encodingType').value;
                    const base64String = document.getElementById('base64String').value;

                    const response = await fetch('/decode', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ encodingType, base64String }),
                    });

                    const data = await response.json();
                    const resultElement = document.getElementById('result');
                    const pdfViewer = document.getElementById('pdfViewer');
                    const htmlViewer = document.getElementById('htmlViewer');
                    const xmlViewer = document.getElementById('xmlViewer');

                    if (response.ok) {
                        resultElement.textContent = '';
                        if (encodingType === 'pdf') {
                            const blob = new Blob([new Uint8Array(atob(data.decodedContent).split("").map(c => c.charCodeAt(0)))], { type: 'application/pdf' });
                            const url = URL.createObjectURL(blob);
                            pdfViewer.src = url;
                            pdfViewer.style.display = 'block';
                            htmlViewer.style.display = 'none';
                            xmlViewer.style.display = 'none';
                        } else if (encodingType === 'html') {
                            htmlViewer.innerHTML = data.decodedContent;
                            htmlViewer.style.display = 'block';
                            pdfViewer.style.display = 'none';
                            xmlViewer.style.display = 'none';
                        } else if (encodingType === 'xml') {
                            xmlViewer.textContent = data.decodedContent;
                            xmlViewer.style.display = 'block';
                            pdfViewer.style.display = 'none';
                            htmlViewer.style.display = 'none';
                        }
                    } else {
                        resultElement.textContent = data.error;
                        pdfViewer.style.display = 'none';
                        htmlViewer.style.display = 'none';
                        xmlViewer.style.display = 'none';
                    }
                });
            </script>
        </body>
    </html>
    ''')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
