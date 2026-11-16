/* Progressive enhancements: inline editing, shortcuts, delete confirmation. */

(function () {
  "use strict";

  const addInput = document.getElementById("new-task");

  /* --- Inline editing ------------------------------------------------ */

  document.querySelectorAll(".edit-btn").forEach(function (button) {
    button.addEventListener("click", function () {
      const form = document.getElementById(button.dataset.target);
      if (!form) return;

      // Close any other open editors first.
      document.querySelectorAll(".edit-form").forEach(function (other) {
        if (other !== form) other.hidden = true;
      });

      form.hidden = !form.hidden;
      if (!form.hidden) {
        const input = form.querySelector('input[name="title"]');
        input.focus();
        input.setSelectionRange(input.value.length, input.value.length);
      }
    });
  });

  document.querySelectorAll("[data-cancel]").forEach(function (button) {
    button.addEventListener("click", function () {
      button.closest(".edit-form").hidden = true;
    });
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") {
      document.querySelectorAll(".edit-form:not([hidden])").forEach(function (form) {
        form.hidden = true;
      });
    }
  });

  /* --- Delete confirmation ------------------------------------------- */

  document.querySelectorAll(".delete-form").forEach(function (form) {
    form.addEventListener("submit", function (event) {
      const title = form
        .closest(".task")
        .querySelector(".task-title").textContent.trim();
      if (!window.confirm('Delete "' + title + '"?')) {
        event.preventDefault();
      }
    });
  });

  /* --- Keyboard shortcut: N or / focuses the add field ---------------- */

  document.addEventListener("keydown", function (event) {
    if (!addInput) return;

    const typing =
      event.target instanceof HTMLElement &&
      (event.target.matches("input, textarea, select") ||
        event.target.isContentEditable);

    if (typing || event.ctrlKey || event.metaKey || event.altKey) return;
    if (event.key === "n" || event.key === "N" || event.key === "/") {
      event.preventDefault();
      addInput.focus();
    }
  });
})();
