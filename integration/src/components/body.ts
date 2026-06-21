import { Paragraph, TextRun } from 'docx';
import { COLORS } from '../styles/colors.js';
import { FONTS, SIZES } from '../styles/fonts.js';

export interface BodyOptions {
  color?: string;
  bold?: boolean;
  italic?: boolean;
}

export function body(text: string, opts: BodyOptions = {}): Paragraph {
  return new Paragraph({
    spacing: { before: 40, after: 60 },
    children: [
      new TextRun({
        text,
        size: SIZES.body,
        color: opts.color || COLORS.darkGray,
        font: FONTS.primary,
        bold: opts.bold || false,
        italics: opts.italic || false,
      }),
    ],
  });
}

export function bullet(text: string, level: number = 0): Paragraph {
  return new Paragraph({
    numbering: { reference: 'bullets', level },
    spacing: { before: 30, after: 30 },
    children: [
      new TextRun({ text, size: SIZES.body, color: COLORS.darkGray, font: FONTS.primary }),
    ],
  });
}

export function checkbox(text: string, done: boolean = false): Paragraph {
  const box = done ? '\u2611' : '\u2610';
  return new Paragraph({
    spacing: { before: 40, after: 40 },
    indent: { left: 360 },
    children: [
      new TextRun({
        text: `${box}  `,
        size: SIZES.body,
        color: done ? COLORS.doneGreen : COLORS.darkGray,
        font: FONTS.primary,
        bold: done,
      }),
      new TextRun({
        text,
        size: SIZES.body,
        color: done ? COLORS.midGray : COLORS.darkGray,
        font: FONTS.primary,
      }),
    ],
  });
}
