/**
 * Theme configuration for the migraine tracking app.
 * To change the theme, simply modify the color values below.
 * All colors support both light and dark modes.
 */

import { Platform } from 'react-native';

// Primary theme colors - soft, calming palette for migraine prevention
const primaryColor = '#017173'; // Teal
const primaryDark = '#0F2E28'; // Dark teal background
const secondaryColor = '#88CCC5'; // Light teal
const accentColor = '#60DDAC'; // Mint green

// Neutral colors
const tintColorLight = primaryColor;
const tintColorDark = secondaryColor;

export const Colors = {
  light: {
    // Base colors
    text: '#0F2E28',
    textSecondary: '#017173',
    background: '#F4F4F4',
    backgroundSecondary: '#FFFFFF',
    border: '#88CCC5',
    
    // Primary colors
    primary: primaryColor,
    primaryDark: primaryDark,
    secondary: secondaryColor,
    accent: accentColor,
    
    // UI colors
    tint: tintColorLight,
    icon: '#017173',
    tabIconDefault: '#88CCC5',
    tabIconSelected: tintColorLight,
    
    // Status colors - softer versions
    success: '#60DDAC',
    warning: '#88CCC5',
    error: '#88CCC5', // Softer error color
    info: '#017173',
    
    // Card colors
    card: '#FFFFFF',
    cardBorder: '#88CCC5',
    
    // Input colors
    inputBackground: '#FFFFFF',
    inputBorder: '#88CCC5',
    inputFocus: primaryColor,
  },
  dark: {
    // Base colors - using the dark teal background as default
    text: '#F4F4F4',
    textSecondary: '#88CCC5',
    background: '#0F2E28',
    backgroundSecondary: '#017173',
    border: '#88CCC5',
    
    // Primary colors
    primary: secondaryColor,
    primaryDark: primaryDark,
    secondary: accentColor,
    accent: accentColor,
    
    // UI colors
    tint: tintColorDark,
    icon: '#88CCC5',
    tabIconDefault: '#60DDAC',
    tabIconSelected: tintColorDark,
    
    // Status colors - softer versions
    success: '#60DDAC',
    warning: '#88CCC5',
    error: '#88CCC5', // Softer error color
    info: '#88CCC5',
    
    // Card colors
    card: '#017173',
    cardBorder: '#88CCC5',
    
    // Input colors
    inputBackground: '#017173',
    inputBorder: '#88CCC5',
    inputFocus: secondaryColor,
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
