import { Document, LevelFormat, AlignmentType, Paragraph, Table } from 'docx';
import { DocumentConfig } from '../config/schema.js';
import { createCover } from '../components/cover.js';
import { createFooter } from '../components/footer.js';
import { createOverview } from '../sections/overview.js';
import { createPhases } from '../sections/phases.js';
import { createDeliverables } from '../sections/deliverables.js';
import { createTechStack } from '../sections/techStack.js';
import { createWhatWins } from '../sections/whatWins.js';
import { PAGE } from '../styles/fonts.js';

export function buildDocument(config: DocumentConfig): Document {
  const children = [
    // Cover page
    ...createCover(config),

    // Overview + 14-stage flow + guardrails
    ...createOverview(config),

    // All phases (0-6)
    ...createPhases(config),

    // Required deliverables
    ...createDeliverables(config),

    // Tech stack reference
    ...createTechStack(config),

    // What makes this win
    ...createWhatWins(config),
  ];

  return new Document({
    numbering: {
      config: [
        {
          reference: 'bullets',
          levels: [
            {
              level: 0,
              format: LevelFormat.BULLET,
              text: '\u2022',
              alignment: AlignmentType.LEFT,
              style: { paragraph: { indent: { left: 720, hanging: 360 } } },
            },
            {
              level: 1,
              format: LevelFormat.BULLET,
              text: '\u2013',
              alignment: AlignmentType.LEFT,
              style: { paragraph: { indent: { left: 1080, hanging: 360 } } },
            },
          ],
        },
      ],
    },
    styles: {
      default: {
        document: { run: { font: 'Arial', size: 22 } },
      },
      paragraphStyles: [
        {
          id: 'Heading1',
          name: 'Heading 1',
          basedOn: 'Normal',
          next: 'Normal',
          quickFormat: true,
          run: { size: 34, bold: true, font: 'Arial' },
          paragraph: { spacing: { before: 360, after: 120 }, outlineLevel: 0 },
        },
        {
          id: 'Heading2',
          name: 'Heading 2',
          basedOn: 'Normal',
          next: 'Normal',
          quickFormat: true,
          run: { size: 26, bold: true, font: 'Arial' },
          paragraph: { spacing: { before: 280, after: 100 }, outlineLevel: 1 },
        },
        {
          id: 'Heading3',
          name: 'Heading 3',
          basedOn: 'Normal',
          next: 'Normal',
          quickFormat: true,
          run: { size: 22, bold: true, font: 'Arial' },
          paragraph: { spacing: { before: 200, after: 80 }, outlineLevel: 2 },
        },
      ],
    },
    sections: [
      {
        properties: {
          page: {
            size: { width: PAGE.width, height: PAGE.height },
            margin: PAGE.margin,
          },
        },
        footers: {
          default: createFooter(config.projectName, config.confidential),
        },
        children,
      },
    ],
  });
}
