import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Visualizer = () => {
    const [texContent, setTexContent] = useState("");
    const [pdfUrl, setPdfUrl] = useState("");

    const path = 'temp.tex';

    useEffect(() => {
        const fetchTexFiles = async () => {
            try {
                const response = await fetch(path);
                const data = await response.text();
                setTexContent(data);
            } catch (err) {
                console.error('Error loading the .tex file:', err);
            }
        };

        fetchTexFiles();
    }, []);

    const handleTexChange = (event) => {
        setTexContent(event.target.value);
    };

    const handleCompile = async () => {
        try {
            const formData = new FormData();
            formData.append('tex_code', texContent);

            const response = await axios.post('http://localhost:8000/api/tex-to-pdf-file', formData, {
                responseType: 'blob',
            });

            const url = window.URL.createObjectURL(new Blob([response.data]));
            setPdfUrl(url);
        } catch (error) {
            console.error('Error compiling LaTeX:', error);
        }
    };

    return (
        <div className="visualizer-container" style={{ display: 'flex', justifyContent: 'space-between' }}>
            <div className="code-section" style={{ width: '48%' }}>
                <h2>LaTeX Code</h2>
                <textarea
                    value={texContent}
                    onChange={handleTexChange}
                    style={{ width: '100%', height: '500px' }}
                />
                <button onClick={handleCompile}>Compile LaTeX</button>
            </div>
            <div className="pdf-section" style={{ width: '48%' }}>
                <h2>PDF Preview</h2>
                <iframe
                    src= "temp.pdf"
                    width="100%"
                    height="600px"
                    title="PDF Preview"
                    style={{ border: '1px solid #ccc' }}
                />
            </div>
        </div>
    );
};

export default Visualizer;
