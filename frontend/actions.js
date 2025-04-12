export async function executeAction(parsedCommand) {
  const { action, courseCode, moduleNumber } = parsedCommand;

  if (courseCode) {
    const cards = document.querySelectorAll("a[href*='/d2l/home/']");
    let matchedCard = [...cards].find(card =>
      card.textContent.toUpperCase().includes(courseCode)
    );
    if (matchedCard) {
      matchedCard.click();
      return;
    }
  }

  if (action === "goToContent") {
    const contentLink = document.querySelector("a[href*='/content/']");
    if (contentLink) {
      contentLink.click();
      return;
    }
  }

  if (action === "goToGrades") {
    const gradesLink = document.querySelector("a[href*='/grades/']");
    if (gradesLink) {
      gradesLink.click();
      return;
    }
  }

  if (action === "goToAssignments") {
    const assignmentsLink = document.querySelector("a[href*='/dropbox/']");
    if (assignmentsLink) {
      assignmentsLink.click();
      return;
    }
  }

  if (action === "goToDiscussions") {
    const discussionsLink = document.querySelector("a[href*='/discussions/']");
    if (discussionsLink) {
      discussionsLink.click();
      return;
    }
  }

  if (moduleNumber) {
    const modules = document.querySelectorAll("h2, h3, span");
    for (const el of modules) {
      if (el.textContent.toLowerCase().includes("module " + moduleNumber)) {
        el.scrollIntoView({ behavior: "smooth", block: "center" });
        el.style.backgroundColor = "#fffbcc";
        return;
      }
    }
  }

  console.log("No matching action executed.");
}