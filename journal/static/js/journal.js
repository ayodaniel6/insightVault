document.addEventListener("DOMContentLoaded", function () {
  const modal = document.getElementById("note-modal");
  const form = document.getElementById("note-form");
  const noteIdField = document.getElementById("note-id");
  const modalTitle = document.getElementById("modal-title");

  // ---- Open modal for new note ----
  document.getElementById("new-entry-btn").addEventListener("click", () => {
    form.reset();
    noteIdField.value = "";
    modalTitle.innerText = "New Entry";
    modal.classList.remove("hidden");
    modal.classList.add("flex");
  });

  // ---- Edit note ----
  window.editNote = function (noteId) {
    fetch(`/journal/get/${noteId}/`, {
      headers: { "X-Requested-With": "XMLHttpRequest" }
    })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          const note = data.note;
          noteIdField.value = note.id;
          form.querySelector("[name=title]").value = note.title;
          form.querySelector("[name=content]").value = note.content;
          form.querySelector("[name=tags]").value = note.tags_list.join(", ");
          form.querySelector("[name=pinned]").checked = note.pinned;

          modalTitle.innerText = "Edit Entry";
          modal.classList.remove("hidden");
          modal.classList.add("flex");
        }
      });
  };

  // ---- Close modal ----
  window.closeModal = function () {
    modal.classList.add("hidden");
    modal.classList.remove("flex");
  };

  const saveNoteUrl = document.getElementById("new-entry-btn").dataset.saveUrl;

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    const formData = new FormData(form);

    fetch(saveNoteUrl, {
      method: "POST",
      body: formData,
      headers: { "X-Requested-With": "XMLHttpRequest" }
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        window.location.reload();
      } else {
        console.error(data.errors);
      }
    });
  });


  // ---- Delete note ----
  window.deleteNote = function (noteId) {
    if (!confirm("Are you sure you want to delete this note?")) return;

    fetch(`/journal/delete/${noteId}/`, {
      method: "POST",
      headers: {
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRFToken": getCookie("csrftoken")
      }
    })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          document.getElementById(`note-${noteId}`).remove();
        } else {
          console.error("Delete failed:", data.error);
        }
      });
  };

  // ---- Toggle pin ----
  window.togglePin = function (noteId) {
    fetch(`/journal/toggle-pin/${noteId}/`, {
      method: "POST",
      headers: {
        "X-Requested-With": "XMLHttpRequest",
        "X-CSRFToken": getCookie("csrftoken")
      }
    })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          window.location.reload();
        } else {
          console.error("Toggle pin failed:", data.error);
        }
      });
  };

  // ---- Expand/Collapse note content smoothly ----
  window.expandNote = function (noteId, event) {
    if (event.target.tagName === "BUTTON" || event.target.tagName === "A") return;

    const container = document.getElementById(`note-content-${noteId}`);
    const preview = container.querySelector(".note-preview");
    const full = container.querySelector(".note-full");

    if (full.style.maxHeight && full.style.maxHeight !== "0px") {
      // Collapse
      full.style.maxHeight = "0px";
      setTimeout(() => {
        full.classList.add("hidden");
        preview.classList.remove("hidden");
      }, 300);
    } else {
      // Expand
      preview.classList.add("hidden");
      full.classList.remove("hidden");
      full.style.maxHeight = full.scrollHeight + "px";
    }
  };

  // ---- Helper: Get CSRF token ----
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith(name + "=")) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
});
