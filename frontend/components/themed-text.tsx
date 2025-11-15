import { StyleSheet, Text, type TextProps } from 'react-native';

import { useThemeColor } from '@/hooks/use-theme-color';
import { Fonts } from '@/constants/theme';

export type ThemedTextProps = TextProps & {
  lightColor?: string;
  darkColor?: string;
  type?: 'default' | 'title' | 'defaultSemiBold' | 'subtitle' | 'link';
};

export function ThemedText({
  style,
  lightColor,
  darkColor,
  type = 'default',
  ...rest
}: ThemedTextProps) {
  const color = useThemeColor({ light: lightColor, dark: darkColor }, 'text');
  const fonts = Fonts;

  return (
    <Text
      style={[
        { color, backgroundColor: 'transparent' },
        type === 'default' ? [styles.default, { fontFamily: fonts.sans }] : undefined,
        type === 'title' ? [styles.title, { fontFamily: fonts.sansBold }] : undefined,
        type === 'defaultSemiBold' ? [styles.defaultSemiBold, { fontFamily: fonts.sansSemiBold }] : undefined,
        type === 'subtitle' ? [styles.subtitle, { fontFamily: fonts.sansBold }] : undefined,
        type === 'link' ? [styles.link, { fontFamily: fonts.sans }] : undefined,
        style,
      ]}
      {...rest}
    />
  );
}

const styles = StyleSheet.create({
  default: {
    fontSize: 16,
    lineHeight: 24,
  },
  defaultSemiBold: {
    fontSize: 16,
    lineHeight: 24,
  },
  title: {
    fontSize: 32,
    lineHeight: 32,
  },
  subtitle: {
    fontSize: 20,
  },
  link: {
    lineHeight: 30,
    fontSize: 16,
    color: '#0a7ea4',
  },
});
