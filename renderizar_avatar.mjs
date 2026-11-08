// Renderiza assets/avatar-terror.svg em PNG 1024x1024 (o GitHub aceita PNG/JPG no avatar).
import puppeteer from "puppeteer-core";
import fs from "node:fs";
import path from "node:path";

const svg = path.resolve("assets/avatar-terror.svg");
const b = await puppeteer.launch({ executablePath: "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe", headless: "new", args: ["--allow-file-access-from-files"] });
const p = await b.newPage();
await p.setViewport({ width: 1024, height: 1024 });
await p.goto("file:///" + svg.replace(/\\/g, "/"));
await new Promise((r) => setTimeout(r, 800));
await p.screenshot({ path: "assets/avatar-terror.png" });
await b.close();
console.log("png ok", Math.round(fs.statSync("assets/avatar-terror.png").size / 1024) + " KB");
