import React, { useState, useEffect } from 'react';
import { getMyProfile, updateMyProfile } from '../services/api';
import './ProfileEditor.css';

/**
 * Profile editor form for the authenticated user.
 * Allows updating bio, location, website, and avatar.
 */
const ProfileEditor = () => {
  const [profile, setProfile] = useState(null);
  const [formData, setFormData] = useState({
    bio: '',
    location: '',
    website: '',
  });
  const [avatarFile, setAvatarFile] = useState(null);
  const [avatarPreview, setAvatarPreview] = useState(null);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  useEffect(() => {
    const loadProfile = async () => {
      try {
        const response = await getMyProfile();
        const data = response.data;
        setProfile(data);
        setFormData({
          bio: data.bio || '',
          location: data.location || '',
          website: data.website || '',
        });
        setAvatarPreview(data.avatar_url);
      } catch (err) {
        setMessage({ type: 'error', text: 'Failed to load your profile.' });
      }
    };
    loadProfile();
  }, []);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleAvatarChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.size > 5 * 1024 * 1024) {
        setMessage({ type: 'error', text: 'Avatar must be under 5 MB.' });
        return;
      }
      setAvatarFile(file);
      setAvatarPreview(URL.createObjectURL(file));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setMessage({ type: '', text: '' });

    try {
      const payload = new FormData();
      payload.append('bio', formData.bio);
      payload.append('location', formData.location);
      payload.append('website', formData.website);
      if (avatarFile) {
        payload.append('avatar', avatarFile);
      }

      const response = await updateMyProfile(payload);
      setProfile(response.data);
      setMessage({ type: 'success', text: 'Profile updated successfully!' });
      setAvatarFile(null);
    } catch (err) {
      const detail =
        err.response?.data?.detail || 'Failed to update profile.';
      setMessage({ type: 'error', text: detail });
    } finally {
      setSaving(false);
    }
  };

  if (!profile) {
    return <div className="profile-editor__loading">Loading...</div>;
  }

  return (
    <div className="profile-editor">
      <h2>Edit Profile</h2>

      {message.text && (
        <div className={`profile-editor__message profile-editor__message--${message.type}`}>
          {message.text}
        </div>
      )}

      <form onSubmit={handleSubmit} className="profile-editor__form">
        {/* Avatar */}
        <div className="profile-editor__avatar-section">
          <div className="profile-editor__avatar-preview">
            {avatarPreview ? (
              <img src={avatarPreview} alt="Avatar preview" />
            ) : (
              <div className="profile-editor__avatar-placeholder">
                {profile.display_name?.charAt(0).toUpperCase() || '?'}
              </div>
            )}
          </div>
          <label className="profile-editor__avatar-upload">
            Change Avatar
            <input
              type="file"
              accept="image/*"
              onChange={handleAvatarChange}
              hidden
            />
          </label>
        </div>

        {/* Bio */}
        <div className="profile-editor__field">
          <label htmlFor="bio">Bio</label>
          <textarea
            id="bio"
            name="bio"
            value={formData.bio}
            onChange={handleInputChange}
            maxLength={500}
            rows={4}
            placeholder="Tell us about yourself..."
          />
          <span className="profile-editor__char-count">
            {formData.bio.length}/500
          </span>
        </div>

        {/* Location */}
        <div className="profile-editor__field">
          <label htmlFor="location">Location</label>
          <input
            type="text"
            id="location"
            name="location"
            value={formData.location}
            onChange={handleInputChange}
            placeholder="e.g. San Francisco, CA"
          />
        </div>

        {/* Website */}
        <div className="profile-editor__field">
          <label htmlFor="website">Website</label>
          <input
            type="url"
            id="website"
            name="website"
            value={formData.website}
            onChange={handleInputChange}
            placeholder="https://yoursite.com"
          />
        </div>

        <button
          type="submit"
          className="profile-editor__submit"
          disabled={saving}
        >
          {saving ? 'Saving...' : 'Save Changes'}
        </button>
      </form>
    </div>
  );
};

export default ProfileEditor;
