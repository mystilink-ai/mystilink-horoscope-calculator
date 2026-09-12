import { spawn } from "node:child_process";
import {
  buildDailyArgs,
  buildMonthlyArgs,
  buildNatalArgs,
  runWith,
} from "./shared.js";

export function resolveCli() {
  const env = process.env.MYSTILINK_HOROSCOPE_CLI;
  return env && env.trim() ? env.trim() : "mystilink-horoscope";
}

export function createNodeRunner(cliPath = resolveCli()) {
  return function runCli(args) {
    return new Promise((resolve, reject) => {
      const child = spawn(cliPath, args, { stdio: ["ignore", "pipe", "pipe"] });
      let stdout = "";
      let stderr = "";
      child.stdout.setEncoding("utf8");
      child.stderr.setEncoding("utf8");
      child.stdout.on("data", (chunk) => {
        stdout += chunk;
      });
      child.stderr.on("data", (chunk) => {
        stderr += chunk;
      });
      child.on("error", reject);
      child.on("close", (code) => {
        if (code === 0) {
          resolve(stdout);
        } else {
          reject(new Error(stderr || stdout || `CLI exited with ${code}`));
        }
      });
    });
  };
}

const defaultRunner = createNodeRunner();

export async function run(args) {
  return runWith(defaultRunner, args);
}

export async function version() {
  return run(["version"]);
}

export async function natal(options) {
  return run(buildNatalArgs(options));
}

export async function daily(options) {
  return run(buildDailyArgs(options));
}

export async function monthly(options) {
  return run(buildMonthlyArgs(options));
}

export { buildDailyArgs, buildMonthlyArgs, buildNatalArgs };
