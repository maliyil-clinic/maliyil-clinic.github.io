document.addEventListener("DOMContentLoaded", function () {

  /* =========================
     1. MOBILE MENU TOGGLE
  ========================= */
  const toggle = document.getElementById("menu-toggle");
  const nav = document.getElementById("nav-menu");
  const navLinks = document.querySelectorAll(".nav a");

  // Toggle menu open/close
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      nav.classList.toggle("active");
    });
  }

  // Close menu when a navigation link is clicked
  if (navLinks.length > 0) {
    navLinks.forEach(function (link) {
      link.addEventListener("click", function () {
        nav.classList.remove("active");
      });
    });
  }

  /* =========================
     2. WHATSAPP DOCTOR APPOINTMENT SLOTS
  ========================= */
  const slots = document.querySelectorAll(".slot-btn");

  if (slots.length > 0) {
    slots.forEach(function (slot) {
      slot.addEventListener("click", function (e) {
        let dateInput = document.getElementById("appointmentDate");

        // Ensure the date input exists on the page
        if (!dateInput) return;

        let date = dateInput.value;

        // Force user to pick a date first
        if (!date) {
          alert("Please select an appointment date first.");
          e.preventDefault();
          return;
        }

        let time = this.innerText;
        let message = "Hello Doctor,%0A" +
          "Name:%20_____%0A" +
          "Date:%20" + date + "%0A" +
          "Preferred Time:%20" + time + "%0A" +
          "Please confirm my appointment.";

        // Set the link dynamically before it redirects
        this.href = "https://wa.me/919447039929?text=" + message;
      });
    });
  }
});

/* =========================
   3. WHATSAPP BOOKING FORM FUNCTION 
========================= */
function sendToWhatsApp(event) {
  event.preventDefault(); // Prevents page from refreshing

  // Fetching form details (with fallbacks if fields are missing)
  const service = document.getElementById('bookService') ? document.getElementById('bookService').value : 'Not Specified';
  const name = document.getElementById('bookName') ? document.getElementById('bookName').value : 'Not Specified';
  const phone = document.getElementById('bookPhone') ? document.getElementById('bookPhone').value : 'Not Specified';
  const date = document.getElementById('bookDate') ? document.getElementById('bookDate').value : 'Not Specified';
  const time = document.getElementById('bookTime') ? document.getElementById('bookTime').value : 'Not Specified';
  const message = document.getElementById('bookMessage') ? document.getElementById('bookMessage').value : '';

  const clinicNumber = "919447039929"; // Maliyil Medical Centre Number

  // Formatting the WhatsApp Message
  let whatsappMessage = `*New Appointment Request*%0A%0A`;
  whatsappMessage += `*Service:* ${service}%0A`;
  whatsappMessage += `*Patient Name:* ${name}%0A`;
  whatsappMessage += `*Contact:* ${phone}%0A`;
  whatsappMessage += `*Date:* ${date}%0A`;
  whatsappMessage += `*Time:* ${time}%0A`;

  if (message.trim() !== "") {
    whatsappMessage += `*Details:* ${message}%0A`;
  }

  // Redirecting to WhatsApp
  const whatsappURL = `https://wa.me/${clinicNumber}?text=${whatsappMessage}`;
  window.open(whatsappURL, '_blank');
}