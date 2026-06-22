# Maliyil Medical Centre - Booking System Project Documentation

This repository contains the source code for the Maliyil Medical Centre clinic website and its integrated online booking system. It is designed to be lightweight, secure, and mobile-friendly.

---

## 1. System Architecture

The project uses a two-tier architecture:
1. **Frontend (Static Website):** Built using semantic HTML5, vanilla CSS3, and modern JavaScript. It is hosted on GitHub Pages.
2. **Backend (Google Workspace Serverless):** Google Sheets acts as the database. A Google Apps Script Web App acts as a serverless JSON REST API to handle database queries (fetching booked slots, adding bookings, checking passwords, and processing cancellations) with concurrency locking.

```mermaid
graph TD
    subgraph Client-Side (GitHub Pages)
        User[Patient Booking Page]
        Staff[Staff Portal Dashboard]
    end

    subgraph Serverless Backend
        API[Google Apps Script Web App]
        DB[(Google Sheet Database)]
    end

    User -->|doGet / doPost JSON| API
    Staff -->|doGet / doPost JSON with Passcode| API
    API -->|Read/Write Rows| DB
```

---

## 2. File Directory Structure

* **`index.html`**: The home page of the website detailing clinic services, clinic info, and the "Find Us on Map" interactive section.
* **`services.html`**: Detailed list of clinic services offered.
* **`contact.html`**: The client-facing appointment booking page. Features real-time slot checking (disabling taken slots) and self-service booking/cancellation.
* **`staff-booking.html`**: Private mobile-responsive staff portal for front-office assistants to book walk-in/phone-in patients, view patient details, and cancel slots.
* **`style.css`**: Central stylesheet containing the visual design tokens, component classes, and responsive grids.
* **`script.js`**: Core site-wide JavaScript helper libraries.
* **`STAFF_GUIDE.md`**: Simplified user guide written for front office assistants.
* **`.github/workflows/deploy.yml`**: GitHub Actions automated pipeline to build and deploy code to dev and production URLs.

---

## 3. Environments Configuration

The system is split into two environments to allow testing changes safely:

| Environment | GitHub Branch | URL | Google Sheets Database |
| :--- | :--- | :--- | :--- |
| **Development (Dev)** | `dev` | `https://maliyil-clinic.github.io/dev/` | `Maliyil Clinic Bookings - DEV` |
| **Production (Prod)** | `main` | `https://maliyil-clinic.github.io/` | `Maliyil Clinic Bookings - PROD` |

---

## 4. Google Sheets Database & Security

### Google Sheet Tabs
Each environment's spreadsheet contains:
1. **Monthly Tabs (e.g., `2026-06`, `2026-07`):** The system automatically creates a tab for each month on the fly when a booking is made. The columns are:
   `Timestamp` | `Date` | `Time` | `Name` | `Phone` | `Service` | `Details` | `Status` | `BookedBy`
2. **`Config` Tab:** Stores settings. Cell **A2** (row 2, column 1, under header `StaffPassword`) contains the passcode used to log in to `staff-booking.html`.

### Staff Portal Authentication
1. To access patient names and numbers or to override/cancel slots, staff must enter the passcode.
2. The password is submitted server-side to Google Apps Script and verified against the `Config` tab.
3. If valid, the password is saved in the browser's `localStorage` to avoid repeating logins.

---

## 5. Deployment Git Workflow

GitHub Actions handles automated deployments. When code is pushed to GitHub, it is compiled and deployed.

### How to Make & Test Changes in Dev
1. **Switch to the Dev Branch:**
   ```bash
   git checkout dev
   ```
2. **Apply Your Changes:**
   Modify your HTML/CSS/JS files locally.
3. **Commit & Push to Dev:**
   ```bash
   git add .
   git commit -m "Describe your changes here"
   git push origin dev
   ```
4. **Verify on Dev:**
   Wait ~30 seconds and check `https://maliyil-clinic.github.io/dev/`.

### How to Promote Changes to Production (Prod)
Once dev has been fully verified and tested:
1. **Switch to the Main Branch:**
   ```bash
   git checkout main
   ```
2. **Merge the Dev Changes:**
   ```bash
   git merge dev
   ```
3. **Push to Main:**
   ```bash
   git push origin main
   ```
4. **Verify on Prod:**
   Wait ~30 seconds and check `https://maliyil-clinic.github.io/`.

---

## 6. Google Apps Script Backend Code

Below is the complete Apps Script code deployed inside both the DEV and PROD Google Sheets.

To set up a new environment or update the backend:
1. Open the Google Sheet, go to **Extensions** > **Apps Script**.
2. Paste the code below, replacing all existing code.
3. Click **Save**.
4. Click **Deploy** > **Manage deployments** > **Edit** > Select **New version** > Click **Deploy**.

```javascript
const COLUMNS = {
  TIMESTAMP: 1,
  DATE: 2,
  TIME: 3,
  NAME: 4,
  PHONE: 5,
  SERVICE: 6,
  DETAILS: 7,
  STATUS: 8,
  BOOKED_BY: 9
};

// Helper to verify the staff password against the Config tab
function verifyPassword(enteredPassword) {
  try {
    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const configSheet = ss.getSheetByName('Config');
    if (!configSheet) return false;
    const correctPassword = String(configSheet.getRange(2, 1).getValue()).trim();
    return enteredPassword === correctPassword;
  } catch (e) {
    return false;
  }
}

// Helper to check if a YYYY-MM-DD date is Sunday
function isDateSunday(dateStr) {
  try {
    const parts = dateStr.split('-');
    const d = new Date(Number(parts[0]), Number(parts[1]) - 1, Number(parts[2]));
    return d.getDay() === 0;
  } catch (e) {
    return false;
  }
}

function doGet(e) {
  try {
    const action = e.parameter.action;
    const date = e.parameter.date; // Format: YYYY-MM-DD
    const isStaff = e.parameter.staff === 'true';
    const password = e.parameter.password;
    
    if (!date) throw new Error('Date parameter is required.');
    
    // Security check: Only staff with a valid password can request detailed bookings
    if (isStaff && !verifyPassword(password)) {
      return createJsonResponse({ status: 'error', message: 'Unauthorized access.' });
    }
    
    // Check if Sunday
    if (isDateSunday(date)) {
      return createJsonResponse({ status: 'success', isSunday: true });
    }
    
    const sheet = getOrCreateMonthlySheet(date);
    const data = sheet.getDataRange().getValues();
    const results = [];
    let isDoctorOff = false;
    let doctorOffReason = '';
    
    // First, scan for a Full Day block
    for (let i = 1; i < data.length; i++) {
      const rowDate = formatDate(data[i][COLUMNS.DATE - 1]);
      const rowStatus = data[i][COLUMNS.STATUS - 1];
      const rowTime = formatTime(data[i][COLUMNS.TIME - 1]);
      const rowName = data[i][COLUMNS.NAME - 1];
      
      if (rowDate === date && rowStatus !== 'Cancelled') {
        if (rowTime === 'Full Day' && rowName === 'Doctor Off') {
          isDoctorOff = true;
          doctorOffReason = data[i][COLUMNS.DETAILS - 1] || 'Doctor is off-duty today.';
          break;
        }
      }
    }
    
    if (isDoctorOff) {
      return createJsonResponse({ status: 'success', doctorOff: true, reason: doctorOffReason });
    }
    
    // If not off for full day, compile normal list
    for (let i = 1; i < data.length; i++) {
      const rowDate = formatDate(data[i][COLUMNS.DATE - 1]);
      const rowStatus = data[i][COLUMNS.STATUS - 1];
      
      if (rowDate === date && rowStatus !== 'Cancelled') {
        const rowTime = formatTime(data[i][COLUMNS.TIME - 1]);
        if (isStaff) {
          // Staff gets full details of booked slots
          results.push({
            time: rowTime,
            name: data[i][COLUMNS.NAME - 1],
            phone: data[i][COLUMNS.PHONE - 1],
            service: data[i][COLUMNS.SERVICE - 1],
            details: data[i][COLUMNS.DETAILS - 1],
            bookedBy: data[i][COLUMNS.BOOKED_BY - 1]
          });
        } else {
          // Patients only see which time slots are taken
          results.push(rowTime);
        }
      }
    }
    return createJsonResponse({ status: 'success', data: results });
  } catch (err) {
    return createJsonResponse({ status: 'error', message: err.toString() });
  }
}

function doPost(e) {
  const lock = LockService.getScriptLock();
  try {
    lock.waitLock(30000); // 30s lock to prevent race conditions
    
    const params = JSON.parse(e.postData.contents);
    const action = params.action;
    const date = params.date;
    const password = params.password;
    
    if (action === 'verify') {
      const isValid = verifyPassword(password);
      return createJsonResponse({ status: 'success', authorized: isValid });
    }
    
    if (!date) throw new Error('Date is required.');
    
    // Check if Sunday
    if (isDateSunday(date)) {
      throw new Error('Appointments cannot be scheduled on Sundays.');
    }
    
    const sheet = getOrCreateMonthlySheet(date);
    
    // 1. setDoctorOff Action
    if (action === 'setDoctorOff') {
      if (!verifyPassword(password)) throw new Error('Unauthorized.');
      const time = params.time || 'Full Day';
      const reason = params.reason || '';
      
      // Ensure slot is still free
      const data = sheet.getDataRange().getValues();
      for (let i = 1; i < data.length; i++) {
        const rowDate = formatDate(data[i][COLUMNS.DATE - 1]);
        const rowTime = formatTime(data[i][COLUMNS.TIME - 1]);
        const rowStatus = data[i][COLUMNS.STATUS - 1];
        
        if (rowDate === date && rowTime === time && rowStatus !== 'Cancelled') {
          throw new Error('This slot/day is already blocked or booked.');
        }
      }
      
      sheet.appendRow([new Date(), date, time, 'Doctor Off', 'N/A', 'Doctor Off-Duty', reason, 'Confirmed', 'Staff']);
      return createJsonResponse({ status: 'success' });
    }
    
    // 2. cancelDoctorOff Action
    if (action === 'cancelDoctorOff') {
      if (!verifyPassword(password)) throw new Error('Unauthorized.');
      const time = params.time || 'Full Day';
      
      const data = sheet.getDataRange().getValues();
      let updated = false;
      
      for (let i = 1; i < data.length; i++) {
        const rowDate = formatDate(data[i][COLUMNS.DATE - 1]);
        const rowTime = formatTime(data[i][COLUMNS.TIME - 1]);
        const rowName = data[i][COLUMNS.NAME - 1];
        const rowService = data[i][COLUMNS.SERVICE - 1];
        const rowStatus = data[i][COLUMNS.STATUS - 1];
        
        if (rowDate === date && rowTime === time && rowName === 'Doctor Off' && rowService === 'Doctor Off-Duty' && rowStatus !== 'Cancelled') {
          sheet.getRange(i + 1, COLUMNS.STATUS).setValue('Cancelled');
          updated = true;
          break;
        }
      }
      
      if (!updated) throw new Error('No active off-duty block found.');
      return createJsonResponse({ status: 'success' });
    }
    
    // 3. Booking
    if (action === 'book' || action === 'staffBook') {
      const time = params.time;
      const name = params.name;
      const phone = params.phone;
      const service = params.service || 'Doctor Consultancy';
      const details = params.details || '';
      
      let bookedBy = 'Patient';
      
      if (action === 'staffBook') {
        if (!verifyPassword(password)) throw new Error('Unauthorized.');
        bookedBy = 'Staff';
      }
      
      // Ensure slot is still free, and no Full Day off block is active
      const data = sheet.getDataRange().getValues();
      for (let i = 1; i < data.length; i++) {
        const rowDate = formatDate(data[i][COLUMNS.DATE - 1]);
        const rowTime = formatTime(data[i][COLUMNS.TIME - 1]);
        const rowStatus = data[i][COLUMNS.STATUS - 1];
        const rowName = data[i][COLUMNS.NAME - 1];
        
        if (rowDate === date && rowStatus !== 'Cancelled') {
          if (rowTime === 'Full Day' && rowName === 'Doctor Off') {
            throw new Error('Doctor is off-duty for the full day.');
          }
          if (rowTime === time) {
            throw new Error('This time slot is already booked or blocked.');
          }
        }
      }
      
      sheet.appendRow([new Date(), date, time, name, phone, service, details, 'Confirmed', bookedBy]);
      return createJsonResponse({ status: 'success' });
    }
    
    // 4. Cancellation
    if (action === 'cancel' || action === 'staffCancel') {
      const phone = String(params.phone).trim();
      const time = params.time;
      
      if (action === 'staffCancel' && !verifyPassword(password)) {
        throw new Error('Unauthorized.');
      }
      
      const data = sheet.getDataRange().getValues();
      let updated = false;
      
      for (let i = 1; i < data.length; i++) {
        const rowDate = formatDate(data[i][COLUMNS.DATE - 1]);
        const rowPhone = String(data[i][COLUMNS.PHONE - 1]).trim();
        const rowTime = formatTime(data[i][COLUMNS.TIME - 1]);
        const rowStatus = data[i][COLUMNS.STATUS - 1];
        
        // Match condition
        const matchesIdentity = action === 'staffCancel' || rowPhone.includes(phone);
        if (rowDate === date && rowTime === time && matchesIdentity && rowStatus !== 'Cancelled') {
          sheet.getRange(i + 1, COLUMNS.STATUS).setValue('Cancelled');
          updated = true;
          break;
        }
      }
      
      if (!updated) throw new Error('No matching active booking found.');
      return createJsonResponse({ status: 'success' });
    }
  } catch (err) {
    return createJsonResponse({ status: 'error', message: err.toString() });
  } finally {
    lock.releaseLock();
  }
}

// Helpers
function getOrCreateMonthlySheet(dateStr) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const dateParts = dateStr.split('-');
  const tabName = `${dateParts[0]}-${dateParts[1]}`; // e.g. "2026-06"
  
  let sheet = ss.getSheetByName(tabName);
  if (!sheet) {
    sheet = ss.insertSheet(tabName);
    sheet.appendRow([
      'Timestamp', 'Date', 'Time', 'Name', 'Phone', 'Service', 'Details', 'Status', 'BookedBy'
    ]);
    sheet.getRange("A1:I1").setFontWeight("bold").setBackground("#f3f3f3");
  }
  return sheet;
}

function formatDate(dateVal) {
  if (dateVal instanceof Date) {
    const tz = SpreadsheetApp.getActiveSpreadsheet().getSpreadsheetTimeZone();
    return Utilities.formatDate(dateVal, tz, 'yyyy-MM-dd');
  }
  return String(dateVal).trim();
}

function formatTime(timeVal) {
  if (timeVal instanceof Date) {
    const tz = SpreadsheetApp.getActiveSpreadsheet().getSpreadsheetTimeZone();
    return Utilities.formatDate(timeVal, tz, 'h:mm a');
  }
  return String(timeVal).trim();
}

function createJsonResponse(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}
```
