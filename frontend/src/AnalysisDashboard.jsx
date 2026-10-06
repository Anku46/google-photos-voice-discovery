import React, { useState } from 'react';
import { ChevronLeft, PieChart, Target, Search, AlertCircle, Clock, Users, ArrowRight, X } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

// Anonymous drill-down data
const drillDownData = {
  'Couldn\'t summarize memory': [
    { id: 'User 12', device: 'Android', library: '5,000+', quote: "I remembered it was a blue shirt at the beach, but I didn't know how to search that.", instinct: "Scroll endlessly" },
    { id: 'User 28', device: 'iOS', library: '1,000-5,000', quote: "I just couldn't summarize what I remembered into simple search terms.", instinct: "Type keywords" },
    { id: 'User 34', device: 'Android', library: '5,000+', quote: "I knew it was last winter near a cafe, but the search bar needs exact words.", instinct: "Scroll endlessly" },
    { id: 'User 03', device: 'Android', library: '5,000+', quote: "Hard to put visual vibes into words.", instinct: "Type keywords" }
  ],
  'App misunderstood query': [
    { id: 'User 19', device: 'iOS', library: '5,000+', quote: "I searched 'receipt' and it gave me pictures of menus instead.", instinct: "Type keywords" },
    { id: 'User 41', device: 'Android', library: '1,000-5,000', quote: "The app misunderstood my query completely. Searched literally.", instinct: "Type keywords" },
    { id: 'User 07', device: 'Android', library: '5,000+', quote: "I typed 'Goa sunset' and got generic beaches from other trips.", instinct: "Type keywords" }
  ],
  'Zero results': [
    { id: 'User 14', device: 'iOS', library: '1,000-5,000', quote: "Search returned zero results for 'whiteboard notes red circle'.", instinct: "Type keywords" },
    { id: 'User 09', device: 'Android', library: '5,000+', quote: "Nothing showed up so I just gave up.", instinct: "Type keywords" }
  ],
  'Type keywords': [
    { id: 'User 22', device: 'Android', library: '5,000+', quote: "Type descriptive keywords into the search bar (e.g., 'Goa beach sunset 2022').", fail: "App misunderstood query" },
    { id: 'User 18', device: 'iOS', library: '1,000-5,000', quote: "I try typing exactly what I remember.", fail: "Zero results" },
    { id: 'User 31', device: 'Android', library: '5,000+', quote: "I type keywords but usually end up frustrated.", fail: "Couldn't summarize memory" }
  ],
  'Scroll endlessly': [
    { id: 'User 05', device: 'Android', library: '5,000+', quote: "I don't know how to give query to google i just Scroll the photos.", fail: "Couldn't summarize memory" },
    { id: 'User 11', device: 'iOS', library: '1,000-5,000', quote: "Scroll endlessly backward through the main photo timeline/feed.", fail: "Couldn't summarize memory" },
    { id: 'User 42', device: 'Android', library: '5,000+', quote: "I just scroll until I find it or get tired.", fail: "Couldn't summarize memory" }
  ]
};

export default function AnalysisDashboard({ onClose }) {
  const [selectedSegment, setSelectedSegment] = useState(null);

  const failureData = [
    { name: 'Couldn\'t summarize memory', value: 60, color: '#f28b82' },
    { name: 'App misunderstood query', value: 30, color: '#fbbc04' },
    { name: 'Zero results', value: 10, color: '#81c995' }
  ];

  const instinctData = [
    { name: 'Type keywords', value: 55, color: '#8ab4f8' },
    { name: 'Scroll endlessly', value: 45, color: '#c58af9' }
  ];

  const handleChartClick = (data) => {
    if (data && data.activePayload && data.activePayload.length > 0) {
      const name = data.activePayload[0].payload.name;
      if (drillDownData[name]) {
        setSelectedSegment({ name, data: drillDownData[name], color: data.activePayload[0].payload.color });
      }
    }
  };

  return (
    <div style={{ backgroundColor: '#121212', color: '#e8eaed', minHeight: '100vh', fontFamily: 'sans-serif', display: 'flex', flexDirection: 'column' }}>
      
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', padding: '16px 24px', borderBottom: '1px solid #3c4043', backgroundColor: '#1e1e1e', position: 'sticky', top: 0, zIndex: 10 }}>
        <button onClick={onClose} style={{ background: 'none', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px', color: '#8ab4f8', fontWeight: 'bold' }}>
          <ChevronLeft size={20} /> Back to Hub
        </button>
        <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '12px' }}>
          <PieChart size={20} color="#8ab4f8" />
          <span style={{ fontSize: '18px', fontWeight: '500' }}>Google Photos Contextual Search & Retrieval Study</span>
          <span style={{ backgroundColor: 'rgba(138, 180, 248, 0.2)', color: '#8ab4f8', padding: '4px 10px', borderRadius: '12px', fontSize: '12px', fontWeight: 'bold' }}>n = 45</span>
        </div>
      </div>

      <main style={{ padding: '32px', maxWidth: '1200px', margin: '0 auto', width: '100%', position: 'relative' }}>
        
        {/* Headline Hypotheses */}
        <div style={{ backgroundColor: 'rgba(138, 180, 248, 0.1)', borderLeft: '4px solid #8ab4f8', padding: '24px', borderRadius: '8px', marginBottom: '40px' }}>
          <h2 style={{ fontSize: '20px', color: '#8ab4f8', margin: '0 0 16px 0', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Target size={24} /> Hypotheses Under Test
          </h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', color: '#e8eaed', fontSize: '15px', lineHeight: '1.6' }}>
            <p style={{ margin: 0 }}><strong>H1 - The Translation Gap:</strong> Users remember visual cues and associative contexts (events, colors, broad timeframes) but struggle to map these onto literal search keywords.</p>
            <p style={{ margin: 0 }}><strong>H2 - The Scroll Fallback:</strong> When text searches yield zero results or literal mismatches, users default to brute-force timeline scrolling, leading to high abandonment.</p>
            <p style={{ margin: 0 }}><strong>H3 - Contextual Misalignment:</strong> Users expect the search bar to comprehend natural language intent (e.g., "pasta dish near my birthday"), while the engine processes rigid object identification.</p>
          </div>
        </div>

        {/* Key Metrics */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px', marginBottom: '40px' }}>
          <div style={{ backgroundColor: '#1e1e1e', padding: '24px', borderRadius: '12px', border: '1px solid #3c4043' }}>
            <div style={{ color: '#f28b82', marginBottom: '16px' }}><AlertCircle size={32} /></div>
            <h3 style={{ fontSize: '18px', margin: '0 0 8px 0' }}>The Translation Gap</h3>
            <p style={{ color: '#9aa0a6', margin: 0, lineHeight: '1.5' }}><strong>60% of failures</strong> occur because users couldn't summarize what they remembered into simple search terms.</p>
          </div>
          
          <div style={{ backgroundColor: '#1e1e1e', padding: '24px', borderRadius: '12px', border: '1px solid #3c4043' }}>
            <div style={{ color: '#fbbc04', marginBottom: '16px' }}><Clock size={32} /></div>
            <h3 style={{ fontSize: '18px', margin: '0 0 8px 0' }}>The Time Tax</h3>
            <p style={{ color: '#9aa0a6', margin: 0, lineHeight: '1.5' }}>When searches succeed, they still take <strong>5–15 minutes</strong> of tedious scrolling or query tweaking.</p>
          </div>

          <div style={{ backgroundColor: '#1e1e1e', padding: '24px', borderRadius: '12px', border: '1px solid #3c4043' }}>
            <div style={{ color: '#81c995', marginBottom: '16px' }}><ArrowRight size={32} /></div>
            <h3 style={{ fontSize: '18px', margin: '0 0 8px 0' }}>The Drop-off</h3>
            <p style={{ color: '#9aa0a6', margin: 0, lineHeight: '1.5' }}>"Scroll or give up" is the dominant workaround, indicating a massive abandonment rate for memory retrieval.</p>
          </div>
        </div>

        {/* Charts Section */}
        <p style={{ color: '#9aa0a6', marginBottom: '16px', fontSize: '14px', fontStyle: 'italic' }}>* Click on any bar below to view relevant respondent data segments.</p>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '40px' }}>
          
          <div style={{ backgroundColor: '#1e1e1e', padding: '24px', borderRadius: '12px', border: '1px solid #3c4043', cursor: 'pointer', transition: 'all 0.2s' }} className="chart-card">
            <h3 style={{ fontSize: '16px', margin: '0 0 24px 0', color: '#9aa0a6', textTransform: 'uppercase' }}>First Instincts</h3>
            <div style={{ height: '250px' }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={instinctData} layout="vertical" margin={{ top: 0, right: 30, left: 40, bottom: 0 }} onClick={handleChartClick} style={{ cursor: 'pointer' }}>
                  <XAxis type="number" hide />
                  <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={{ fill: '#e8eaed', fontSize: 12, cursor: 'pointer' }} width={120} />
                  <Tooltip cursor={{ fill: 'rgba(255,255,255,0.05)' }} contentStyle={{ backgroundColor: '#202124', border: 'none', borderRadius: '8px', color: '#fff' }} />
                  <Bar dataKey="value" radius={[0, 4, 4, 0]} barSize={32}>
                    {instinctData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} style={{ cursor: 'pointer' }} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div style={{ backgroundColor: '#1e1e1e', padding: '24px', borderRadius: '12px', border: '1px solid #3c4043', cursor: 'pointer', transition: 'all 0.2s' }} className="chart-card">
            <h3 style={{ fontSize: '16px', margin: '0 0 24px 0', color: '#9aa0a6', textTransform: 'uppercase' }}>Top Failure Reasons</h3>
            <div style={{ height: '250px' }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={failureData} layout="vertical" margin={{ top: 0, right: 30, left: 40, bottom: 0 }} onClick={handleChartClick} style={{ cursor: 'pointer' }}>
                  <XAxis type="number" hide />
                  <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={{ fill: '#e8eaed', fontSize: 12, cursor: 'pointer' }} width={150} />
                  <Tooltip cursor={{ fill: 'rgba(255,255,255,0.05)' }} contentStyle={{ backgroundColor: '#202124', border: 'none', borderRadius: '8px', color: '#fff' }} />
                  <Bar dataKey="value" radius={[0, 4, 4, 0]} barSize={24}>
                    {failureData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} style={{ cursor: 'pointer' }} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Interviews Section */}
        <div style={{ backgroundColor: '#1e1e1e', padding: '32px', borderRadius: '12px', border: '1px solid #3c4043', marginBottom: '40px' }}>
          <h3 style={{ fontSize: '18px', margin: '0 0 24px 0', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Users size={20} color="#8ab4f8" /> High-Intent Retriever Profiles (Interviewees)
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
            <div style={{ padding: '16px', backgroundColor: 'rgba(255,255,255,0.03)', borderRadius: '8px', borderLeft: '3px solid #8ab4f8' }}>
              <h4 style={{ margin: '0 0 8px 0', color: '#fff' }}>Naman</h4>
              <p style={{ margin: 0, color: '#9aa0a6', fontSize: '13px' }}>Heavy traveler & parent. Seeks specific vacation memories and family milestones.</p>
            </div>
            <div style={{ padding: '16px', backgroundColor: 'rgba(255,255,255,0.03)', borderRadius: '8px', borderLeft: '3px solid #fbbc04' }}>
              <h4 style={{ margin: '0 0 8px 0', color: '#fff' }}>Divya</h4>
              <p style={{ margin: 0, color: '#9aa0a6', fontSize: '13px' }}>Active student. Frequent screenshot saver looking for lecture notes and schedules.</p>
            </div>
            <div style={{ padding: '16px', backgroundColor: 'rgba(255,255,255,0.03)', borderRadius: '8px', borderLeft: '3px solid #81c995' }}>
              <h4 style={{ margin: '0 0 8px 0', color: '#fff' }}>Aman</h4>
              <p style={{ margin: 0, color: '#9aa0a6', fontSize: '13px' }}>Foodie. Searches for specific restaurant dishes and cafe interiors.</p>
            </div>
            <div style={{ padding: '16px', backgroundColor: 'rgba(255,255,255,0.03)', borderRadius: '8px', borderLeft: '3px solid #f28b82' }}>
              <h4 style={{ margin: '0 0 8px 0', color: '#fff' }}>Urmila</h4>
              <p style={{ margin: 0, color: '#9aa0a6', fontSize: '13px' }}>Working professional. Looks for travel receipts and intercity transit tickets.</p>
            </div>
            <div style={{ padding: '16px', backgroundColor: 'rgba(255,255,255,0.03)', borderRadius: '8px', borderLeft: '3px solid #c58af9' }}>
              <h4 style={{ margin: '0 0 8px 0', color: '#fff' }}>Pulkit</h4>
              <p style={{ margin: 0, color: '#9aa0a6', fontSize: '13px' }}>Casual photo taker (~4k photos). Relies primarily on endless timeline scrolling.</p>
            </div>
          </div>
        </div>

      </main>

      {/* Drill-down Modal */}
      {selectedSegment && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.7)', zIndex: 100, display: 'flex', alignItems: 'center', justifyContent: 'center', backdropFilter: 'blur(4px)' }}>
          <div style={{ backgroundColor: '#1e1e1e', border: '1px solid #3c4043', borderRadius: '16px', width: '90%', maxWidth: '600px', maxHeight: '80vh', display: 'flex', flexDirection: 'column', boxShadow: '0 24px 48px rgba(0,0,0,0.5)' }}>
            <div style={{ padding: '24px', borderBottom: '1px solid #3c4043', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h3 style={{ margin: 0, color: selectedSegment.color, display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Search size={20} /> Segment: {selectedSegment.name}
              </h3>
              <button onClick={() => setSelectedSegment(null)} style={{ background: 'none', border: 'none', color: '#9aa0a6', cursor: 'pointer' }}>
                <X size={24} />
              </button>
            </div>
            <div style={{ padding: '24px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <p style={{ color: '#9aa0a6', margin: '0 0 8px 0', fontSize: '14px' }}>Showing relevant anonymized respondent data:</p>
              {selectedSegment.data.map((item, idx) => (
                <div key={idx} style={{ backgroundColor: 'rgba(255,255,255,0.03)', padding: '16px', borderRadius: '8px', borderLeft: `4px solid ${selectedSegment.color}` }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px', fontSize: '12px', color: '#9aa0a6' }}>
                    <span style={{ fontWeight: 'bold', color: '#e8eaed' }}>{item.id}</span>
                    <span>{item.device} • {item.library} photos</span>
                  </div>
                  <p style={{ margin: '0 0 12px 0', color: '#fff', fontStyle: 'italic', lineHeight: '1.5' }}>"{item.quote}"</p>
                  <div style={{ fontSize: '12px', color: '#8ab4f8' }}>
                    {item.instinct && <span>First Instinct: {item.instinct}</span>}
                    {item.fail && <span>Failure Reason: {item.fail}</span>}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
