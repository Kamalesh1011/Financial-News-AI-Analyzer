import { Footer, Paragraph, TextRun, AlignmentType, BorderStyle, PageNumber } from 'docx';
import { COLORS } from '../styles/colors.js';
import { FONTS, SIZES } from '../styles/fonts.js';

export function createFooter(projectName: string, confidential: boolean = true): Footer {
  return new Footer({
    children: [
      new Paragraph({
        alignment: AlignmentType.CENTER,
        border: {
          top: { style: BorderStyle.SINGLE, size: 4, color: COLORS.borderGray, space: 4 },
        },
        children: [
          new TextRun({
            text: `${projectName} — Build Plan    |    Page `,
            size: SIZES.tiny,
            color: COLORS.midGray,
            font: FONTS.primary,
          }),
          new TextRun({
            children: [PageNumber.CURRENT],
            size: SIZES.tiny,
            color: COLORS.midGray,
            font: FONTS.primary,
          }),
          ...(confidential
            ? [
                new TextRun({
                  text: '    |    CONFIDENTIAL',
                  size: SIZES.tiny,
                  color: COLORS.midGray,
                  font: FONTS.primary,
                }),
              ]
            : []),
        ],
      }),
    ],
  });
}
