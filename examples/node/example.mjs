import { daily, natal, version } from "../../bindings/js/src/node.js";

const birth = {
  datetime: "1990-06-15 14:30",
  timezone: "Asia/Shanghai",
  lat: 31.2304,
  lon: 121.4737,
};

const ver = await version();
process.stdout.write(ver);

const chart = await natal(birth);
process.stdout.write(chart);

const day = await daily({ ...birth, date: "2026-09-12" });
process.stdout.write(day);
