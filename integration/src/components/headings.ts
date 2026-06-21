import { Paragraph, TextRun, HeadingLevel } from 'docx';
import { COLORS } from '../styles/colors.js';
import { FONTS, SIZES } from '../styles/fonts.js';

export function h1(text: string): Paragraph {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    spacing: { before: 360, after: 120 },
    children: [
      new TextRun({ text, bold: true, size: SIZES.h1, color: COLORS.accentBlue, font: FONTS.primary }),
    ],
  });
}

export function h2(text: string): Paragraph {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    spacing: { before: 280, after: 100 },
    children: [
      new TextRun({ text, bold: true, size: SIZES.h2, color: COLORS.darkGray, font: FONTS.primary }),
    ],
  });
}

export function h3(text: string): Paragraph {
  return new Paragraph({
    heading: HeadingLevel.HEADING_3,
    spacing: { before: 200, after: 80 },
    children: [
      new TextRun({ text, bold: true, size: SIZES.h3, color: COLORS.midGray, font: FONTS.primary }),
    ],
  });
}
