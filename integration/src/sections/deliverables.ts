import { Paragraph, PageBreak, Table } from 'docx';
import { h1, h2 } from '../components/headings.js';
import { body } from '../components/body.js';
import { sp } from '../components/dividers.js';
import { taskTable } from '../components/tables.js';
import { DocumentConfig } from '../config/schema.js';

export function createDeliverables(config: DocumentConfig): (Paragraph | Table)[] {
  return [
    new Paragraph({ children: [new PageBreak()] }),
    h1('Required Deliverables'),
    body('Per the project spec, these must exist at completion — independent of the working system.'),
    sp(80),

    h2('Documentation'),
    taskTable(config.deliverables),
    sp(80),
  ];
}
