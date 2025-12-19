# Infinite Path Drawing Animation

## Overview
Updated the path drawing animation to **loop continuously** instead of playing just once, creating an engaging, always-active visual effect.

## Animation Timeline (5 seconds total)

```
0% ────────► 40% ────────► 60% ────► 65% ──────► 100%
[Hidden]    [Drawing]    [Visible]  [Reset]   [Hidden]
```

### Breakdown:

1. **0% - 40% (2 seconds)**: ✏️ **Drawing Phase**
   - Path draws from start to finish
   - Smooth `ease-in-out` animation
   - Line progressively appears

2. **40% - 60% (1 second)**: 👁️ **Display Phase**
   - Path fully visible
   - Pause to let users see the complete route
   - All details clear and readable

3. **60% - 65% (0.25 seconds)**: 🔄 **Quick Reset**
   - Path quickly disappears
   - Fast reset to prepare for next loop
   - Barely noticeable transition

4. **65% - 100% (1.75 seconds)**: ⏸️ **Pause Phase**
   - Brief pause before restarting
   - Prevents animation from feeling too rushed
   - Creates natural rhythm

## Technical Details

### CSS Keyframes (`index.css`):
```css
@keyframes drawPath {
  0% { stroke-dashoffset: var(--path-length, 1000); }      /* Hidden */
  40% { stroke-dashoffset: 0; }                             /* Fully drawn */
  60% { stroke-dashoffset: 0; }                             /* Stay visible */
  65% { stroke-dashoffset: var(--path-length, 1000); }     /* Quick hide */
  100% { stroke-dashoffset: var(--path-length, 1000); }    /* Pause hidden */
}
```

### React Component (`MapCanvas.jsx`):
```javascript
animation: `drawPath 5s ease-in-out infinite`
```

- **Duration**: 5 seconds per loop
- **Timing**: `ease-in-out` for smooth start/end
- **Repeat**: `infinite` - never stops

## Visual Effects

### What Users See:
1. ✨ Path appears to "draw itself" smoothly
2. 🎯 Complete path displayed for 1 second
3. 🔄 Quick fade out
4. ⏰ Brief pause
5. 🔁 **Loop restarts automatically**

### Benefits:
✅ **Always Active**: Continuously draws attention to the route  
✅ **Engaging**: Movement keeps the UI feeling alive  
✅ **Clear**: Pause phase ensures path is fully visible  
✅ **Smooth**: Natural rhythm prevents jarring transitions  
✅ **Premium**: Polished, professional animation loop  

## Timing Considerations

### Why 5 seconds?
- **2s drawing**: Enough time to follow the animation
- **1s visible**: Time to see the complete path
- **0.25s reset**: Fast enough to be nearly invisible
- **1.75s pause**: Prevents overwhelming repetition

### Adjustable Parameters:
You can modify the animation speed by changing:
- **Total duration**: `5s` → `3s` (faster) or `7s` (slower)
- **Pause timing**: Adjust keyframe percentages in CSS

## Examples

### Fast Loop (3 seconds):
```css
animation: `drawPath 3s ease-in-out infinite`
```
- More rapid, energetic feel
- Good for short paths

### Slow Loop (7 seconds):
```css
animation: `drawPath 7s ease-in-out infinite`
```
- More relaxed, detailed view
- Good for complex paths

## Files Modified
1. `frontend/src/index.css` - Updated keyframe animation
2. `frontend/src/components/MapCanvas.jsx` - Changed to infinite loop

## User Experience Impact
The continuous animation creates a **living, breathing interface** that:
- Naturally guides the eye along the route
- Keeps the interface feeling dynamic
- Reinforces the navigation path
- Creates a premium, polished feel
