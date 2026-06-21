import { Paragraph, PageBreak, TextRun, AlignmentType, Table } from 'docx';
import { h1, h2 } from '../components/headings.js';
import { body } from '../components/body.js';
import { sp, sectionDivider } from '../components/dividers.js';
import { infoBox } from '../components/tables.js';
import { COLORS } from '../styles/colors.js';
import { FONTS, SIZES } from '../styles/fonts.js';
import { DocumentConfig } from '../config/schema.js';

export function createWhatWins(config: DocumentConfig): (Paragraph | Table)[] {
  const elements: (Paragraph | Table)[] = [
    new Paragraph({ children: [new PageBreak()] }),
    h1('What Makes This Win'),
    sp(40),
    infoBox(
      'The three moments judges remember',
      'These three sequences, if they work live, will win the hackathon. Every other task in this plan is in service of making these three moments bulletproof.',
      COLORS.accentBlue,
      COLORS.accentLight
    ),
    sp(80),
  ];

  for (const moment of config.winMoments) {
    elements.push(h2(moment.title));
    elements.push(body(moment.body));
    elements.push(sp(60));
  }

  elements.push(sp(120));
  elements.push(sectionDivider());
  elements.push(
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { before: 120 },
      children: [
        new TextRun({
          text: `${config.projectName} — Build something worth deploying.`,
          size: SIZES.body,
          color: COLORS.midGray,
          font: FONTS.primary,
          italics: true,
        }),
      ],
    })
  );

  return elements;
}
