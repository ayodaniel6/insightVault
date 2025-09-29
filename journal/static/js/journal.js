// journal.js

// Panel for creating new note
const createPanel = document.getElementById("createPanel");
const openCreatePanelBtn = document.getElementById("openCreatePanel");
const createNoteForm = document.getElementById("createNoteForm");

// Modal for delete confirmation
const deleteModal = document.getElementById("deleteModal");
const deleteForm = document.getElementById("deleteForm");


// ------------------ CREATE NOTE ------------------
openCreatePanelBtn.onclick = () => {
  createNoteForm.reset();
  openCreatePanel();
};

function openCreatePanel() {
  createPanel.classList.remove("translate-x-full");
}
function closeCreatePanel() {
  createPanel.classList.add("translate-x-full");
}

createNoteForm.onsubmit = async function (e) {
  e.preventDefault();
  let formData = new FormData(this);
  let res = await fetch("", {
    method: "POST",
    body: formData,
    headers: { "X-Requested-With": "XMLHttpRequest" },
  });

  if (res.ok) {
    location.reload(); // reload to reflect new note
  }
};


// ------------------ EXPAND / COLLAPSE ------------------
function toggleExpand(el) {
  const card = el.closest(".note-card");
  const preview = card.querySelector(".preview");
  const editForm = card.querySelector(".edit-form");

  preview.classList.toggle("hidden");
  editForm.classList.toggle("hidden");
}


// ------------------ EDIT NOTE ------------------
async function submitEdit(e, id) {
  e.preventDefault();
  let formData = new FormData(e.target);
  formData.append("note_id", id);

  let res = await fetch("", {
    method: "POST",
    body: formData,
    headers: { "X-Requested-With": "XMLHttpRequest" },
  });

  if (res.ok) {
    location.reload(); // reload to show updates
  }
}


// ------------------ DELETE NOTE ------------------
function confirmDelete(id) {
  deleteForm.onsubmit = async function (e) {
    e.preventDefault();
    let res = await fetch(`/journal/delete/${id}/`, {
      method: "POST",
      headers: {
        "X-CSRFToken": getCsrfToken(),
        "X-Requested-With": "XMLHttpRequest",
      },
    });
    if (res.ok) {
      location.reload(); // reload to update list
    } else {
      alert("Error while deleting note");
    }
  };
  openModal("deleteModal");
}


// ------------------ PIN NOTE ------------------
async function togglePin(id) {
  let res = await fetch(`/journal/pin/${id}/`, {
    method: "POST",
    headers: {
      "X-CSRFToken": getCsrfToken(),
      "X-Requested-With": "XMLHttpRequest",
    },
  });
  if (res.ok) {
    location.reload(); // reload so pinned goes to top
  }
}


// ------------------ HELPERS ------------------
function openModal(id) {
  document.getElementById(id).classList.remove("hidden");
}
function closeModal(id) {
  document.getElementById(id).classList.add("hidden");
}
function getCsrfToken() {
  return document.querySelector("[name=csrfmiddlewaretoken]").value;
}
