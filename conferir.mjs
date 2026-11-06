// Abre os SVGs como <img> (igual ao GitHub) e tira print em dois tempos para conferir a animação.
import puppeteer from "puppeteer-core";
import fs from "node:fs";
import path from "node:path";

const pasta = path.resolve("assets");
const so = process.argv.slice(2);
const arquivos = fs.readdirSync(pasta).filter((f) => f.endsWith(".svg") && !f.startsWith("btn-") && (!so.length || so.some((s) => f.includes(s))));
const b = await puppeteer.launch({ executablePath: "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe", headless: "new", args: ["--allow-file-access-from-files"] });
const p = await b.newPage();
await p.setViewport({ width: 1040, height: 700 });
fs.mkdirSync("tmp/prints", { recursive: true });
for (const f of arquivos) {
  const html = path.resolve("tmp/ver.html");
  fs.writeFileSync(html, `<body style="margin:20px;background:#0d1117"><img id=i src="file:///${pasta.replace(/\\/g, "/")}/${f}" style="width:1000px;display:block"></body>`);
  await p.goto("file:///" + html.replace(/\\/g, "/"));
  await p.waitForFunction(() => document.getElementById("i").complete);
  const h = await p.evaluate(() => document.getElementById("i").getBoundingClientRect().height);
  await p.setViewport({ width: 1040, height: Math.ceil(h) + 40 });
  await new Promise((r) => setTimeout(r, 3400));
  await p.screenshot({ path: `tmp/prints/${f.replace(".svg", "")}.png` });
}
await b.close();
console.log("ok", arquivos.length);
