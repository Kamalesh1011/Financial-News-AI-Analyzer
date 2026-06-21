#!/usr/bin/env node

import * as fs from 'fs';
import * as path from 'path';
import { DocumentConfigSchema } from './config/schema.js';
import { DEFAULT_CONFIG } from './config/defaults.js';
import { buildDocument } from './utils/document.js';
import { exportToDocx } from './utils/export.js';

// ── CLI Argument Parsing ──

function parseArgs(): { configPath: string; outputPath?: string } {
  const args = process.argv.slice(2);
  let configPath = '';
  let outputPath: string | undefined;

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--config' && args[i + 1]) {
      configPath = args[++i];
    } else if (args[i] === '--output' && args[i + 1]) {
      outputPath = args[++i];
    } else if (!args[i].startsWith('--')) {
      configPath = args[i];
    }
  }

  if (!configPath) {
    console.error('Usage: tsx src/index.ts --config <path-to-config.json> [--output <output-dir>]');
    console.error('');
    console.error('Examples:');
    console.error('  tsx src/index.ts --config src/config/sample.json');
    console.error('  tsx src/index.ts --config my-project.json --output ./my-output');
    process.exit(1);
  }

  return { configPath, outputPath };
}

// ── Main ──

async function main() {
  const { configPath, outputPath: customOutputPath } = parseArgs();

  console.log(`\n  PLOTCODE DOCX Generator v2.0`);
  console.log(`  ${'─'.repeat(40)}`);

  // Load config
  const configFullPath = path.resolve(configPath);
  if (!fs.existsSync(configFullPath)) {
    console.error(`\n  Error: Config file not found: ${configFullPath}`);
    process.exit(1);
  }

  console.log(`  Loading config: ${configPath}`);
  const rawConfig = JSON.parse(fs.readFileSync(configFullPath, 'utf-8'));

  // Validate config
  const parseResult = DocumentConfigSchema.safeParse(rawConfig);
  if (!parseResult.success) {
    console.error('\n  Error: Invalid config file:');
    for (const issue of parseResult.error.issues) {
      console.error(`    - ${issue.path.join('.')}: ${issue.message}`);
    }
    process.exit(1);
  }

  const config = parseResult.data;
  console.log(`  Project: ${config.projectName}`);
  console.log(`  Phases: ${config.phases.length}`);
  console.log(`  Total tasks: ${config.phases.reduce((sum, p) => sum + p.sections.reduce((s, sec) => s + sec.tasks.length, 0), 0)}`);

  // Build document
  console.log(`\n  Building document...`);
  const doc = buildDocument(config);

  // Export
  const outputDir = customOutputPath || path.resolve(config.outputPath || 'output');
  const filename = `${config.projectName.replace(/\s+/g, '_')}_${config.docType.replace(/\s+/g, '_')}.docx`;

  console.log(`  Exporting to: ${path.join(outputDir, filename)}`);
  const fullPath = await exportToDocx(doc, outputDir, filename);

  console.log(`\n  Done! File saved to: ${fullPath}`);
  console.log(`  File size: ${(fs.statSync(fullPath).size / 1024).toFixed(1)} KB\n`);
}

main().catch((err) => {
  console.error('\n  Fatal error:', err);
  process.exit(1);
});
