import React from 'react';
import './ProfileCard.css';

/**
 * Renders a single user profile card with avatar, name, and location.
 */
const ProfileCard = ({ profile }) => {
  const { display_name, username, avatar_url, location } = profile;

  return (
    <div className="profile-card">
      <div className="profile-card__avatar">
        {avatar_url ? (
          <img src={avatar_url} alt={`${display_name}'s avatar`} />
        ) : (
          <div className="profile-card__avatar-placeholder">
            {(display_name || username || '?').charAt(0).toUpperCase()}
          </div>
        )}
      </div>
      <div className="profile-card__info">
        <h3 className="profile-card__name">{display_name || username}</h3>
        <p className="profile-card__username">@{username}</p>
        {location && (
          <p className="profile-card__location">📍 {location}</p>
        )}
      </div>
    </div>
  );
};

export default ProfileCard;
