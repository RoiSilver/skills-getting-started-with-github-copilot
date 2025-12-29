document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageEl = document.getElementById("message");

  function showMessage(text, type = "info") {
    messageEl.textContent = text;
    messageEl.className = `message ${type}`;
    setTimeout(() => messageEl.classList.add("hidden"), 4000);
  }

  function clearMessage() {
    messageEl.textContent = "";
    messageEl.className = "hidden";
  }

  function renderActivities(data) {
    activitiesList.innerHTML = "";
    // populate select
    activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';

    Object.entries(data).forEach(([name, info]) => {
      // option for select
      const opt = document.createElement("option");
      opt.value = name;
      opt.textContent = name;
      activitySelect.appendChild(opt);

      // card
      const card = document.createElement("div");
      card.className = "activity-card";

      const title = document.createElement("h4");
      title.textContent = name;
      card.appendChild(title);

      const desc = document.createElement("p");
      desc.textContent = info.description;
      card.appendChild(desc);

      const schedule = document.createElement("p");
      schedule.innerHTML = `<strong>Schedule:</strong> ${info.schedule}`;
      card.appendChild(schedule);

      const slots = document.createElement("p");
      const remaining = Math.max(0, info.max_participants - info.participants.length);
      slots.innerHTML = `<strong>Slots:</strong> ${info.participants.length} / ${info.max_participants} (${remaining} left)`;
      card.appendChild(slots);

      // participants section
      const participantsWrap = document.createElement("div");
      participantsWrap.className = "participants";

      const pHeader = document.createElement("h5");
      pHeader.textContent = "Participants";
      participantsWrap.appendChild(pHeader);

      if (info.participants && info.participants.length) {
        const ul = document.createElement("ul");
        ul.className = "participants-list";
        info.participants.forEach((email) => {
          const li = document.createElement("li");
          
          const span = document.createElement("span");
          span.textContent = email;
          li.appendChild(span);
          
          const deleteBtn = document.createElement("button");
          deleteBtn.className = "delete-participant";
          deleteBtn.textContent = "×";
          deleteBtn.title = `Remove ${email} from ${name}`;
          deleteBtn.addEventListener("click", async (e) => {
            e.preventDefault();
            try {
              const res = await fetch(`/activities/${encodeURIComponent(name)}/unregister?email=${encodeURIComponent(email)}`, { method: "POST" });
              if (res.ok) {
                showMessage(`${email} removed from ${name}`, "success");
                await fetchAndRender();
              } else {
                const err = await res.json().catch(() => ({}));
                showMessage(err.detail || "Failed to remove participant.", "error");
              }
            } catch (err) {
              showMessage(err.message || "Network error.", "error");
            }
          });
          li.appendChild(deleteBtn);
          
          ul.appendChild(li);
        });
        participantsWrap.appendChild(ul);
      } else {
        const none = document.createElement("p");
        none.className = "info";
        none.textContent = "No participants yet.";
        participantsWrap.appendChild(none);
      }

      card.appendChild(participantsWrap);
      activitiesList.appendChild(card);
    });
  }

  async function fetchAndRender() {
    clearMessage();
    try {
      const res = await fetch("/activities");
      if (!res.ok) throw new Error("Failed to load activities");
      const data = await res.json();
      renderActivities(data);
    } catch (err) {
      showMessage(err.message, "error");
    }
  }

  signupForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("email").value.trim();
    const activity = activitySelect.value;
    if (!email || !activity) {
      showMessage("Please provide an email and select an activity.", "error");
      return;
    }

    try {
      const url = `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`;
      const res = await fetch(url, { method: "POST" });
      if (res.ok) {
        const body = await res.json();
        showMessage(body.message || "Signed up successfully!", "success");
        signupForm.reset();
        await fetchAndRender();
      } else {
        const err = await res.json().catch(() => ({}));
        showMessage(err.detail || "Signup failed.", "error");
      }
    } catch (err) {
      showMessage(err.message || "Network error.", "error");
    }
  });

  // initial load
  fetchAndRender();
});
