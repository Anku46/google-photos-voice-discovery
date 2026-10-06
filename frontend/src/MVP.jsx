import React, { useState } from 'react';
import { Search, Image as ImageIcon, Mic, ChevronLeft } from 'lucide-react';

const DUMMY_PHOTOS = [
  { id: 1, url: 'https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=400&q=80', tags: ['medicine', 'sick', 'pills', 'bottle', 'winter'] },
  { id: 2, url: 'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=400&q=80', tags: ['cafe', 'coffee', 'goa', 'trip', 'small'] },
  { id: 3, url: 'https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=400&q=80', tags: ['restaurant', 'dinner', 'goa', 'friends'] },
  { id: 4, url: 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=400&q=80', tags: ['beach', 'goa', 'sand', 'sunset'] },
  { id: 5, url: 'https://images.unsplash.com/photo-1516542076529-1ea3854896f2?w=400&q=80', tags: ['thermometer', 'fever', 'sick', 'winter'] },
  { id: 6, url: 'https://images.unsplash.com/photo-1498837167922-ddd27525d352?w=400&q=80', tags: ['food', 'breakfast', 'healthy'] },
  { id: 7, url: 'https://images.unsplash.com/photo-1540189549336-e6e99c3679fe?w=400&q=80', tags: ['salad', 'lunch', 'cafe'] },
  { id: 8, url: 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400&q=80', tags: ['healthy', 'bowl', 'vegetables'] },
];

export default function MVP({ onClose }) {
  const [query, setQuery] = useState('');
  const [activePhotos, setActivePhotos] = useState(DUMMY_PHOTOS);
  const [chatLog, setChatLog] = useState([]);
  const [isTyping, setIsTyping] = useState(false);

  const handleSearch = (e) => {
    if (e.key === 'Enter' && query.trim()) {
      const userQ = query;
      setQuery('');
      setChatLog(prev => [...prev, { role: 'user', text: userQ }]);
      setIsTyping(true);

      setTimeout(() => {
        setIsTyping(false);
        const lowerQ = userQ.toLowerCase();
        
        if (lowerQ.includes('sick') || lowerQ.includes('medicine')) {
          setChatLog(prev => [...prev, { 
            role: 'ai', 
            text: "I found a few photos from when you were sick last winter. Are you looking for the medicine bottle or the thermometer?"
          }]);
          setActivePhotos(DUMMY_PHOTOS.filter(p => p.tags.includes('sick')));
        } 
        else if (lowerQ.includes('bottle') || lowerQ.includes('pill')) {
          setChatLog(prev => [...prev, { role: 'ai', text: "Found it! Here is the medicine bottle from last winter." }]);
          setActivePhotos(DUMMY_PHOTOS.filter(p => p.tags.includes('bottle')));
        }
        else if (lowerQ.includes('goa') || lowerQ.includes('cafe')) {
          setChatLog(prev => [...prev, { 
            role: 'ai', 
            text: "I found 3 places from your Goa trip. Was it the small coffee shop or the dinner restaurant?"
          }]);
          setActivePhotos(DUMMY_PHOTOS.filter(p => p.tags.includes('goa')));
        }
        else if (lowerQ.includes('coffee') || lowerQ.includes('small')) {
          setChatLog(prev => [...prev, { role: 'ai', text: "Here is the small cafe from your Goa trip." }]);
          setActivePhotos(DUMMY_PHOTOS.filter(p => p.tags.includes('coffee')));
        }
        else {
          setChatLog(prev => [...prev, { 
            role: 'ai', 
            text: "I couldn't find an exact match for that. Do you remember any colors, objects, or who you were with?" 
          }]);
        }
      }, 1000);
    }
  };

  return (
    <div style={{ backgroundColor: '#fff', color: '#202124', minHeight: '100vh', fontFamily: 'sans-serif' }}>
      {/* Top Nav */}
      <div style={{ display: 'flex', alignItems: 'center', padding: '16px 24px', borderBottom: '1px solid #dadce0', position: 'sticky', top: 0, backgroundColor: '#fff', zIndex: 10 }}>
        <button onClick={onClose} style={{ background: 'none', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px', color: '#1a73e8', fontWeight: 'bold' }}>
          <ChevronLeft size={20} /> Back to Dashboard
        </button>
        <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '12px', color: '#5f6368' }}>
          <span style={{ fontSize: '18px', fontWeight: '500' }}>Google Photos</span>
          <span style={{ backgroundColor: '#fce8e6', color: '#d93025', padding: '2px 8px', borderRadius: '4px', fontSize: '12px', fontWeight: 'bold' }}>MVP Prototype</span>
        </div>
      </div>

      <div style={{ maxWidth: '800px', margin: '0 auto', padding: '32px 16px' }}>
        
        {/* Search Bar Area */}
        <div style={{ marginBottom: '32px' }}>
          <h1 style={{ fontSize: '24px', textAlign: 'center', marginBottom: '24px', fontWeight: '400' }}>Find your memories</h1>
          
          <div style={{ position: 'relative', maxWidth: '600px', margin: '0 auto' }}>
            <div style={{ position: 'absolute', left: '16px', top: '14px', color: '#5f6368' }}>
              <Search size={20} />
            </div>
            <input 
              type="text" 
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleSearch}
              placeholder="Ask anything (e.g. 'the medicine I took when I was sick')"
              style={{ 
                width: '100%', padding: '14px 48px', borderRadius: '24px', 
                border: '1px solid #dfe1e5', boxShadow: '0 1px 6px rgba(32,33,36,.28)',
                fontSize: '16px', outline: 'none'
              }}
            />
            <div style={{ position: 'absolute', right: '16px', top: '14px', color: '#1a73e8' }}>
              <Mic size={20} />
            </div>
          </div>
        </div>

        {/* Conversational AI Area */}
        {chatLog.length > 0 && (
          <div style={{ maxWidth: '600px', margin: '0 auto 32px auto', display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {chatLog.map((msg, i) => (
              <div key={i} style={{ 
                alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                backgroundColor: msg.role === 'user' ? '#e8f0fe' : '#f1f3f4',
                color: msg.role === 'user' ? '#1967d2' : '#202124',
                padding: '12px 16px', borderRadius: '16px', maxWidth: '80%', fontSize: '14px',
                borderBottomRightRadius: msg.role === 'user' ? '4px' : '16px',
                borderBottomLeftRadius: msg.role === 'ai' ? '4px' : '16px'
              }}>
                {msg.text}
              </div>
            ))}
            {isTyping && (
              <div style={{ alignSelf: 'flex-start', backgroundColor: '#f1f3f4', padding: '12px 16px', borderRadius: '16px', fontSize: '14px', borderBottomLeftRadius: '4px', color: '#5f6368' }}>
                Searching memories...
              </div>
            )}
          </div>
        )}

        {/* Photos Grid */}
        <div>
          <h2 style={{ fontSize: '14px', color: '#5f6368', marginBottom: '16px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
            {activePhotos.length === DUMMY_PHOTOS.length ? 'Recent Highlights' : `Found ${activePhotos.length} results`}
          </h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))', gap: '16px' }}>
            {activePhotos.map(photo => (
              <div key={photo.id} style={{ aspectRatio: '1', borderRadius: '12px', overflow: 'hidden', backgroundColor: '#f1f3f4' }}>
                <img src={photo.url} alt="Memory" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
              </div>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
}
