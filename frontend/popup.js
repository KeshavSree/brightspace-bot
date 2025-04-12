import { parseCommand } from './agent-core.js';

document.getElementById("runBtn").addEventListener("click", async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  const command = document.getElementById("commandInput").value;

  const parsedCommand = await parseCommand(command);

  chrome.scripting.executeScript({
    target: { tabId: tab.id },
    func: async (parsed) => {
      const module = await import(chrome.runtime.getURL("actions.js"));
      module.executeAction(parsed);
    },
    args: [parsedCommand]
  });
});