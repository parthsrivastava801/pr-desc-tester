import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './index.css';

function NotificationBell() {
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    // Fetch notifications from the new v2 endpoint
    axios.get('http://127.0.0.1:8000/api/v2/notifications/')
      .then(response => {
        const unread = response.data.filter(n => !n.read).length;
        setUnreadCount(unread);
      })
      .catch(error => {
        console.error('Error fetching notifications:', error);
      });
  }, []);

  return (
    <div style={{ position: 'absolute', top: '20px', right: '20px', fontSize: '24px' }}>
      🔔
      {unreadCount > 0 && (
        <span style={{
          position: 'absolute', top: '-5px', right: '-10px',
          backgroundColor: 'red', color: 'white', borderRadius: '50%',
          padding: '2px 6px', fontSize: '12px'
        }}>
          {unreadCount}
        </span>
      )}
    </div>
  );
}

function App() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get('http://127.0.0.1:8000/api/tasks/')
      .then(response => {
        setTasks(response.data);
        setLoading(false);
      })
      .catch(error => {
        console.error('Error fetching data:', error);
        setLoading(false);
      });
  }, []);

  return (
    <div className="App">
      <NotificationBell />
      <header className="App-header">
        <h1>Task List</h1>
        {loading ? (
          <p>Loading...</p>
        ) : (
          <ul>
            {tasks.length > 0 ? (
              tasks.map(task => (
                <li key={task.id}>{task.title} - {task.completed ? 'Done' : 'Pending'}</li>
              ))
            ) : (
              <p>No tasks found.</p>
            )}
          </ul>
        )}
      </header>
    </div>
  );
}

export default App;
