/**
 * Browser example: inject a host runner that calls the local CLI.
 * In a real host (desktop webview / extension), replace `hostRun` with the bridge.
 */
import { createClient } from "../../bindings/js/src/browser.js";

async function hostRun(args) {
  // Placeholder: browsers cannot spawn processes. Host apps must implement this.
  throw new Error(
    "Provide a host runner. Example args: " + JSON.stringify(args)
  );
}

const client = createClient({ run: hostRun });

// Demonstrates the API surface; will throw until a real host runner is injected.
client.version().catch((err) => {
  console.error(String(err.message || err));
});
