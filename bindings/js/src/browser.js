/**
 * Browser entry: no process spawn. Provide a host runner that bridges to the
 * local mystilink-horoscope CLI (e.g. via a desktop shell or extension).
 */
import {
  buildDailyArgs,
  buildMonthlyArgs,
  buildNatalArgs,
  runWith,
} from "./shared.js";

/**
 * @param {{ run: (args: string[]) => Promise<string> | string }} options
 */
export function createClient(options) {
  if (!options || typeof options.run !== "function") {
    throw new Error(
      "Browser binding requires createClient({ run }) where run(args) invokes the local CLI."
    );
  }
  const runner = options.run;
  return {
    run: (args) => runWith(runner, args),
    version: () => runWith(runner, ["version"]),
    natal: (opts) => runWith(runner, buildNatalArgs(opts)),
    daily: (opts) => runWith(runner, buildDailyArgs(opts)),
    monthly: (opts) => runWith(runner, buildMonthlyArgs(opts)),
  };
}

export { buildDailyArgs, buildMonthlyArgs, buildNatalArgs };
