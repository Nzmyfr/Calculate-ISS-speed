# Quick Reference - Code Improvements

## 🎯 At a Glance

### Current Code Has:
- ✅ Functional ISS tracking
- ✅ Sensor data collection
- ✅ CSV output
- ❌ No logging
- ❌ Global variables
- ❌ Basic error handling
- ❌ No type hints

### What Should Be Fixed:
1. **Critical (5 min)** - Remove unused imports, fix typo, move start_time
2. **High (20 min)** - Add Config class, organize imports
3. **Medium (1-2 hours)** - Add logging, error handling, refactor functions
4. **Nice-to-have (2+ hours)** - Full class refactor, comprehensive docs

---

## 🔧 Quick Fix Commands

### 1. Remove Unused Import
**Find:** Line 3 in main.py
```python
from numpy import imag  # DELETE THIS LINE
```

### 2. Fix Typo
**Find & Replace:**
```
last_postion  →  last_position
```
(Appears ~10 times in file)

### 3. Move start_time
**Find:** Line 4
```python
start_time = datetime.now()  # Move this...
```
**Move to:** Inside main() function

### 4. Fix time_delta Comment
**Find:** Line 124
```python
time_delta = 0.5 #10 #minutes  # Confusing!
```
**Change to:**
```python
time_delta = 0.5  # Change from 0.5 to 10 minutes if needed
```

---

## 📝 Add Config Class (2 minutes)

Insert at top of file, after imports:

```python
class Config:
    """Configuration constants"""
    SENSE_HAT_GAIN = 60
    SENSE_HAT_INTEGRATION_CYCLES = 64
    PROGRAM_DURATION_MINUTES = 10
    EARTH_RADIUS_KM = 6371.0
    RESULT_FILE = 'result.txt'
    DATA_CSV_FILE = 'data.csv'
```

Then replace hardcoded values:
```python
# Before:
sense.color.gain = 60
sense.color.integration_cycles = 64

# After:
sense.color.gain = Config.SENSE_HAT_GAIN
sense.color.integration_cycles = Config.SENSE_HAT_INTEGRATION_CYCLES
```

---

## 🔍 Add Basic Logging (3 minutes)

Add after imports:
```python
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
```

Replace prints:
```python
# Before:
print(f'The calculated speed is {ISS_speed}')

# After:
logger.info(f'The calculated speed is {ISS_speed}')
```

---

## 🛡️ Add Type Hints (5 minutes)

Add hints to function signatures:

```python
# Before:
def get_time(image):
    return time

# After:
from typing import Optional
from datetime import datetime

def get_time(image: str) -> datetime:
    return time
```

---

## ✍️ Add Docstrings (10 minutes)

```python
def calculate_speed(iss, time_scale, cam, time_1, position_1) -> tuple:
    """
    Calculate ISS speed between two observations.
    
    Args:
        iss: ISS object from astro_pi_orbit
        time_scale: Skyfield timescale
        cam: Camera object
        time_1: First observation time
        position_1: First ISS position
    
    Returns:
        Tuple of (speed, time_2, position_2)
    """
    # ... function code ...
```

---

## 🔐 Add Error Handling

### Before:
```python
def calculate_speed(iss, time_scale, cam, time_1, position_1):
    image_index += 1
    image_filename = f'Photo{image_index}.jpg'
    cam.take_photo(image_filename)  # Can fail!
    time_2 = get_time(image_filename)
    # ...
```

### After:
```python
def calculate_speed(iss, time_scale, cam, time_1, position_1):
    try:
        image_index += 1
        image_filename = f'Photo{image_index}.jpg'
        cam.take_photo(image_filename)
        time_2 = get_time(image_filename)
        
        time_difference = (time_2 - time_1).total_seconds()
        if time_difference <= 0:
            logger.warning(f'Invalid time difference: {time_difference}')
            return None, None, None
        
        # ... rest of code ...
        return speed, time_2, position_2
    
    except FileNotFoundError as e:
        logger.error(f'Photo file not found: {e}')
        return None, None, None
    except Exception as e:
        logger.error(f'Error calculating speed: {e}')
        return None, None, None
```

---

## 📊 Priority Matrix

```
┌─────────────────────────────────┐
│ Impact / Effort                 │
├─────────────────────────────────┤
│ HIGH │   Config + Logging       │
│      │   Remove unused imports  │
│ MED  │   Fix typo               │
│      │   Add error handling     │
│ LOW  │   Formatting             │
│      │   Add docstrings         │
└──────────────────────────────────
  LOW          EFFORT          HIGH
```

**Focus on:** High Impact / Low Effort items first

---

## ⏱️ Time Breakdown

| Task | Time | Impact |
|------|------|--------|
| Remove unused code | 2 min | Low |
| Fix typo | 2 min | Low |
| Config class | 3 min | High |
| Add logging | 3 min | High |
| Add type hints | 5 min | Medium |
| Add docstrings | 10 min | Medium |
| Error handling | 15 min | High |
| Refactor functions | 60 min | High |
| **TOTAL** | **100 min** | **Excellent** |

---

## ✅ Checklist: Quick Improvements

### Must Do (10 minutes)
- [ ] Delete `from numpy import imag`
- [ ] Delete or move `start_time = datetime.now()` 
- [ ] Find & replace `last_postion` with `last_position`
- [ ] Add Config class (copy from above)

### Should Do (20 minutes)
- [ ] Add logging setup (copy from above)
- [ ] Replace print() with logger calls
- [ ] Add docstrings to main functions

### Nice to Have (30+ minutes)
- [ ] Add type hints
- [ ] Add error handling
- [ ] Refactor get_sense_data()
- [ ] Use classes (ISS_SpeedTracker, SensorCollector)

---

## 📚 Reference Links in This Project

All files in: `c:\Users\vesel\OneDrive\Documents\project\Calculate-ISS-speed\`

1. **CODE_ANALYSIS_AND_IMPROVEMENTS.md** - Full detailed analysis (15 issues)
2. **CODE_ANALYSIS_SUMMARY.md** - Executive summary
3. **main_refactored.py** - Complete refactored version
4. **BEFORE_AND_AFTER_COMPARISON.md** - Side-by-side examples
5. **QUICK_REFERENCE_FIXES.md** - This file

---

## 🎓 Key Takeaways

### Don't Do:
```python
# ❌ Global mutable state
image_index = 1
def foo():
    global image_index
    image_index += 1

# ❌ Bare print() statements
print("Error!")

# ❌ Magic numbers
altitude_km = distance.km - 6371.0

# ❌ No error handling
data = dict[key]  # What if key doesn't exist?
```

### Do This Instead:
```python
# ✅ Use classes for state
class Tracker:
    def __init__(self):
        self.image_index = 1

# ✅ Use logging
logger.error("Error!")

# ✅ Use constants
altitude_km = distance.km - Config.EARTH_RADIUS_KM

# ✅ Handle errors
value = dict.get(key, default)
```

---

## 🚀 Getting Started

### Recommended Path for You:

1. **Day 1 (10 min):** Apply critical fixes
   - Remove unused import
   - Fix typo
   - Move start_time

2. **Day 2 (20 min):** Add Config & logging
   - Copy Config class
   - Add logging setup
   - Replace print() calls

3. **Day 3+ (Optional):** Full refactor
   - Use main_refactored.py as guide
   - Test thoroughly
   - Deploy improved version

---

## 💡 Pro Tips

1. **Use IDE Features:**
   - Find & Replace all `last_postion` instances at once
   - IDE autocomplete with type hints
   - IDE refactoring tools for renaming

2. **Test After Each Change:**
   - Make one change
   - Run the program
   - Verify it works
   - Commit to git

3. **Use Version Control:**
   ```bash
   git add main.py
   git commit -m "Fix: Remove unused import and fix typo"
   git commit -m "Improve: Add Config class and logging"
   ```

4. **Gradual Refactor:**
   - Don't try to fix everything at once
   - One function at a time
   - Test after each refactor

---

## ❓ FAQ

**Q: Should I use the refactored version or make incremental changes?**
A: Use the refactored version as a *reference guide*, make incremental changes to existing code. This is safer and easier to debug.

**Q: How do I test these changes?**
A: Run your program with test data. If it still works, the change was good. Add assertions for critical paths.

**Q: Will these changes break anything?**
A: No, if you follow the refactoring carefully. They only improve the code structure, not functionality.

**Q: Where's the best place to start?**
A: **Config class.** It requires minimal changes but makes the code immediately clearer.

---

## 📞 Questions?

Refer to the detailed documents:
- For "why" → CODE_ANALYSIS_AND_IMPROVEMENTS.md
- For "how" → BEFORE_AND_AFTER_COMPARISON.md
- For "what" → main_refactored.py
- For "summary" → CODE_ANALYSIS_SUMMARY.md

