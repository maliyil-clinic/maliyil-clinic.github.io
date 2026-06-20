# Maliyil Medical Centre - Booking System User Guide

This guide explains how to use and manage the clinic's online booking system. It is written for clinic managers, front office staff, and administrative assistants.

---

## 1. System Overview

The clinic booking system consists of three main parts:
1. **Customer Booking Page:** Where patients view open times, fill out their details, and send a WhatsApp confirmation.
2. **Staff Portal (Front Office Dashboard):** A mobile-friendly page for your staff to manage the daily schedule and record phone calls.
3. **Google Sheets Database:** Where all booking records are stored and organized automatically.

---

## 2. Managing Daily Bookings (Front Office Staff)

Your front office staff will use the **Staff Portal** on their mobile phones or desktop computers to manage bookings.

* **Staff Portal URL:** `https://maliyil-clinic.github.io/staff-booking.html`
* **Accessing the Portal:** 
  - The first time they open the page, they will be prompted to enter the **Staff Password**.
  - The browser will remember the password, so they won't have to type it again unless they log out.
  - *Shortcut:* You can save the link as an app icon on your phone's home screen for one-tap access.

### How to book a phone-in patient:
1. Open the Staff Portal and select the **Appointment Date** from the calendar.
2. You will see a list of time slots:
   - **Green Slots:** Available times.
   - **Red/Blue Slots:** Already booked.
3. Tap **"Book Slot"** on any green slot.
4. Enter the **Patient's Name**, **Phone Number**, and select the **Service** (Consultancy, Lab, or Pharmacy).
5. Click **Confirm Booking**. The slot will immediately turn red and be blocked on the public website.

### How to cancel a booking:
1. In the Staff Portal, find the booked slot (Red or Blue).
2. Tap the red **"Cancel Slot"** button.
3. Confirm the cancellation. The slot will instantly turn green and become available for other patients on the website.

---

## 3. How Patients Book & Cancel Online

### Booking:
1. Patients visit: `https://maliyil-clinic.github.io/contact.html`
2. They select a date and tap an available time slot.
3. They enter their name, phone number, and service in the popup form.
4. Once they click confirm, the slot is locked in your Google Sheet, and the page opens **WhatsApp** so they can send the booking message to your clinic phone.

### Cancelling:
1. Patients click the **"Cancel Appointment"** tab on your contact page.
2. They select the date, enter their WhatsApp number, select their booked slot, and click **"Request Cancellation"**.
3. The system automatically finds their booking in the Google Sheet and marks it as **"Cancelled"**.

---

## 4. Managing the Google Sheet Database

All bookings are stored in your Google Sheets account.

### Monthly Sheets (Tabs)
To prevent the spreadsheet from getting too cluttered, the system automatically creates a new tab for each month (e.g., `2026-06` for June, `2026-07` for July). 
* You do not need to create these tabs manually; the system creates them the first time a patient books a slot in a new month.

### Manual Changes in the Spreadsheet
As an administrator, you have full access to edit the Google Sheet directly:
* **Manual Bookings:** You can type a booking directly into a new row in the sheet. (Make sure you fill in the **Date**, **Time**, and set the **Status** column to `Confirmed`). The website will automatically detect it and block that slot.
* **Rescheduling:** If you need to change a patient's time, just type the new time in the **Time** column of their row.
* **Cancellations:** If you manually change a patient's **Status** cell from `Confirmed` to `Cancelled` in the sheet, that slot will instantly open up on the website.

---

## 5. Security & Changing the Password

The password that protects the Staff Portal is stored inside your Google Sheet:
1. Open your Google Sheet and click on the **`Config`** tab (at the bottom).
2. Look at cell **A2** (directly under the header `StaffPassword`).
3. Simply type your new password in cell **A2**.
4. **Done!** The Staff Portal will immediately start requiring the new password. Any staff members already logged in will be prompted to log in again with the new password.

---

## 6. Testing Changes (Dev vs Live)

To make sure you can test updates without messing up your real booking logs, the system runs in two separate environments:

* **Production (Live Clinic):**
  * Website: `https://maliyil-clinic.github.io/`
  * Spreadsheet: Connected to `Maliyil Clinic Bookings - PROD`
* **Development (Testing Area):**
  * Website: `https://maliyil-clinic.github.io/dev/`
  * Spreadsheet: Connected to `Maliyil Clinic Bookings - DEV` (use this sheet to run test bookings or play with features).
