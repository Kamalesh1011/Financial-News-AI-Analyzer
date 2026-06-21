import { Packer } from 'docx';
import * as fs from 'fs';
import * as path from 'path';

export async function exportToDocx(doc: any, outputPath: string, filename: string): Promise<string> {
  const dir = path.dirname(outputPath);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }

  const buffer = await Packer.toBuffer(doc);
  const fullPath = path.join(outputPath, filename);
  fs.writeFileSync(fullPath, buffer);

  return fullPath;
}

export function ensureDir(dirPath: string): void {
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
  }
}
