import { Paragraph, PageBreak, Table } from 'docx';
import { h1 } from '../components/headings.js';
import { sp } from '../components/dividers.js';
import { techStackTable } from '../components/tables.js';
import { DocumentConfig } from '../config/schema.js';

export function createTechStack(config: DocumentConfig): (Paragraph | Table)[] {
  return [
    new Paragraph({ children: [new PageBreak()] }),
    h1('Tech Stack Reference'),
    sp(40),
    techStackTable(config.techStack),
    sp(120),
  ];
}
