import { z } from 'zod';

export const TaskSchema = z.object({
  text: z.string(),
  owner: z.string(),
  type: z.enum(['Infra', 'Agent', 'HITL', 'Guardrail', 'UI', 'Test']),
  notes: z.string().optional(),
});

export const PhaseSectionSchema = z.object({
  title: z.string(),
  intro: z.string().optional(),
  tasks: z.array(TaskSchema),
});

export const PhaseSchema = z.object({
  num: z.number(),
  title: z.string(),
  tag: z.string(),
  tagColor: z.string(),
  tagBg: z.string(),
  intro: z.string().optional(),
  sections: z.array(PhaseSectionSchema),
});

export const TechStackItemSchema = z.object({
  layer: z.string(),
  choice: z.string(),
  reason: z.string(),
});

export const GuardrailSchema = z.object({
  text: z.string(),
  owner: z.string(),
  type: z.literal('Guardrail'),
  notes: z.string().optional(),
});

export const DeliverableSchema = z.object({
  text: z.string(),
  owner: z.string(),
  type: z.string(),
  notes: z.string().optional(),
});

export const WinMomentSchema = z.object({
  title: z.string(),
  body: z.string(),
});

export const DocumentConfigSchema = z.object({
  projectName: z.string(),
  tagline: z.string(),
  docType: z.string(),
  confidential: z.boolean().default(true),

  overview: z.object({
    description: z.string(),
    goal: z.string(),
  }),

  flowSummary: z.array(z.object({
    stage: z.string(),
    task: z.string(),
    owner: z.string(),
    type: z.string(),
    notes: z.string().optional(),
  })),

  guardrails: z.array(GuardrailSchema),

  phases: z.array(PhaseSchema),

  deliverables: z.array(DeliverableSchema),

  techStack: z.array(TechStackItemSchema),

  winMoments: z.array(WinMomentSchema),

  outputPath: z.string().optional().default('output'),
});

export type DocumentConfig = z.infer<typeof DocumentConfigSchema>;
export type Task = z.infer<typeof TaskSchema>;
export type Phase = z.infer<typeof PhaseSchema>;
export type TechStackItem = z.infer<typeof TechStackItemSchema>;
