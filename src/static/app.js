document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Utility to escape HTML
  function escapeHtml(text) {
    const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };
    return String(text).replace(/[&<>"']/g, (m) => map[m]);
  }

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message and reset select
      activitiesList.innerHTML = "";
      activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const participants = details.participants || [];
        const spotsLeft = (details.max_participants || 0) - participants.length;

        // Build participants HTML
        let participantsHtml = "";
        if (participants.length > 0) {
          participantsHtml = `
            <div class="participants">
              <h5>Participants</h5>
              <ul>
                ${participants.map(p => `
                  <li class="participant-item" data-activity="${escapeHtml(name)}" data-email="${escapeHtml(p)}">
                    <span class="participant-email">${escapeHtml(p)}</span>
                    <button class="delete-participant" aria-label="Remove ${escapeHtml(p)}" title="Remove participant">×</button>
                  </li>
                `).join("")}
              </ul>
            </div>
          `;
        } else {
          participantsHtml = `<p class="no-participants">No participants yet — be the first to sign up!</p>`;
        }

        activityCard.innerHTML = `
          <h4>${escapeHtml(name)}</h4>
          <p>${escapeHtml(details.description || "")}</p>
          <p><strong>Schedule:</strong> ${escapeHtml(details.schedule || "TBD")}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          ${participantsHtml}
        `;

        activitiesList.appendChild(activityCard);

        // Add delete handlers
        activityCard.querySelectorAll(".delete-participant").forEach(btn => {
          btn.addEventListener("click", async (e) => {
            e.preventDefault();
            const li = btn.closest(".participant-item");
            const activity = li.dataset.activity;
            const email = li.dataset.email;

            try {
              const response = await fetch(
                `/activities/${encodeURIComponent(activity)}/participants/${encodeURIComponent(email)}`,
                { method: "DELETE" }
              );

              if (response.ok) {
                // Refresh activities to show updated participants
                fetchActivities();
              } else {
                const error = await response.json();
                alert(`Failed to remove participant: ${error.detail || "Unknown error"}`);
              }
            } catch (error) {
              console.error("Error removing participant:", error);
              alert("Failed to remove participant. Please try again.");
            }
          });
        });

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value.trim();
    const activity = document.getElementById("activity").value;

    if (!email || !activity) {
      messageDiv.textContent = "Please provide an email and select an activity.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      setTimeout(() => messageDiv.classList.add("hidden"), 5000);
      return;
    }

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message || "Signed up successfully.";
        messageDiv.className = "success";
        signupForm.reset();
        // Refresh activities to show the new participant
        fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
