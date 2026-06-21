import { Paragraph, PageBreak, TextRun, Table } from 'docx';
import { phaseHeader, taskTable } from '../components/tables.js';
import { body } from '../components/body.js';
import { sp } from '../components/dividers.js';
import { COLORS } from '../styles/colors.js';
import { FONTS, SIZES } from '../styles/fonts.js';
import { DocumentConfig } from '../config/schema.js';

export function createPhases(config: DocumentConfig): (Paragraph | Table)[] {
  const elements: (Paragraph | Table)[] = [];

  for (const phase of config.phases) {
    elements.push(new Paragraph({ children: [new PageBreak()] }));
    elements.push(phaseHeader(
      String(phase.num),
      phase.title,
      phase.tag,
      phase.tagColor,
      phase.tagBg
    ));
    elements.push(sp(80));

    if (phase.intro) {
      elements.push(body(phase.intro));
      elements.push(sp(80));
    }

    for (const section of phase.sections) {
      elements.push(new Paragraph({
        spacing: { before: 200, after: 80 },
        children: [
          new TextRun({
            text: section.title,
            bold: true,
            size: SIZES.h3,
            color: COLORS.midGray,
            font: FONTS.primary,
          }),
        ],
      }));

      if (section.intro) {
        elements.push(body(section.intro));
      }

      elements.push(taskTable(section.tasks));
      elements.push(sp(60));
    }

    elements.push(sp(80));
  }

  return elements;
}
