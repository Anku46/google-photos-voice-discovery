export const THEMES = [
  { name: 'Medical/Sick', tags: ['medicine', 'sick', 'pills', 'bottle', 'winter', 'fever', 'thermometer'] },
  { name: 'Goa Trip', tags: ['beach', 'goa', 'sand', 'sunset', 'ocean', 'vacation', 'friends', 'cafe', 'small'] },
  { name: 'Europe Backpacking', tags: ['paris', 'europe', 'backpacking', 'eiffel', 'summer', 'hostel', 'train'] },
  { name: 'Wedding (Friend)', tags: ['wedding', 'suit', 'dress', 'party', 'celebration', 'dancing', 'night'] },
  { name: 'Office Parties', tags: ['office', 'work', 'colleagues', 'pizza', 'desk', 'laptop', 'celebration'] },
  { name: 'Childhood Memories', tags: ['childhood', 'old', 'scanned', 'film', 'nostalgia', 'school'] },
  { name: 'Pets', tags: ['dog', 'cat', 'pet', 'park', 'playing', 'cute', 'fluffy'] },
  { name: 'Concerts', tags: ['music', 'concert', 'festival', 'lights', 'crowd', 'stage', 'night'] },
  { name: 'Food & Cafes', tags: ['food', 'breakfast', 'healthy', 'coffee', 'cafe', 'restaurant', 'dinner'] },
  { name: 'Meme Screenshots', tags: ['meme', 'funny', 'screenshot', 'twitter', 'joke', 'text'] },
  { name: 'Receipts & Bills', tags: ['receipt', 'bill', 'tax', 'document', 'paper', 'expense'] },
  { name: 'Hiking Mountains', tags: ['hike', 'mountain', 'nature', 'trees', 'trail', 'outdoors', 'green'] },
  { name: 'Road Trips', tags: ['car', 'driving', 'roadtrip', 'highway', 'window', 'friends'] },
  { name: 'Family Gatherings', tags: ['family', 'diwali', 'christmas', 'home', 'livingroom', 'dinner'] },
  { name: 'Fitness Progress', tags: ['gym', 'workout', 'mirror', 'selfie', 'weights', 'fitness', 'sweat'] }
];

export const LOCATIONS = ['Goa', 'Paris', 'Mumbai', 'London', 'Home', 'Office', 'Mountains', 'Unknown'];
export const PEOPLE = ['Mom', 'Dad', 'Sarah', 'Mike', 'John', 'David', 'Emma', 'None'];
export const TIMELINES = ['Today', 'Yesterday', 'This Week', 'This Month', '2023', '2022'];
export const SYNC_STATUS = ['Backed Up', 'In Trash', 'Device Only (Pending Sync)', 'Archived'];

const DATE_GROUPS = ['Today', 'Yesterday', 'Wednesday', 'Monday', 'September 2023', 'August 2023', 'July 2022'];

export const DUMMY_PHOTOS = THEMES.flatMap((theme, themeIdx) => 
  Array.from({ length: 10 }).map((_, i) => {
    const year = 2022 + (i % 3);
    const dateGroup = DATE_GROUPS[i % DATE_GROUPS.length];
    
    // For Deleted Photos page grouping
    const deletedGroup = ['Today', 'Yesterday', 'This Week', 'This Month'][i % 4];

    return {
      id: themeIdx * 10 + i,
      url: `https://picsum.photos/seed/${themeIdx * 100 + i}/400/400`,
      tags: theme.tags,
      theme: theme.name,
      timeline: dateGroup, // updated timeline to use dateGroup
      dateGroup: dateGroup,
      deletedGroup: deletedGroup,
      location: LOCATIONS[(themeIdx + i) % LOCATIONS.length],
      people: PEOPLE[(themeIdx * 2 + i) % PEOPLE.length],
      syncStatus: (i === 9) ? 'In Trash' : (i === 8) ? 'Device Only (Pending Sync)' : 'Backed Up'
    };
  })
);
