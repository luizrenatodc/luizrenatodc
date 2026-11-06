// Grava o site real (luizrenato.dev) quadro a quadro para o GIF do perfil.
import puppeteer from "puppeteer-core";
import fs from "node:fs";
const b = await puppeteer.launch({ executablePath: "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe", headless: "new", args: ["--use-angle=swiftshader", "--enable-webgl", "--ignore-gpu-blocklist", "--hide-scrollbars"] });
const p = await b.newPage();
await p.setViewport({ width: 1280, height: 720 });
await p.goto("https://www.luizrenato.dev", { waitUntil: "networkidle2", timeout: 60000 });
await new Promise((r) => setTimeout(r, 6000));
const vai = (y) => p.evaluate((y) => window.scrollTo({ top: y, behavior: "instant" }), y);
// passada de aquecimento: carrega imagens e dispara as entradas
const total = await p.evaluate(() => document.documentElement.scrollHeight);
for (let y = 0; y < total; y += 500) { await vai(y); await new Promise((r) => setTimeout(r, 180)); }
await vai(0);
await new Promise((r) => setTimeout(r, 1500));
const paradas = [[0, 13], [760, 7], [3650, 7], [6250, 8], [9400, 8], [13500, 8], [16300, 7], [18330, 12]];
fs.rmSync("tmp/gif", { recursive: true, force: true });
fs.mkdirSync("tmp/gif", { recursive: true });
let n = 0;
const foto = async () => { await p.screenshot({ path: `tmp/gif/${String(n++).padStart(4, "0")}.jpg`, type: "jpeg", quality: 88 }); };
const suave = (t) => t * t * (3 - 2 * t);
for (let i = 0; i < paradas.length; i++) {
  const [y, fica] = paradas[i];
  for (let k = 0; k < fica; k++) await foto();
  if (i + 1 < paradas.length) {
    const alvo = paradas[i + 1][0], passos = 9;
    for (let k = 1; k <= passos; k++) { await vai(y + (alvo - y) * suave(k / passos)); await new Promise((r) => setTimeout(r, 60)); await foto(); }
  }
}
console.log("quadros", n);
await b.close();
