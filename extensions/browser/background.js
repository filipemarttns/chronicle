// Opt-in browser capture service worker skeleton.
// Navigation events are only forwarded when the user enables browser consent.

chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.local.set({ chronicleBrowserCaptureEnabled: false });
});

chrome.action.onClicked.addListener(async () => {
  const state = await chrome.storage.local.get("chronicleBrowserCaptureEnabled");
  const next = !state.chronicleBrowserCaptureEnabled;
  await chrome.storage.local.set({ chronicleBrowserCaptureEnabled: next });
});
