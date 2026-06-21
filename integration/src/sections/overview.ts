import { Paragraph, PageBreak, Table } from 'docx';
import { h1, h2 } from '../components/headings.js';
import { body } from '../components/body.js';
import { sp } from '../components/dividers.js';
import { taskTable, infoBox } from '../components/tables.js';
import { COLORS } from '../styles/colors.js';
import { DocumentConfig } from '../config/schema.js';

export function createOverview(config: DocumentConfig): (Paragraph | Table)[] {
  return [
    new Paragraph({ children: [new PageBreak()] }),
    h1('Project Overview'),
    body(config.overview.description),
    sp(),
    body(config.overview.goal, { color: COLORS.midGray, italic: true }),
    sp(120),

    h2('The 14-Stage Flow'),
    taskTable(
      config.flowSummary.map(f => ({
        text: f.task,
        owner: f.owner,
        type: f.type,
        notes: f.notes,
      }))
    ),
    sp(120),

    h2('Non-Negotiable Guardrails'),
    infoBox(
      'AI Constraints — Hard Limits',
      config.guardrails.map(g => g.text).join('. ') + '.',
      COLORS.warnRed,
      COLORS.warnBg
    ),
    sp(80),
  ];
}
