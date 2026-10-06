import React, { useState, useMemo } from 'react';
import { Search, Mic, ChevronLeft, Filter, Trash2, Image as ImageIcon } from 'lucide-react';
import { DUMMY_PHOTOS, TIMELINES, LOCATIONS, PEOPLE } from './dummyData';
import Cleanup from './Cleanup';

export default function MVP({ onClose }) {
  const [query, setQuery] = useState('');
  const [chatLog, setChatLog] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const [aiFilterTags, setAiFilterTags] = useState([]);
  const [recoveryMode, setRecoveryMode] = useState(false);
  const [activeTab, setActiveTab] = useState('search'); // 'search' or 'cleanup'

  // Traditional Dropdown Filters
  const [filterTimeline, setFilterTimeline] = useState('All');
  const [filterLocation, setFilterLocation] = useState('All');
  const [filterPeople, setFilterPeople] = useState('All');

  const handleSearch = (e) => {
    if (e.key === 'Enter' && query.trim()) {
      const userQ = query;
      setQuery('');
      setChatLog(prev => [...prev, { role: 'user', text: userQ }]);
      setIsTyping(true);

      setTimeout(() => {
        setIsTyping(false);
        const lowerQ = userQ.toLowerCase();
        
        let foundTags = [];
        let isRecovery = false;
        let aiResponse = "I couldn't find an exact match for that. Do you remember any colors, objects, or who you were with?";

        if (lowerQ.includes('lost') || lowerQ.includes('deleted') || lowerQ.includes('missing') || lowerQ.includes('find')) {
          aiResponse = "Don't panic! It looks like you're searching for missing photos. I checked your sync status and found 15 photos in your Trash, and 15 photos that haven't synced from your old phone yet. Here they are:";
          isRecovery = true;
        }
        else if (lowerQ.includes('sick') || lowerQ.includes('medicine')) {
          aiResponse = "I found a few photos from when you were sick. Are you looking for the medicine bottle or the thermometer?";
          foundTags = ['sick'];
        } 
        else if (lowerQ.includes('bottle') || lowerQ.includes('pill')) {
          aiResponse = "Found it! Here is the medicine bottle.";
          foundTags = ['bottle'];
        }
        else if (lowerQ.includes('goa') || lowerQ.includes('beach')) {
          aiResponse = "I found several photos from Goa. Was it the small coffee shop or the beach sunset?";
          foundTags = ['goa'];
        }
        else if (lowerQ.includes('coffee') || lowerQ.includes('cafe')) {
          aiResponse = "Here is the cafe from your trip.";
          foundTags = ['cafe'];
        }
        else if (lowerQ.includes('wedding') || lowerQ.includes('party')) {
          aiResponse = "I found photos from a celebration. Are you looking for the dancing or the suits?";
          foundTags = ['wedding', 'party'];
        }
        else if (lowerQ.includes('dog') || lowerQ.includes('pet')) {
          aiResponse = "Found your pet photos!";
          foundTags = ['pet'];
        }
        else if (lowerQ.includes('receipt') || lowerQ.includes('bill')) {
          aiResponse = "I've pulled up your document screenshots.";
          foundTags = ['receipt'];
        }

        setChatLog(prev => [...prev, { role: 'ai', text: aiResponse }]);
        
        setRecoveryMode(isRecovery);
        if (!isRecovery && foundTags.length > 0) {
          setAiFilterTags(foundTags);
        } else if (isRecovery) {
          setAiFilterTags([]);
        }
      }, 1000);
    }
  };

  const activePhotos = useMemo(() => {
    return DUMMY_PHOTOS.filter(photo => {
      // 3. Recovery Mode Override
      if (recoveryMode) {
        return photo.syncStatus !== 'Backed Up';
      }

      // 1. Traditional Filters
      if (filterTimeline !== 'All' && photo.timeline !== filterTimeline) return false;
      if (filterLocation !== 'All' && photo.location !== filterLocation) return false;
      if (filterPeople !== 'All' && photo.people !== filterPeople) return false;
      
      // 2. AI Semantic Filters
      if (aiFilterTags.length > 0) {
        const matchesAi = aiFilterTags.some(tag => photo.tags.includes(tag));
        if (!matchesAi) return false;
      }
      
      return true;
    });
  }, [filterTimeline, filterLocation, filterPeople, aiFilterTags, recoveryMode]);

  return (
    <div style={{ backgroundColor: '#fff', color: '#202124', minHeight: '100vh', fontFamily: 'sans-serif', display: 'flex', flexDirection: 'column' }}>
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

      <div style={{ display: 'flex', flex: 1 }}>
        {/* Left Sidebar: Navigation & Filters */}
        <div style={{ width: '280px', borderRight: '1px solid #dadce0', padding: '24px', backgroundColor: '#f8f9fa' }}>
          
          <div style={{ marginBottom: '32px' }}>
            <h2 style={{ fontSize: '14px', color: '#5f6368', marginBottom: '16px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
              Menu
            </h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <button onClick={() => setActiveTab('search')} style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '12px 16px', borderRadius: '8px', cursor: 'pointer', border: 'none', background: activeTab === 'search' ? '#e8f0fe' : 'transparent', color: activeTab === 'search' ? '#1a73e8' : '#3c4043', fontWeight: activeTab === 'search' ? 'bold' : 'normal', textAlign: 'left', width: '100%' }}>
                <ImageIcon size={20} /> Memories & Search
              </button>
              <button onClick={() => setActiveTab('cleanup')} style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '12px 16px', borderRadius: '8px', cursor: 'pointer', border: 'none', background: activeTab === 'cleanup' ? '#e8f0fe' : 'transparent', color: activeTab === 'cleanup' ? '#1a73e8' : '#3c4043', fontWeight: activeTab === 'cleanup' ? 'bold' : 'normal', textAlign: 'left', width: '100%' }}>
                <Trash2 size={20} /> Auto-Cleanup
              </button>
            </div>
          </div>

          {activeTab === 'search' && (
            <>
              <h2 style={{ fontSize: '14px', color: '#5f6368', marginBottom: '24px', textTransform: 'uppercase', letterSpacing: '0.5px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Filter size={16} /> Traditional Search
              </h2>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '12px', fontWeight: 'bold', color: '#5f6368', marginBottom: '8px' }}>Timeline</label>
              <select value={filterTimeline} onChange={e => setFilterTimeline(e.target.value)} style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid #dadce0', outline: 'none', backgroundColor: '#fff' }}>
                <option value="All">All Time</option>
                {TIMELINES.map(t => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '12px', fontWeight: 'bold', color: '#5f6368', marginBottom: '8px' }}>People</label>
              <select value={filterPeople} onChange={e => setFilterPeople(e.target.value)} style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid #dadce0', outline: 'none', backgroundColor: '#fff' }}>
                <option value="All">Anyone</option>
                {PEOPLE.map(p => <option key={p} value={p}>{p}</option>)}
              </select>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '12px', fontWeight: 'bold', color: '#5f6368', marginBottom: '8px' }}>Place</label>
              <select value={filterLocation} onChange={e => setFilterLocation(e.target.value)} style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid #dadce0', outline: 'none', backgroundColor: '#fff' }}>
                <option value="All">Anywhere</option>
                {LOCATIONS.map(l => <option key={l} value={l}>{l}</option>)}
              </select>
            </div>
          </div>
          
              <div style={{ marginTop: '32px', fontSize: '12px', color: '#80868b', lineHeight: '1.5' }}>
                <p><strong>Status:</strong> Loaded {DUMMY_PHOTOS.length} photos across 15 themes.</p>
                <p>Traditional filters break down when the user doesn't know the exact date, person, or GPS location. Try using the AI search on the right instead!</p>
              </div>
            </>
          )}
        </div>

        {/* Main Content */}
        <div style={{ flex: 1, padding: activeTab === 'search' ? '32px' : '0', display: 'flex', flexDirection: 'column', backgroundColor: '#fff', overflowY: 'auto' }}>
          
          {activeTab === 'cleanup' ? (
            <Cleanup embedded={true} onClose={() => setActiveTab('search')} />
          ) : (
            <>
              {/* Search Bar Area */}
              <div style={{ marginBottom: '32px' }}>
            <h1 style={{ fontSize: '24px', textAlign: 'center', marginBottom: '24px', fontWeight: '400' }}>AI Memory Search</h1>
            
            <div style={{ position: 'relative', maxWidth: '700px', margin: '0 auto' }}>
              <div style={{ position: 'absolute', left: '16px', top: '14px', color: '#5f6368' }}>
                <Search size={20} />
              </div>
              <input 
                type="text" 
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={handleSearch}
                placeholder="Ask anything (e.g. 'the medicine I took when I was sick', or 'Goa trip')"
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
            <div style={{ maxWidth: '700px', margin: '0 auto 32px auto', display: 'flex', flexDirection: 'column', gap: '12px', width: '100%' }}>
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
          <div style={{ flex: 1 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <h2 style={{ fontSize: '14px', color: '#5f6368', textTransform: 'uppercase', letterSpacing: '0.5px', margin: 0 }}>
                {activePhotos.length === DUMMY_PHOTOS.length ? 'Recent Highlights' : `Found ${activePhotos.length} results`}
              </h2>
              {aiFilterTags.length > 0 || recoveryMode ? (
                <button onClick={() => { setAiFilterTags([]); setRecoveryMode(false); }} style={{ fontSize: '12px', color: '#1a73e8', background: 'none', border: 'none', cursor: 'pointer', fontWeight: 'bold' }}>
                  Clear AI Filters
                </button>
              ) : null}
            </div>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))', gap: '16px' }}>
              {activePhotos.map(photo => (
                <div key={photo.id} style={{ aspectRatio: '1', borderRadius: '12px', overflow: 'hidden', backgroundColor: '#f1f3f4', position: 'relative' }}>
                  <img src={photo.url} alt="Memory" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                  {photo.syncStatus !== 'Backed Up' && (
                    <div style={{ position: 'absolute', top: '8px', right: '8px', background: photo.syncStatus === 'In Trash' ? '#ea4335' : '#fbbc04', color: photo.syncStatus === 'In Trash' ? '#fff' : '#000', fontSize: '10px', padding: '4px 8px', borderRadius: '12px', fontWeight: 'bold' }}>
                      {photo.syncStatus}
                    </div>
                  )}
                  <div style={{ position: 'absolute', bottom: 0, left: 0, right: 0, padding: '8px', background: 'linear-gradient(transparent, rgba(0,0,0,0.7))', color: '#fff', fontSize: '10px', display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
                    {photo.tags.slice(0, 3).map(t => <span key={t} style={{background: 'rgba(255,255,255,0.2)', padding: '2px 6px', borderRadius: '4px'}}>{t}</span>)}
                  </div>
                </div>
              ))}
            </div>
            
            {activePhotos.length === 0 && (
              <div style={{ textAlign: 'center', padding: '64px', color: '#80868b' }}>
                <Search size={48} style={{ opacity: 0.2, margin: '0 auto 16px auto', display: 'block' }} />
                <p>No photos match your current filters.</p>
              </div>
            )}
          </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
