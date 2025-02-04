import React, { useEffect, useState } from "react";
import axios from "axios";
import { Bar, Pie } from "react-chartjs-2";
import "chart.js/auto";
import moment from "moment";
import "./App.css";
import { useSearchParams } from "react-router-dom";

function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchParams] = useSearchParams();
  const userId = searchParams.get("user_id");
  

  // Function to handle login redirect
  const handleLogin = () => {
    axios.get("http://localhost:8888/")
      .then((response) => {
        window.location.href = response.data.auth_url;
      })
      .catch((error) => {
        console.error("Login error:", error);
        setError("Failed to fetch login URL.");
      });
  };

  useEffect(() => {
    setLoading(true);
    axios.get(`http://localhost:8888/dashboard?user_id=${userId}`, { withCredentials: true })
      .then((response) => {
        console.log(response.data);
        setData(response.data);
      })
      .catch((error) => {
        console.error("Error fetching data:", error);
        setError("Failed to fetch Spotify data.");
      })
      .finally(() => setLoading(false));
  }, [userId]);

  if (!userId) {
    return (
      <div className="container">
        <h1 className="title">Spotify Listening Insights</h1>
        <button className="login-button" onClick={handleLogin}>Login with Spotify</button>
      </div>
    );
  }

  if (loading) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  if (!data) {
    return <div>No data available</div>;
  }

  // Ensure data exists before mapping
  const genreLabels = data.top_genres ? data.top_genres.map((item) => item[0]) : [];
  const genreValues = data.top_genres ? data.top_genres.map((item) => item[1]) : [];

  const genreChartData = {
    labels: genreLabels,
    datasets: [
      {
        label: "Genres",
        data: genreValues,
        backgroundColor: ["#ff6384", "#36a2eb", "#ffce56", "#4bc0c0", "#9966ff"],
      },
    ],
  };

  const peakHourData = {
    labels: ["Peak Listening Hour"],
    datasets: [
      {
        label: "Hour",
        data: [data.peak_listening_hour || 0], // Ensure value exists
        backgroundColor: ["#36a2eb"],
      },
    ],
  };


  return (
    <div className="container">
      <h1 className="title">Spotify Listening Insights</h1>
      
      <button className="login-button" onClick={handleLogin}>Login with Spotify</button>

      <div className="grid">
        {data.top_genres && data.top_genres.length > 0 && (
          <div className="card">
            <h2>Top Genres</h2>
            <Pie data={genreChartData} />
          </div>
        )}

        {data.peak_listening_hour !== null && (
          <div className="card">
            <h2>Peak Listening Hour</h2>
            <Bar data={peakHourData} />
          </div>
        )}
      </div>

      <div className="card">
        <h2>Recent Tracks</h2>
        {data.recent_tracks && data.recent_tracks.length > 0 ? (
          <ul className="track-list">
            {data.recent_tracks.map((track, index) => (
              <li key={index}>
                <strong>{track.track}</strong> - {track.artist} 
                <span className="time">{moment(track.played_at).format("hh:mm A")}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p>No recent tracks available</p>
        )}
      </div>
    </div>
  );
}

export default App;



