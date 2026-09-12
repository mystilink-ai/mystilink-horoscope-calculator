/**
 * Shared helpers for mystilink-horoscope CLI bindings.
 * @param {string[]} args
 * @param {(args: string[]) => Promise<string> | string} runner
 */
export async function runWith(runner, args) {
  const out = await runner(args);
  return typeof out === "string" ? out : String(out);
}

export function buildNatalArgs(options) {
  const args = [
    "natal",
    "--datetime",
    options.datetime,
    "--timezone",
    options.timezone,
    "--lat",
    String(options.lat),
    "--lon",
    String(options.lon),
  ];
  if (options.houseSystem) {
    args.push("--house-system", options.houseSystem);
  }
  if (options.zodiac) {
    args.push("--zodiac", options.zodiac);
  }
  if (options.siderealMode) {
    args.push("--sidereal-mode", options.siderealMode);
  }
  if (options.trueSolarTime) {
    args.push("--true-solar-time");
  }
  if (options.noAspects) {
    args.push("--no-aspects");
  }
  return args;
}

export function buildDailyArgs(options) {
  const args = [
    "daily",
    "--datetime",
    options.datetime,
    "--timezone",
    options.timezone,
    "--lat",
    String(options.lat),
    "--lon",
    String(options.lon),
    "--date",
    options.date,
  ];
  if (options.houseSystem) {
    args.push("--house-system", options.houseSystem);
  }
  if (options.zodiac) {
    args.push("--zodiac", options.zodiac);
  }
  if (options.transitTime) {
    args.push("--transit-time", options.transitTime);
  }
  return args;
}

export function buildMonthlyArgs(options) {
  return [
    "monthly",
    "--datetime",
    options.datetime,
    "--timezone",
    options.timezone,
    "--lat",
    String(options.lat),
    "--lon",
    String(options.lon),
    "--year",
    String(options.year),
    "--month",
    String(options.month),
  ];
}
