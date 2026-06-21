import { BorderStyle } from 'docx';
import { COLORS } from './colors.js';

export const border = {
  style: BorderStyle.SINGLE,
  size: 1,
  color: COLORS.borderGray,
};

export const borders = {
  top: border,
  bottom: border,
  left: border,
  right: border,
};

export const noBorders = {
  top: { style: BorderStyle.NONE, size: 0, color: COLORS.white },
  bottom: { style: BorderStyle.NONE, size: 0, color: COLORS.white },
  left: { style: BorderStyle.NONE, size: 0, color: COLORS.white },
  right: { style: BorderStyle.NONE, size: 0, color: COLORS.white },
};

export const thickBottomBorder = {
  top: { style: BorderStyle.NONE, size: 0, color: COLORS.white },
  bottom: { style: BorderStyle.SINGLE, size: 6, color: COLORS.accentBlue, space: 0 },
  left: { style: BorderStyle.NONE, size: 0, color: COLORS.white },
  right: { style: BorderStyle.NONE, size: 0, color: COLORS.white },
  insideH: { style: BorderStyle.NONE, size: 0, color: COLORS.white },
  insideV: { style: BorderStyle.NONE, size: 0, color: COLORS.white },
};

export const leftAccentBorder = (color: string) => ({
  top: { style: BorderStyle.NONE, size: 0, color: COLORS.white },
  bottom: { style: BorderStyle.NONE, size: 0, color: COLORS.white },
  right: { style: BorderStyle.NONE, size: 0, color: COLORS.white },
  left: { style: BorderStyle.SINGLE, size: 12, color },
});

export const topDividerBorder = {
  top: { style: BorderStyle.SINGLE, size: 4, color: COLORS.borderGray, space: 4 },
  bottom: { style: BorderStyle.NONE, size: 0, color: COLORS.white },
  left: { style: BorderStyle.NONE, size: 0, color: COLORS.white },
  right: { style: BorderStyle.NONE, size: 0, color: COLORS.white },
};
