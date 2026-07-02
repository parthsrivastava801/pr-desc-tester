import React, { useState, useEffect } from 'react';
import { getProfiles } from '../services/api';
import ProfileCard from './ProfileCard';
import './ProfileList.css';

/**
 * Displays a searchable, paginated grid of public user profiles.
 */
const ProfileList = () => {
  const [profiles, setProfiles] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchProfiles = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await getProfiles(search);
        setProfiles(response.data.results || []);
      } catch (err) {
        setError('Failed to load profiles. Please try again.');
        console.error('Error fetching profiles:', err);
      } finally {
        setLoading(false);
      }
    };

    // Debounce search input
    const timeoutId = setTimeout(fetchProfiles, 300);
    return () => clearTimeout(timeoutId);
  }, [search]);

  return (
    <div className="profile-list">
      <div className="profile-list__header">
        <h2>User Profiles</h2>
        <div className="profile-list__search">
          <input
            type="text"
            placeholder="Search by username..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="profile-list__search-input"
          />
        </div>
      </div>

      {loading && (
        <div className="profile-list__loading">
          <div className="spinner" />
          <p>Loading profiles...</p>
        </div>
      )}

      {error && (
        <div className="profile-list__error">
          <p>{error}</p>
          <button onClick={() => setSearch(search)}>Retry</button>
        </div>
      )}

      {!loading && !error && profiles.length === 0 && (
        <div className="profile-list__empty">
          <p>No profiles found.</p>
        </div>
      )}

      {!loading && !error && (
        <div className="profile-list__grid">
          {profiles.map((profile) => (
            <ProfileCard key={profile.id} profile={profile} />
          ))}
        </div>
      )}
    </div>
  );
};

export default ProfileList;
