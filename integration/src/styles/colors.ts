export const COLORS = {
  black:       '1A1A1A',
  darkGray:    '2D2D2D',
  midGray:     '555555',
  lightGray:   'F5F5F5',
  borderGray:  'DDDDDD',
  white:       'FFFFFF',

  accentBlue:  '1E3A5F',
  accentLight: 'EBF0F7',

  gateOrange:  'B05000',
  gateLight:   'FDF3EB',

  agentPurple: '3B1A6E',
  agentLight:  'F2EEF9',

  infraGreen:  '1A4D2E',
  infraLight:  'EAF4EE',

  doneGreen:   '1A6B3A',
  doneBg:      'E8F5ED',

  warnRed:     '8B1A1A',
  warnBg:      'FDF0F0',
} as const;

export type ColorKey = keyof typeof COLORS;

export const TYPE_COLORS: Record<string, { fg: string; bg: string }> = {
  Infra:     { fg: COLORS.infraGreen,  bg: COLORS.infraLight },
  Agent:     { fg: COLORS.agentPurple, bg: COLORS.agentLight },
  HITL:      { fg: COLORS.gateOrange,  bg: COLORS.gateLight },
  Guardrail: { fg: COLORS.warnRed,     bg: COLORS.warnBg },
  UI:        { fg: COLORS.accentBlue,  bg: COLORS.accentLight },
  Test:      { fg: COLORS.doneGreen,   bg: COLORS.doneBg },
};
