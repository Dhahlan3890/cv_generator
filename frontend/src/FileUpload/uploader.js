import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';


const Uploader = () => {
    const [friendCV, setFriendCV] = useState('');
    const [userCV, setUserCV] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [texContents, setTexContents] = useState([]);
    const [selectedSample, setSelectedSample] = useState(null);
  
    // List of LaTeX file paths
    const filePaths = ['/latex/sample1.tex', '/latex/sample2.tex', '/latex/sample3.tex', '/latex/sample4.tex', '/latex/sample5.tex']; 

    useEffect(() => {
        // Fetch all .tex files
        const fetchTexFiles = async () => {
        try {
            const fetchPromises = filePaths.map(path =>
            fetch(path).then(response => response.text())
            );
            const filesData = await Promise.all(fetchPromises);
            setTexContents(filesData);
        } catch (err) {
            console.error('Error loading the .tex files:', err);
        }
        };

        fetchTexFiles();
    }, []);
  
    const handleSubmit = async (e) => {
      e.preventDefault();
      setLoading(true);
      setError(null);
  
      const formData = new FormData();
      formData.append('friend_cv', friendCV);
      formData.append('user_cv', userCV);
  
      try {
        const response = await axios.post('http://localhost:8000/api/generate-cv', formData, {
          responseType: 'blob',
        });
  
        // Create a URL for the blob
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'generated_cv.pdf');
        document.body.appendChild(link);
        link.click();
      } catch (err) {
        if (err.response && err.response.status === 422) {
          setError('Invalid data submitted. Please check your inputs and try again.');
        } else {
          setError('An error occurred while generating the CV. Please try again later.');
        }
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
  
    return (
      <div className="uploader">
        <h1>CV Generator</h1>
        <form onSubmit={handleSubmit}>
            <div style={{display:"flex", justifyContent:"space-around", marginBottom:"50px"}}>
                {texContents.map((content, index) => (
                    <div key={index} style={{position:"relative"}}>
                        <button 
                            onClick={() => {
                                setFriendCV(content);
                                setSelectedSample(index);
                                console.log(`Sample ${index + 1} selected`);
                            }}
                            disabled={selectedSample !== null && selectedSample !== index}
                        >
                          <img src={`/sample_images/sample${index + 1}.jpeg`} style={{width:"200px"}}/>
                          
                        </button>
                        {selectedSample === index && <svg style={{width:"20px", position:"absolute"}} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="size-1">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
                        </svg>
                        }
                    </div>
                ))}
            </div>
          <div>
            <label htmlFor="userCV">Your CV (PDF):</label>
            <input
              type="file"
              id="userCV"
              onChange={(e) => setUserCV(e.target.files[0])}
              accept=".pdf"
              required
            />
          </div>
          <button type="submit" disabled={loading}>
            {loading ? 'Generating...' : 'Generate CV'}
          </button>
        </form>
        {error && <p className="error">{error}</p>}

        <Link to="/visualizer">
            <button>Visualize</button>
        </Link>
      </div>
    );
  }

  export default Uploader;