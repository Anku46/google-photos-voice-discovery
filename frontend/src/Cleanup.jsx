import React, { useState } from 'react';
import { ChevronLeft, Trash2, AlertTriangle, Clock, Copy, Check, X } from 'lucide-react';

// Mock Data
const MOCK_DUPLICATES = [
  { id: 'd1', url: 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=400&q=80', similarUrl: 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=400&q=80', reason: 'Duplicate' },
  { id: 'd2', url: 'https://images.unsplash.com/photo-1516542076529-1ea3854896f2?w=400&q=80', similarUrl: 'https://images.unsplash.com/photo-1516542076529-1ea3854896f2?w=400&q=80', reason: 'Duplicate' },
];

const MOCK_INACTIVE = [
  { id: 'i1', url: 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400&q=80', reason: 'Not viewed in 3 years' },
  { id: 'i2', url: 'https://images.unsplash.com/photo-1540189549336-e6e99c3679fe?w=400&q=80', reason: 'Not viewed in 3 years' },
  { id: 'i3', url: 'https://images.unsplash.com/photo-1498837167922-ddd27525d352?w=400&q=80', reason: 'Not viewed in 3 years' },
];

export default function Cleanup({ onClose, embedded }) {
  const [view, setView] = useState('notifications'); // 'notifications', 'review-dupes', 'review-inactive', 'confirm-dupe'
  const [selectedPhoto, setSelectedPhoto] = useState(null);
  
  const [duplicates, setDuplicates] = useState(MOCK_DUPLICATES);
  const [inactive, setInactive] = useState(MOCK_INACTIVE);

  const handleUndoDupe = (photo) => {
    setSelectedPhoto(photo);
    setView('confirm-dupe');
  };

  const handleKeepPhoto = () => {
    setDuplicates(prev => prev.filter(p => p.id !== selectedPhoto.id));
    setView('review-dupes');
    setSelectedPhoto(null);
  };

  const handleDeleteAnyway = () => {
    setDuplicates(prev => prev.filter(p => p.id !== selectedPhoto.id));
    setView('review-dupes');
    setSelectedPhoto(null);
  };

  const handleUndoInactive = (id) => {
    setInactive(prev => prev.filter(p => p.id !== id));
  };

  return (
    <div style={{ backgroundColor: '#fff', color: '#202124', height: embedded ? '100%' : 'minHeight: 100vh', fontFamily: 'sans-serif', display: 'flex', flexDirection: 'column' }}>
      
      {/* Top Nav (only if not embedded) */}
      {!embedded && (
        <div style={{ display: 'flex', alignItems: 'center', padding: '16px 24px', borderBottom: '1px solid #dadce0', position: 'sticky', top: 0, backgroundColor: '#fff', zIndex: 10 }}>
          <button 
            onClick={() => view === 'notifications' ? onClose() : setView('notifications')} 
            style={{ background: 'none', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px', color: '#1a73e8', fontWeight: 'bold' }}
          >
            <ChevronLeft size={20} /> {view === 'notifications' ? 'Back to Dashboard' : 'Back to Notifications'}
          </button>
          <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '12px', color: '#5f6368' }}>
            <span style={{ fontSize: '18px', fontWeight: '500' }}>Google Photos</span>
            <span style={{ backgroundColor: '#e8f0fe', color: '#1a73e8', padding: '2px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: 'bold' }}>Auto-Cleanup</span>
          </div>
        </div>
      )}

      {/* Embedded Nav Header (if embedded and not on notifications) */}
      {embedded && view !== 'notifications' && (
        <div style={{ padding: '16px 24px', borderBottom: '1px solid #dadce0' }}>
          <button 
            onClick={() => setView('notifications')} 
            style={{ background: 'none', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px', color: '#1a73e8', fontWeight: 'bold' }}
          >
            <ChevronLeft size={20} /> Back to Notifications
          </button>
        </div>
      )}

      <div style={{ maxWidth: '800px', margin: '0 auto', padding: '32px 16px', width: '100%' }}>
        
        {/* VIEW: Notifications */}
        {view === 'notifications' && (
          <div>
            <h1 style={{ fontSize: '24px', marginBottom: '8px', fontWeight: '400', color: '#174ea6' }}>Scheduled for Deletion</h1>
            <p style={{ color: '#5f6368', marginBottom: '32px' }}>Review items scheduled for automatic cleanup to save storage.</p>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              
              {duplicates.length > 0 && (
                <div onClick={() => setView('review-dupes')} style={{ display: 'flex', alignItems: 'center', padding: '20px', border: '1px solid #dadce0', borderRadius: '12px', cursor: 'pointer', hover: { backgroundColor: '#f8f9fa' } }}>
                  <div style={{ background: '#fce8e6', padding: '12px', borderRadius: '50%', marginRight: '16px', color: '#d93025' }}>
                    <Copy size={24} />
                  </div>
                  <div style={{ flex: 1 }}>
                    <h3 style={{ margin: '0 0 4px 0', fontSize: '16px', color: '#174ea6' }}>{duplicates.length} Duplicate Photos</h3>
                    <p style={{ margin: 0, color: '#5f6368', fontSize: '13px' }}>These photos are visually identical to others in your library.</p>
                  </div>
                  <ChevronLeft size={20} style={{ color: '#5f6368', transform: 'rotate(180deg)' }} />
                </div>
              )}

              {inactive.length > 0 && (
                <div onClick={() => setView('review-inactive')} style={{ display: 'flex', alignItems: 'center', padding: '20px', border: '1px solid #dadce0', borderRadius: '12px', cursor: 'pointer' }}>
                  <div style={{ background: '#fef7e0', padding: '12px', borderRadius: '50%', marginRight: '16px', color: '#ea8600' }}>
                    <Clock size={24} />
                  </div>
                  <div style={{ flex: 1 }}>
                    <h3 style={{ margin: '0 0 4px 0', fontSize: '16px', color: '#174ea6' }}>{inactive.length} Inactive Photos</h3>
                    <p style={{ margin: 0, color: '#5f6368', fontSize: '13px' }}>Not viewed, clicked, or searched for over a long period.</p>
                  </div>
                  <ChevronLeft size={20} style={{ color: '#5f6368', transform: 'rotate(180deg)' }} />
                </div>
              )}

              {duplicates.length === 0 && inactive.length === 0 && (
                <div style={{ textAlign: 'center', padding: '48px', color: '#80868b' }}>
                  <Check size={48} style={{ opacity: 0.2, margin: '0 auto 16px auto', display: 'block', color: '#34a853' }} />
                  <p>Your library is clean! Nothing scheduled for deletion.</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* VIEW: Review Duplicates */}
        {view === 'review-dupes' && (
          <div>
            <h1 style={{ fontSize: '24px', marginBottom: '8px', fontWeight: '400', color: '#174ea6' }}>Review Duplicates</h1>
            <p style={{ color: '#5f6368', marginBottom: '32px' }}>These will be permanently deleted in 30 days unless you undo.</p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
              {duplicates.map(photo => (
                <div key={photo.id} style={{ display: 'flex', alignItems: 'center', gap: '24px', padding: '16px', border: '1px solid #dadce0', borderRadius: '12px' }}>
                  <img src={photo.url} alt="Duplicate" style={{ width: '120px', height: '120px', objectFit: 'cover', borderRadius: '8px' }} />
                  <div style={{ flex: 1 }}>
                    <h4 style={{ margin: '0 0 8px 0', color: '#d93025' }}>Scheduled for deletion</h4>
                    <p style={{ margin: '0 0 16px 0', color: '#5f6368', fontSize: '13px' }}>Reason: Duplicate photo detected</p>
                    <button onClick={() => handleUndoDupe(photo)} style={{ padding: '8px 16px', background: '#fff', border: '1px solid #dadce0', borderRadius: '24px', cursor: 'pointer', fontWeight: 'bold', color: '#1a73e8' }}>
                      Undo Deletion
                    </button>
                  </div>
                </div>
              ))}
              {duplicates.length === 0 && <p style={{ color: '#80868b' }}>All duplicates resolved.</p>}
            </div>
          </div>
        )}

        {/* VIEW: Review Inactive */}
        {view === 'review-inactive' && (
          <div>
            <h1 style={{ fontSize: '24px', marginBottom: '8px', fontWeight: '400', color: '#174ea6' }}>Review Inactive</h1>
            <p style={{ color: '#5f6368', marginBottom: '32px' }}>These will be permanently deleted in 30 days unless you undo.</p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
              {inactive.map(photo => (
                <div key={photo.id} style={{ display: 'flex', alignItems: 'center', gap: '24px', padding: '16px', border: '1px solid #dadce0', borderRadius: '12px' }}>
                  <img src={photo.url} alt="Inactive" style={{ width: '120px', height: '120px', objectFit: 'cover', borderRadius: '8px' }} />
                  <div style={{ flex: 1 }}>
                    <h4 style={{ margin: '0 0 8px 0', color: '#d93025' }}>Scheduled for deletion</h4>
                    <p style={{ margin: '0 0 16px 0', color: '#5f6368', fontSize: '13px' }}>Reason: {photo.reason}</p>
                    <button onClick={() => handleUndoInactive(photo.id)} style={{ padding: '8px 16px', background: '#fff', border: '1px solid #dadce0', borderRadius: '24px', cursor: 'pointer', fontWeight: 'bold', color: '#1a73e8' }}>
                      Keep Photo
                    </button>
                  </div>
                </div>
              ))}
              {inactive.length === 0 && <p style={{ color: '#80868b' }}>All inactive photos resolved.</p>}
            </div>
          </div>
        )}

        {/* VIEW: Confirm Duplicate Undo */}
        {view === 'confirm-dupe' && selectedPhoto && (
          <div>
            <h1 style={{ fontSize: '24px', marginBottom: '8px', fontWeight: '400', color: '#174ea6' }}>Are you sure you want to keep this photo?</h1>
            <p style={{ color: '#5f6368', marginBottom: '32px' }}>Here are similar photos you already have in your library.</p>
            
            <div style={{ display: 'flex', gap: '24px', justifyContent: 'center', marginBottom: '48px' }}>
              
              {/* The Photo to be Deleted */}
              <div style={{ textAlign: 'center' }}>
                <div style={{ position: 'relative', width: '200px', height: '200px', margin: '0 auto', borderRadius: '12px', border: '3px solid #d93025', overflow: 'hidden' }}>
                  <img src={selectedPhoto.url} alt="To delete" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                  <div style={{ position: 'absolute', bottom: 0, left: 0, right: 0, background: '#d93025', color: '#fff', fontSize: '12px', padding: '4px', fontWeight: 'bold' }}>
                    Scheduled to delete
                  </div>
                </div>
              </div>

              {/* The Existing Similar Photo */}
              <div style={{ textAlign: 'center' }}>
                <div style={{ position: 'relative', width: '200px', height: '200px', margin: '0 auto', borderRadius: '12px', border: '3px solid #34a853', overflow: 'hidden' }}>
                  <img src={selectedPhoto.similarUrl} alt="Similar" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                  <div style={{ position: 'absolute', bottom: 0, left: 0, right: 0, background: '#34a853', color: '#fff', fontSize: '12px', padding: '4px', fontWeight: 'bold' }}>
                    Already in Library
                  </div>
                </div>
              </div>

            </div>

            <div style={{ display: 'flex', justifyContent: 'center', gap: '16px' }}>
              <button onClick={handleKeepPhoto} style={{ padding: '12px 24px', background: '#1a73e8', color: '#fff', border: 'none', borderRadius: '24px', cursor: 'pointer', fontWeight: 'bold', fontSize: '14px' }}>
                Keep it anyway
              </button>
              <button onClick={handleDeleteAnyway} style={{ padding: '12px 24px', background: '#fff', color: '#d93025', border: '1px solid #d93025', borderRadius: '24px', cursor: 'pointer', fontWeight: 'bold', fontSize: '14px' }}>
                Delete this photo
              </button>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}
