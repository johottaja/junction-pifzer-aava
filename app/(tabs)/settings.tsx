import React from 'react';
import { StyleSheet, ScrollView, TouchableOpacity, Switch, Platform } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { Colors } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { IconSymbol } from '@/components/ui/icon-symbol';

export default function SettingsScreen() {
  const colorScheme = useColorScheme();
  const theme = Colors[colorScheme ?? 'light'];
  const [notificationsEnabled, setNotificationsEnabled] = React.useState(true);
  const [remindersEnabled, setRemindersEnabled] = React.useState(false);
  const [analyticsEnabled, setAnalyticsEnabled] = React.useState(true);

  const settingsSections = [
    {
      title: 'Notifications',
      items: [
        {
          icon: 'bell.fill',
          label: 'Push Notifications',
          value: notificationsEnabled,
          onToggle: setNotificationsEnabled,
          type: 'toggle',
        },
        {
          icon: 'clock.fill',
          label: 'Reminder Alerts',
          value: remindersEnabled,
          onToggle: setRemindersEnabled,
          type: 'toggle',
        },
      ],
    },
    {
      title: 'Data & Privacy',
      items: [
        {
          icon: 'chart.bar.fill',
          label: 'Analytics',
          value: analyticsEnabled,
          onToggle: setAnalyticsEnabled,
          type: 'toggle',
        },
        {
          icon: 'lock.fill',
          label: 'Privacy Policy',
          type: 'navigation',
        },
        {
          icon: 'doc.text.fill',
          label: 'Terms of Service',
          type: 'navigation',
        },
      ],
    },
    {
      title: 'About',
      items: [
        {
          icon: 'info.circle.fill',
          label: 'App Version',
          value: '1.0.0',
          type: 'text',
        },
        {
          icon: 'questionmark.circle.fill',
          label: 'Help & Support',
          type: 'navigation',
        },
        {
          icon: 'star.fill',
          label: 'Rate App',
          type: 'navigation',
        },
      ],
    },
  ];

  const handleNavigation = (label: string) => {
    // TODO: Implement navigation logic
    console.log('Navigate to:', label);
  };

  const SettingItem = ({ item }: { item: any }) => {
    return (
      <TouchableOpacity
        style={[
          styles.settingItem,
          {
            backgroundColor: theme.card,
            borderColor: theme.cardBorder,
          },
        ]}
        onPress={() => {
          if (item.type === 'navigation') {
            handleNavigation(item.label);
          } else if (item.type === 'toggle' && item.onToggle) {
            item.onToggle(!item.value);
          }
        }}
        disabled={item.type === 'text'}
      >
        <ThemedView style={styles.settingItemLeft}>
          <ThemedView
            style={[
              styles.iconContainer,
              { backgroundColor: theme.backgroundSecondary },
            ]}
          >
            <IconSymbol name={item.icon} size={20} color={theme.primary} />
          </ThemedView>
          <ThemedText style={styles.settingLabel}>{item.label}</ThemedText>
        </ThemedView>
        <ThemedView style={styles.settingItemRight}>
          {item.type === 'toggle' && (
            <Switch
              value={item.value}
              onValueChange={item.onToggle}
              trackColor={{ false: theme.border, true: theme.primary }}
              thumbColor={item.value ? '#FFFFFF' : theme.textSecondary}
            />
          )}
          {item.type === 'text' && (
            <ThemedText style={[styles.settingValue, { color: theme.textSecondary }]}>
              {item.value}
            </ThemedText>
          )}
          {item.type === 'navigation' && (
            <IconSymbol name="chevron.right" size={16} color={theme.textSecondary} />
          )}
        </ThemedView>
      </TouchableOpacity>
    );
  };

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.background }]} edges={['top']}>
      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        <ThemedView style={styles.header}>
          <ThemedText type="title" style={styles.title}>Settings</ThemedText>
          <ThemedText style={[styles.subtitle, { color: theme.textSecondary }]}>
            Manage your app preferences
          </ThemedText>
        </ThemedView>

        {settingsSections.map((section, sectionIndex) => (
          <ThemedView key={sectionIndex} style={styles.section}>
            <ThemedText style={[styles.sectionTitle, { color: theme.textSecondary }]}>
              {section.title}
            </ThemedText>
            <ThemedView style={styles.sectionContent}>
              {section.items.map((item, itemIndex) => (
                <SettingItem key={itemIndex} item={item} />
              ))}
            </ThemedView>
          </ThemedView>
        ))}

        <ThemedView style={styles.footer}>
          <ThemedText style={[styles.footerText, { color: theme.textSecondary }]}>
            Migraine Tracker v1.0.0
          </ThemedText>
          <ThemedText style={[styles.footerText, { color: theme.textSecondary }]}>
            Built with care for your health
          </ThemedText>
        </ThemedView>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    padding: 20,
    paddingBottom: 40,
  },
  header: {
    marginBottom: 32,
  },
  title: {
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
  },
  section: {
    marginBottom: 32,
  },
  sectionTitle: {
    fontSize: 13,
    fontWeight: '600',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
    marginBottom: 12,
    paddingHorizontal: 4,
  },
  sectionContent: {
    gap: 8,
  },
  settingItem: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    ...Platform.select({
      ios: {
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 1 },
        shadowOpacity: 0.05,
        shadowRadius: 4,
      },
      android: {
        elevation: 1,
      },
    }),
  },
  settingItemLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
    gap: 12,
  },
  iconContainer: {
    width: 36,
    height: 36,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
  },
  settingLabel: {
    fontSize: 16,
    fontWeight: '500',
  },
  settingItemRight: {
    alignItems: 'center',
    justifyContent: 'center',
  },
  settingValue: {
    fontSize: 14,
  },
  footer: {
    alignItems: 'center',
    marginTop: 20,
    gap: 4,
  },
  footerText: {
    fontSize: 12,
  },
});

