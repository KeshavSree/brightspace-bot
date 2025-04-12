export async function parseCommand(command) {
  command = command.toLowerCase();

  const result = {
    action: null,
    courseCode: null,
    moduleNumber: null
  };

  const courseMatch = command.match(/cs\s?\d{3}/i);
  const moduleMatch = command.match(/module\s?(\d+)/i);

  if (command.includes("grades")) result.action = "goToGrades";
  else if (command.includes("content")) result.action = "goToContent";
  else if (command.includes("assignments")) result.action = "goToAssignments";
  else if (command.includes("discussions")) result.action = "goToDiscussions";
  else result.action = "unknown";

  if (courseMatch) result.courseCode = courseMatch[0].replace(/\s/g, '').toUpperCase();
  if (moduleMatch) result.moduleNumber = parseInt(moduleMatch[1]);

  return result;
}