import { Paragraph, TextRun, AlignmentType, BorderStyle, PageBreak } from 'docx';
import { COLORS } from '../styles/colors.js';
import { FONTS, SIZES } from '../styles/fonts.js';
import { sp } from './dividers.js';

export interface CoverConfig {
  projectName: string;
  tagline: string;
  docType: string;
}

export function createCover(config: CoverConfig): Paragraph[] {
  return [
    sp(720),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [
        new TextRun({ text: config.projectName, bold: true, size: SIZES.title, color: COLORS.accentBlue, font: FONTS.primary }),
      ],
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { before: 80, after: 80 },
      children: [
        new TextRun({ text: config.tagline, size: SIZES.subtitle, color: COLORS.midGray, font: FONTS.primary }),
      ],
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { before: 40, after: 480 },
      children: [
        new TextRun({ text: config.docType.toUpperCase(), bold: true, size: SIZES.docType, color: COLORS.midGray, font: FONTS.primary, allCaps: true }),
      ],
    }),
    new Paragraph({
      border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: COLORS.accentBlue, space: 1 } },
      children: [],
    }),
    sp(200),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [
        new TextRun({ text: 'From request to production — autonomously, with humans in the loop.', size: SIZES.body, color: COLORS.midGray, font: FONTS.primary, italics: true }),
      ],
    }),
    sp(800),
  ];
}
