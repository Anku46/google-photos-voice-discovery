import React from 'react';
import { ChevronLeft, PieChart, Target, Search, AlertCircle, Clock, Users, ArrowRight } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

export default function AnalysisDashboard({ onClose }) {
  const failureData = [
    { name: 'Couldn\'t summarize memory', value: 60, color: '#f28b82' },
    { name: 'App misunderstood query', value: 30, color: '#fbbc04' },
    { name: 'Zero results', value: 10, color: '#81c995' }
  ];

  const instinctData = [
    { name: 'Type keywords', value: 55, color: '#8ab4f8' },
    { name: 'Scroll endlessly', value: 45, color: '#c58af9' }
  ];

  return (
    <div style={{ backgroundColor: '#121212', color: '#e8eaed', minHeight: '100vh', fontFamily: 'sans-serif', display: 'flex', flexDirection: 'column' }}>
      
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', padding: '16px 24px', borderBottom: '1px solid #3c4043', backgroundColor: '#1e1e1e', position: 'sticky', top: 0, zIndex: 10 }}>
        <button onClick={onClose} style={{ background: 'none', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px', color: '#8ab4f8', fontWeight: 'bold' }}>
          <ChevronLeft size={20} /> Back to Hub
        </button>
        <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '12px' }}>
          <PieChart size={20} color="#8ab4f8" />
          <span style={{ fontSize: '18px', fontWeight: '500' }}>Google Photos Study</span>
          <span style={{ backgroundColor: 'rgba(138, 180, 248, 0.2)', color: '#8ab4f8', padding: '4px 10px', borderRadius: '12px', fontSize: '12px', fontWeight: 'bold' }}>n = 45</span>
        </div>
      </div>

      <main style={{ padding: '32px', maxWidth: '1200px', margin: '0 auto', width: '100%' }}>
        
        {/* Headline */}
        <div style={{ backgroundColor: 'rgba(138, 180, 248, 0.1)', borderLeft: '4px solid #8ab4f8', padding: '24px', borderRadius: '8px', marginBottom: '40px' }}>
          <h2 style={{ fontSize: '20px', color: '#8ab4f8', margin: '0 0 12px 0', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Target size={24} /> Headline Insight
          </h2>
          <p style={{ fontSize: '16px', lineHeight: '1.6', margin: 0, color: '#e8eaed' }}>
            Users don't need more metadata filters; they need an interface that understands "vibes" and context. 
            The biggest barrier isn't that photos are lost, but that human memory works associatively (visuals, timeframes) 
            while current search requires exact, literal keywords.
          </p>
        </div>

        {/* Key Metrics */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px', marginBottom: '40px' }}>
          <div style={{ backgroundColor: '#1e1e1e', padding: '24px', borderRadius: '12px', border: '1px solid #3c4043' }}>
            <div style={{ color: '#f28b82', marginBottom: '16px' }}><AlertCircle size={32} /></div>
            <h3 style={{ fontSize: '18px', margin: '0 0 8px 0' }}>The Translation Gap</h3>
            <p style={{ color: '#9aa0a6', margin: 0, lineHeight: '1.5' }}><strong>60% of failures</strong> occur because users "couldn't summarize what I remembered into simple search terms."</p>
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
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '40px' }}>
          <div style={{ backgroundColor: '#1e1e1e', padding: '24px', borderRadius: '12px', border: '1px solid #3c4043' }}>
            <h3 style={{ fontSize: '16px', margin: '0 0 24px 0', color: '#9aa0a6', textTransform: 'uppercase' }}>First Instincts</h3>
            <div style={{ height: '250px' }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={instinctData} layout="vertical" margin={{ top: 0, right: 30, left: 40, bottom: 0 }}>
                  <XAxis type="number" hide />
                  <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={{ fill: '#e8eaed', fontSize: 12 }} width={120} />
                  <Tooltip cursor={{ fill: 'rgba(255,255,255,0.05)' }} contentStyle={{ backgroundColor: '#202124', border: 'none', borderRadius: '8px', color: '#fff' }} />
                  <Bar dataKey="value" radius={[0, 4, 4, 0]} barSize={32}>
                    {instinctData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div style={{ backgroundColor: '#1e1e1e', padding: '24px', borderRadius: '12px', border: '1px solid #3c4043' }}>
            <h3 style={{ fontSize: '16px', margin: '0 0 24px 0', color: '#9aa0a6', textTransform: 'uppercase' }}>Top Failure Reasons</h3>
            <div style={{ height: '250px' }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={failureData} layout="vertical" margin={{ top: 0, right: 30, left: 40, bottom: 0 }}>
                  <XAxis type="number" hide />
                  <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={{ fill: '#e8eaed', fontSize: 12 }} width={150} />
                  <Tooltip cursor={{ fill: 'rgba(255,255,255,0.05)' }} contentStyle={{ backgroundColor: '#202124', border: 'none', borderRadius: '8px', color: '#fff' }} />
                  <Bar dataKey="value" radius={[0, 4, 4, 0]} barSize={24}>
                    {failureData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Interviews & JTBD */}
        <div style={{ display: 'grid', gridTemplateColumns: '3fr 2fr', gap: '24px' }}>
          
          <div style={{ backgroundColor: '#1e1e1e', padding: '32px', borderRadius: '12px', border: '1px solid #3c4043' }}>
            <h3 style={{ fontSize: '18px', margin: '0 0 24px 0', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Users size={20} color="#8ab4f8" /> 5 Patterns from Interviews
            </h3>
            <ul style={{ margin: 0, paddingLeft: '20px', display: 'flex', flexDirection: 'column', gap: '16px', color: '#bdc1c6', lineHeight: '1.6' }}>
              <li><strong style={{ color: '#fff' }}>First Action:</strong> Users default to typing multi-word phrases ("blue slide conference") expecting AI comprehension, but get literal keyword matches instead.</li>
              <li><strong style={{ color: '#fff' }}>Biggest Failure (Vocabulary Mismatch):</strong> Users remember <em>what</em> a photo is about, but search engines only know <em>what objects</em> are in the photo.</li>
              <li><strong style={{ color: '#fff' }}>What They Remember:</strong> Broad timeframes, colors, and associated life events ("around my birthday") are recalled far more often than exact locations or dates.</li>
              <li><strong style={{ color: '#fff' }}>Workaround:</strong> Brute-force scrolling or completely abandoning the search out of frustration.</li>
              <li><strong style={{ color: '#fff' }}>What Would Build Trust:</strong> Explainability (the AI explaining <em>why</em> it retrieved a specific photo) and interactive narrowing (step-by-step filtering).</li>
            </ul>
          </div>

          <div style={{ backgroundColor: '#1e1e1e', padding: '32px', borderRadius: '12px', border: '1px solid #3c4043' }}>
            <h3 style={{ fontSize: '18px', margin: '0 0 24px 0', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Search size={20} color="#81c995" /> Jobs To Be Done (JTBD)
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
              <div style={{ backgroundColor: 'rgba(255,255,255,0.05)', padding: '16px', borderRadius: '8px', borderLeft: '4px solid #81c995' }}>
                <p style={{ margin: 0, color: '#e8eaed', lineHeight: '1.5', fontStyle: 'italic' }}>
                  "When I vaguely remember an associated detail of a past event, I want the search engine to understand that contextual clue, so that I don't have to scroll through thousands of photos."
                </p>
              </div>
              <div style={{ backgroundColor: 'rgba(255,255,255,0.05)', padding: '16px', borderRadius: '8px', borderLeft: '4px solid #fbbc04' }}>
                <p style={{ margin: 0, color: '#e8eaed', lineHeight: '1.5', fontStyle: 'italic' }}>
                  "When I am looking for a specific photo among hundreds of similar ones, I want to be able to use natural language modifiers, so that I can pinpoint the exact memory instantly."
                </p>
              </div>
            </div>
          </div>

        </div>
        
      </main>
    </div>
  );
}
