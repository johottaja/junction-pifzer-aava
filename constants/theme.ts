/**
 * Theme configuration for the migraine tracking app.
 * To change the theme, simply modify the color values below.
 * All colors support both light and dark modes.
 */

import { Platform } from 'react-native';

// Primary theme colors - change these to customize the app appearance
const primaryColor = '#6366F1'; // Indigo
const primaryDark = '#4F46E5';
const secondaryColor = '#8B5CF6'; // Purple
const accentColor = '#EC4899'; // Pink

// Neutral colors
const tintColorLight = primaryColor;
const tintColorDark = '#A5B4FC';

export const Colors = {
  light: {
    // Base colors
    text: '#1F2937',
    textSecondary: '#6B7280',
    background: '#FFFFFF',
    backgroundSecondary: '#F9FAFB',
    border: '#E5E7EB',
    
    // Primary colors
    primary: primaryColor,
    primaryDark: primaryDark,
    secondary: secondaryColor,
    accent: accentColor,
    
    // UI colors
    tint: tintColorLight,
    icon: '#6B7280',
    tabIconDefault: '#9CA3AF',
    tabIconSelected: tintColorLight,
    
    // Status colors
    success: '#10B981',
    warning: '#F59E0B',
    error: '#EF4444',
    info: '#3B82F6',
    
    // Card colors
    card: '#FFFFFF',
    cardBorder: '#E5E7EB',
    
    // Input colors
    inputBackground: '#F9FAFB',
    inputBorder: '#D1D5DB',
    inputFocus: primaryColor,
  },
  dark: {
    // Base colors
    text: '#F9FAFB',
    textSecondary: '#D1D5DB',
    background: '#111827',
    backgroundSecondary: '#1F2937',
    border: '#374151',
    
    // Primary colors
    primary: tintColorDark,
    primaryDark: '#818CF8',
    secondary: '#A78BFA',
    accent: '#F472B6',
    
    // UI colors
    tint: tintColorDark,
    icon: '#9CA3AF',
    tabIconDefault: '#6B7280',
    tabIconSelected: tintColorDark,
    
    // Status colors
    success: '#34D399',
    warning: '#FBBF24',
    error: '#F87171',
    info: '#60A5FA',
    
    // Card colors
    card: '#1F2937',
    cardBorder: '#374151',
    
    // Input colors
    inputBackground: '#1F2937',
    inputBorder: '#4B5563',
    inputFocus: tintColorDark,
  },
};

export const Fonts = Platform.select({
  ios: {
    /** iOS `UIFontDescriptorSystemDesignDefault` */
    sans: 'system-ui',
    /** iOS `UIFontDescriptorSystemDesignSerif` */
    serif: 'ui-serif',
    /** iOS `UIFontDescriptorSystemDesignRounded` */
    rounded: 'ui-rounded',
    /** iOS `UIFontDescriptorSystemDesignMonospaced` */
    mono: 'ui-monospace',
  },
  default: {
    sans: 'normal',
    serif: 'serif',
    rounded: 'normal',
    mono: 'monospace',
  },
  web: {
    sans: "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
    serif: "Georgia, 'Times New Roman', serif",
    rounded: "'SF Pro Rounded', 'Hiragino Maru Gothic ProN', Meiryo, 'MS PGothic', sans-serif",
    mono: "SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace",
  },
});
