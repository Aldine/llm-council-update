// Industrial Metallic Theme - Converted from OKLCH to hex
export const Colors = {
  background: '#1F262A',      // oklch(20% 0.01 240)
  foreground: '#E8EAEB',      // oklch(92% 0.01 240)
  card: '#4A5C68',            // oklch(57% 0.02 220)
  cardForeground: '#E8EAEB',
  primary: '#546E7A',         // oklch(65% 0.02 240)
  primaryForeground: '#F5F6F6',
  secondary: '#2A3439',       // oklch(50% 0.01 240)
  secondaryForeground: '#E8EAEB',
  muted: '#333D42',
  mutedForeground: '#AAB0AD', // oklch(75% 0.01 240)
  accent: '#AAB0AD',
  accentForeground: '#1F262A',
  destructive: '#E53935',
  destructiveForeground: '#FFFFFF',
  border: '#3D474D',
  input: '#3D474D',
  ring: '#546E7A',
};

export const Spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
};

export const Typography = {
  h1: {
    fontSize: 32,
    fontWeight: '700' as const,
    lineHeight: 40,
  },
  h2: {
    fontSize: 24,
    fontWeight: '600' as const,
    lineHeight: 32,
  },
  h3: {
    fontSize: 20,
    fontWeight: '600' as const,
    lineHeight: 28,
  },
  body: {
    fontSize: 16,
    fontWeight: '400' as const,
    lineHeight: 24,
  },
  small: {
    fontSize: 14,
    fontWeight: '400' as const,
    lineHeight: 20,
  },
  tiny: {
    fontSize: 12,
    fontWeight: '400' as const,
    lineHeight: 16,
  },
};

export const BorderRadius = {
  sm: 4,
  md: 8,
  lg: 12,
  xl: 16,
  full: 9999,
};
