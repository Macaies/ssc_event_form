// static/js/form.js

// Select all steps and buttons
const steps = document.querySelectorAll(".form-step");
const nextBtns = document.querySelectorAll(".btn-next");
const prevBtns = document.querySelectorAll(".btn-prev");
const progressSteps = document.querySelectorAll(".progress-step");

let formStepIndex = 0; // Start at step 0

// Next button logic
nextBtns.forEach((btn) => {
  btn.addEventListener("click", () => {
    formStepIndex++;
    updateFormSteps();
    updateProgressbar();
  });
});

// Previous button logic
prevBtns.forEach((btn) => {
  btn.addEventListener("click", () => {
    formStepIndex--;
    updateFormSteps();
    updateProgressbar();
  });
});

// Show the active step
function updateFormSteps() {
  steps.forEach((step) => {
    step.classList.contains("active") && step.classList.remove("active");
  });
  steps[formStepIndex].classList.add("active");
}

// Update progress bar
function updateProgressbar() {
  progressSteps.forEach((step, idx) => {
    if (idx <= formStepIndex) {
      step.classList.add("active");
    } else {
      step.classList.remove("active");
    }
  });
}
