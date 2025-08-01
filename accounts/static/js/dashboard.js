document.addEventListener("DOMContentLoaded", () => {
    const toggleEditBtn = document.getElementById("toggle-edit-btn");
    const editProfileForm = document.getElementById("edit-profile-form");
    const profileForm = document.getElementById("profileForm");
    const userFirstName = document.getElementById("user-first-name");
    const avatarImg = document.getElementById("avatar-img");

    if (toggleEditBtn && editProfileForm) {
        toggleEditBtn.addEventListener("click", () => {
            editProfileForm.classList.toggle("hidden");
        });
    }

    if (profileForm) {
        profileForm.addEventListener("submit", function (e) {
            e.preventDefault();
            const formData = new FormData(profileForm);
            const csrfToken = profileForm.querySelector('[name=csrfmiddlewaretoken]').value;

            fetch("{% url 'accounts:update_profile' %}", {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrfToken
                },
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                if (data.status === "success") {
                    if (userFirstName) userFirstName.innerText = data.first_name || data.username;
                    if (avatarImg && data.avatar_url) avatarImg.src = data.avatar_url;
                    alert("✅ Profile updated successfully!");
                } else {
                    alert("⚠️ Profile update failed.");
                }
            });
        });
    }
});
