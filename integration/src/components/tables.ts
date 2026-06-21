import {
  Table, TableRow, TableCell, Paragraph, TextRun,
  AlignmentType, WidthType, ShadingType, BorderStyle,
} from 'docx';
import { COLORS, TYPE_COLORS } from '../styles/colors.js';
import { FONTS, SIZES, TABLE_WIDTH } from '../styles/fonts.js';
import { borders, noBorders, leftAccentBorder } from '../styles/borders.js';

// ── Types ──

export interface TaskItem {
  text: string;
  owner: string;
  type: string;
  notes?: string;
}

export interface TechStackItem {
  layer: string;
  choice: string;
  reason: string;
}

// ── Cell Helpers ──

interface CellOpts {
  width: number;
  text?: string;
  runs?: Array<{ text: string; bold?: boolean; size?: number; color?: string; italic?: boolean }>;
  shading?: { fill: string; type: typeof ShadingType.CLEAR };
  align?: typeof AlignmentType[keyof typeof AlignmentType];
  borderStyle?: typeof borders;
  margins?: { top: number; bottom: number; left: number; right: number };
}

function createCell(opts: CellOpts): TableCell {
  const runs = opts.runs || (opts.text
    ? [{ text: opts.text, size: SIZES.small, color: COLORS.darkGray }]
    : []);

  return new TableCell({
    borders: opts.borderStyle || borders,
    width: { size: opts.width, type: WidthType.DXA },
    ...(opts.shading && { shading: { ...opts.shading, type: ShadingType.CLEAR } }),
    margins: opts.margins || { top: 80, bottom: 80, left: 120, right: 120 },
    ...(opts.align && { verticalAlign: opts.align === AlignmentType.CENTER ? 'center' : undefined }),
    children: [
      new Paragraph({
        ...(opts.align && { alignment: opts.align }),
        children: runs.map(r => new TextRun({
          text: r.text,
          bold: r.bold,
          size: r.size || SIZES.small,
          color: r.color || COLORS.darkGray,
          font: FONTS.primary,
          italics: r.italic,
        })),
      }),
    ],
  });
}

// ── Info Box ──

export function infoBox(label: string, text: string, fg: string, bg: string): Table {
  return new Table({
    width: { size: TABLE_WIDTH, type: WidthType.DXA },
    columnWidths: [TABLE_WIDTH],
    rows: [
      new TableRow({
        children: [
          new TableCell({
            borders: leftAccentBorder(fg),
            shading: { fill: bg, type: ShadingType.CLEAR },
            margins: { top: 100, bottom: 100, left: 200, right: 200 },
            width: { size: TABLE_WIDTH, type: WidthType.DXA },
            children: [
              new Paragraph({
                children: [
                  new TextRun({ text: label, bold: true, size: SIZES.small, color: fg, font: FONTS.primary }),
                ],
              }),
              new Paragraph({
                spacing: { before: 40 },
                children: [
                  new TextRun({ text, size: SIZES.body, color: COLORS.darkGray, font: FONTS.primary }),
                ],
              }),
            ],
          }),
        ],
      }),
    ],
  });
}

// ── Phase Header ──

export function phaseHeader(
  phaseNum: string,
  title: string,
  tagText: string,
  tagFg: string,
  tagBg: string,
): Table {
  const leftWidth = TABLE_WIDTH - 1800;
  const rightWidth = 1800;

  return new Table({
    width: { size: TABLE_WIDTH, type: WidthType.DXA },
    columnWidths: [leftWidth, rightWidth],
    borders: {
      top: { style: BorderStyle.NONE, size: 0, color: COLORS.white },
      bottom: { style: BorderStyle.SINGLE, size: 6, color: COLORS.accentBlue, space: 0 },
      left: { style: BorderStyle.NONE, size: 0, color: COLORS.white },
      right: { style: BorderStyle.NONE, size: 0, color: COLORS.white },
    },
    rows: [
      new TableRow({
        children: [
          new TableCell({
            borders: noBorders,
            width: { size: leftWidth, type: WidthType.DXA },
            margins: { top: 80, bottom: 80, left: 0, right: 120 },
            children: [
              new Paragraph({
                children: [
                  new TextRun({ text: `PHASE ${phaseNum}  `, bold: true, size: SIZES.h3, color: COLORS.midGray, font: FONTS.primary }),
                  new TextRun({ text: title, bold: true, size: SIZES.h3, color: COLORS.accentBlue, font: FONTS.primary }),
                ],
              }),
            ],
          }),
          new TableCell({
            borders: noBorders,
            width: { size: rightWidth, type: WidthType.DXA },
            shading: { fill: tagBg, type: ShadingType.CLEAR },
            margins: { top: 80, bottom: 80, left: 120, right: 120 },
            verticalAlign: 'center',
            children: [
              new Paragraph({
                alignment: AlignmentType.CENTER,
                children: [
                  new TextRun({ text: tagText, bold: true, size: SIZES.tiny, color: tagFg, font: FONTS.primary }),
                ],
              }),
            ],
          }),
        ],
      }),
    ],
  });
}

// ── Task Table ──

function taskRow(num: number, task: TaskItem): TableRow {
  const c = TYPE_COLORS[task.type] || { fg: COLORS.midGray, bg: COLORS.lightGray };

  return new TableRow({
    children: [
      // # column
      createCell({
        width: 500,
        text: String(num).padStart(2, '0'),
        shading: { fill: COLORS.lightGray, type: ShadingType.CLEAR },
        align: AlignmentType.CENTER,
        margins: { top: 80, bottom: 80, left: 120, right: 120 },
      }),
      // Task column (with notes support)
      new TableCell({
        borders,
        width: { size: 4160, type: WidthType.DXA },
        margins: { top: 80, bottom: 80, left: 140, right: 120 },
        children: [
          new Paragraph({
            children: [
              new TextRun({ text: '\u2610  ' + task.text, size: SIZES.body - 1, color: COLORS.darkGray, font: FONTS.primary }),
            ],
          }),
          ...(task.notes
            ? [
                new Paragraph({
                  spacing: { before: 30 },
                  children: [
                    new TextRun({ text: task.notes, size: SIZES.tiny, color: COLORS.midGray, font: FONTS.primary, italics: true }),
                  ],
                }),
              ]
            : []),
        ],
      }),
      // Owner column
      createCell({
        width: 2000,
        text: task.owner,
        margins: { top: 80, bottom: 80, left: 120, right: 120 },
      }),
      // Type badge column
      new TableCell({
        borders,
        width: { size: 1200, type: WidthType.DXA },
        shading: { fill: c.bg, type: ShadingType.CLEAR },
        margins: { top: 80, bottom: 80, left: 100, right: 100 },
        verticalAlign: 'center',
        children: [
          new Paragraph({
            alignment: AlignmentType.CENTER,
            children: [
              new TextRun({ text: task.type, bold: true, size: SIZES.tiny, color: c.fg, font: FONTS.primary }),
            ],
          }),
        ],
      }),
    ],
  });
}

function headerCell(text: string, width: number): TableCell {
  return new TableCell({
    borders,
    width: { size: width, type: WidthType.DXA },
    shading: { fill: COLORS.accentBlue, type: ShadingType.CLEAR },
    margins: { top: 100, bottom: 100, left: 120, right: 120 },
    children: [
      new Paragraph({
        children: [
          new TextRun({ text, bold: true, size: SIZES.small, color: COLORS.white, font: FONTS.primary }),
        ],
      }),
    ],
  });
}

export function taskTable(tasks: TaskItem[]): Table {
  const headerRow = new TableRow({
    tableHeader: true,
    children: [
      headerCell('#', 500),
      headerCell('Task', 4160),
      headerCell('Owner', 2000),
      new TableCell({
        borders,
        width: { size: 1200, type: WidthType.DXA },
        shading: { fill: COLORS.accentBlue, type: ShadingType.CLEAR },
        margins: { top: 100, bottom: 100, left: 100, right: 100 },
        children: [
          new Paragraph({
            alignment: AlignmentType.CENTER,
            children: [
              new TextRun({ text: 'Type', bold: true, size: SIZES.small, color: COLORS.white, font: FONTS.primary }),
            ],
          }),
        ],
      }),
    ],
  });

  return new Table({
    width: { size: TABLE_WIDTH, type: WidthType.DXA },
    columnWidths: [500, 4160, 2000, 1200],
    rows: [headerRow, ...tasks.map((t, i) => taskRow(i + 1, t))],
  });
}

// ── Tech Stack Table ──

export function techStackTable(items: TechStackItem[]): Table {
  const colWidths = [2000, 2800, 4560];

  const headerRow = new TableRow({
    tableHeader: true,
    children: [
      headerCell('Layer', colWidths[0]),
      headerCell('Choice', colWidths[1]),
      headerCell('Reason', colWidths[2]),
    ],
  });

  const dataRows = items.map((item, i) =>
    new TableRow({
      children: [
        new TableCell({
          borders,
          width: { size: colWidths[0], type: WidthType.DXA },
          shading: { fill: i % 2 === 0 ? COLORS.lightGray : COLORS.white, type: ShadingType.CLEAR },
          margins: { top: 80, bottom: 80, left: 120, right: 120 },
          children: [
            new Paragraph({
              children: [
                new TextRun({ text: item.layer, bold: true, size: SIZES.small, color: COLORS.darkGray, font: FONTS.primary }),
              ],
            }),
          ],
        }),
        new TableCell({
          borders,
          width: { size: colWidths[1], type: WidthType.DXA },
          shading: { fill: i % 2 === 0 ? COLORS.lightGray : COLORS.white, type: ShadingType.CLEAR },
          margins: { top: 80, bottom: 80, left: 120, right: 120 },
          children: [
            new Paragraph({
              children: [
                new TextRun({ text: item.choice, size: SIZES.small, color: COLORS.accentBlue, font: FONTS.primary }),
              ],
            }),
          ],
        }),
        new TableCell({
          borders,
          width: { size: colWidths[2], type: WidthType.DXA },
          shading: { fill: i % 2 === 0 ? COLORS.lightGray : COLORS.white, type: ShadingType.CLEAR },
          margins: { top: 80, bottom: 80, left: 120, right: 120 },
          children: [
            new Paragraph({
              children: [
                new TextRun({ text: item.reason, size: SIZES.small, color: COLORS.darkGray, font: FONTS.primary }),
              ],
            }),
          ],
        }),
      ],
    }),
  );

  return new Table({
    width: { size: TABLE_WIDTH, type: WidthType.DXA },
    columnWidths: colWidths,
    rows: [headerRow, ...dataRows],
  });
}
