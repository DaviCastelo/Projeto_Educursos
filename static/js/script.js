const passwordField = document.getElementById("password");
const confirmPasswordField = document.getElementById("confirm_password");
const togglePassword = document.querySelectorAll(".password-toggle-icon i");

togglePassword.forEach((toggle, index) => {
  toggle.addEventListener("click", function () {
    const passwordInput = index === 0 ? passwordField : confirmPasswordField;
    if (passwordInput.type === "password") {
      passwordInput.type = "text";
      toggle.classList.remove("fa-eye");
      toggle.classList.add("fa-eye-slash");
    } else {
      passwordInput.type = "password";
      toggle.classList.remove("fa-eye-slash");
      toggle.classList.add("fa-eye");
    }
  });
});
