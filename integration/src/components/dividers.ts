import { Paragraph, BorderStyle } from 'docx';
import { COLORS } from '../styles/colors.js';

export function sectionDivider(): Paragraph {
  return new Paragraph({
    spacing: { before: 200, after: 200 },
    border: {
      bottom: { style: BorderStyle.SINGLE, size: 4, color: COLORS.borderGray, space: 1 },
    },
    children: [],
  });
}

export function sp(before: number = 80, after: number = 80): Paragraph {
  return new Paragraph({ spacing: { before, after }, children: [] });
}
