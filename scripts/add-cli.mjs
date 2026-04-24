import { execFileSync } from "node:child_process";

const spec = process.env.npm_config_pkg;

if (!spec) {
  console.error("Usage:");
  console.error("  npm run -s add-cli --pkg=foo@1.2.3");
  console.error("  npm run -s add-cli --pkg=@scope/foo@1.2.3");
  process.exit(2);
}

function packageNameFromSpec(spec) {
  if (spec.includes("@npm:")) {
    return spec.slice(0, spec.indexOf("@npm:"));
  }

  if (spec.startsWith("@")) {
    const versionAt = spec.indexOf("@", 1);
    return versionAt === -1 ? spec : spec.slice(0, versionAt);
  }

  const versionAt = spec.indexOf("@");
  return versionAt === -1 ? spec : spec.slice(0, versionAt);
}

const name = packageNameFromSpec(spec);
const scriptValue = `npm exec --offline --no -- ${name}`;

execFileSync("npm", ["i", "-E", spec], { stdio: "inherit" });

execFileSync("npm", ["pkg", "set", `scripts[${name}]=${scriptValue}`], {
  stdio: "inherit",
});

console.log(`added script: ${name} -> ${scriptValue}`);
