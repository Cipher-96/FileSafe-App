document.addEventListener("DOMContentLoaded", () => {
  const forms = document.querySelectorAll("[data-conversion-form]");
  const dropZones = document.querySelectorAll(".drag-drop-zone");
  const fileInputs = document.querySelectorAll("input[type='file']");

  dropZones.forEach((dropZone) => {
    const form = dropZone.closest("form");
    const input = form?.querySelector('input[type="file"]');
    dropZone.addEventListener("click", () => input && input.click());
    dropZone.addEventListener("dragover", (event) => {
      event.preventDefault();
      dropZone.classList.add("dragover");
    });
    dropZone.addEventListener("dragleave", () => dropZone.classList.remove("dragover"));
    dropZone.addEventListener("drop", (event) => {
      event.preventDefault();
      dropZone.classList.remove("dragover");
      if (event.dataTransfer.files && event.dataTransfer.files.length) {
        input.files = event.dataTransfer.files;
        const label = dropZone.querySelector(".drop-file-name");
        if (label) label.textContent = event.dataTransfer.files[0].name;
      }
    });
  });

  fileInputs.forEach((input) => {
    input.addEventListener("change", () => {
      const form = input.closest("form");
      const label = form?.querySelector(".drop-file-name");
      if (input.files && input.files[0] && label) label.textContent = input.files[0].name;
    });
  });

  forms.forEach((form) => {
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const fileInput = form.querySelector('input[type="file"]');
      const source = form.querySelector('select[name="source"]')?.value || form.dataset.source || "";
      const target = form.querySelector('select[name="target"]')?.value || form.dataset.target || "";
      const progressWrap = form.querySelector(".progress-wrap");
      const progressFill = form.querySelector(".progress-fill");
      const statusText = form.querySelector(".status-text");
      const resultCard = form.querySelector(".result-card");
      const resultLink = form.querySelector("#download-link");

      if (!fileInput || !fileInput.files || !fileInput.files.length) {
        alert("Please select a file.");
        return;
      }

      const body = new FormData();
      body.append("file", fileInput.files[0]);
      body.append("source", source);
      body.append("target", target);
      if (progressWrap) progressWrap.style.display = "block";
      if (statusText) statusText.textContent = "Preparing secure upload...";
      if (progressFill) progressFill.style.width = "15%";

      try {
        const response = await fetch("/convert", { method: "POST", body });
        if (progressFill) progressFill.style.width = "55%";
        if (statusText) statusText.textContent = "Processing file securely...";
        if (!response.ok) {
          const data = await response.json().catch(() => ({}));
          throw new Error(data.error || "Conversion failed");
        }
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const name = fileInput.files[0].name.replace(/\.[^/.]+$/, "") + "." + target;
        if (resultLink) { resultLink.href = url; resultLink.download = name; resultLink.textContent = "Download converted file"; }
        if (resultCard) resultCard.style.display = "block";
        if (statusText) statusText.textContent = "Conversion complete. Your file is ready to download.";
        if (progressFill) progressFill.style.width = "100%";
      } catch (error) {
        if (statusText) statusText.textContent = error.message || "Something went wrong.";
        if (progressFill) progressFill.style.width = "0%";
      }
    });
  });
});
