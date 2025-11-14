import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { IconSymbol } from '@/components/ui/icon-symbol';
import { Colors } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { Link } from 'expo-router';
import React from 'react';
import { ScrollView, StyleSheet, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

// Helper function to add opacity to hex colors
const hexToRgba = (hex: string, alpha: number): string => {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
};

export default function TodayScreen() {
  const colorScheme = useColorScheme();
  const theme = Colors[colorScheme ?? 'light'];

  // Get today's date
  const today = new Date();
  const dayName = today.toLocaleDateString('en-US', { weekday: 'long' });
  const monthName = today.toLocaleDateString('en-US', { month: 'long' });
  const dayNumber = today.getDate();

  // Mock data - will be replaced with actual data
  const todayStats = {
    hasMigraine: false,
    lastEpisode: '3 days ago',
    streak: 3,
    weeklyAverage: 2.5,
  };

  const quickActions = [
    { icon: 'plus.circle.fill', label: 'Report Migraine', route: '/(tabs)/report', color: theme.primary },
    { icon: 'chart.line.uptrend.xyaxis', label: 'View Predictions', route: '/(tabs)/prediction', color: theme.secondary },
  ];

  const recentActivity = [
    { time: '2 days ago', intensity: 7, trigger: 'Stress' },
    { time: '5 days ago', intensity: 5, trigger: 'Sleep' },
    { time: '1 week ago', intensity: 8, trigger: 'Weather' },
  ];

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.background }]} edges={['top']}>
      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        <ThemedView style={styles.header}>
          <ThemedText style={[styles.greeting, { color: theme.textSecondary }]}>Today</ThemedText>
          <ThemedText type="title" style={styles.dateTitle}>
            {dayName}, {monthName} {dayNumber}
          </ThemedText>
        </ThemedView>

        {todayStats.hasMigraine ? (
          <ThemedView
            style={{
              ...styles.alertCard,
              backgroundColor: hexToRgba(theme.error, 0.08),
              borderColor: hexToRgba(theme.error, 0.25),
            }}
          >
            <IconSymbol name="exclamationmark.triangle.fill" size={24} color={theme.error} />
            <ThemedView style={styles.alertContent}>
              <ThemedText style={[styles.alertTitle, { color: theme.error }]}>
                Active Migraine
              </ThemedText>
              <ThemedText style={[styles.alertText, { color: theme.textSecondary }]}>
                You reported a migraine today. Track your symptoms and triggers.
              </ThemedText>
            </ThemedView>
          </ThemedView>
        ) : (
          <ThemedView
            style={{
              ...styles.statusCard,
              backgroundColor: hexToRgba(theme.success, 0.08),
              borderColor: hexToRgba(theme.success, 0.25),
            }}
          >
            <IconSymbol name="checkmark.circle.fill" size={24} color={theme.success} />
            <ThemedView style={styles.statusContent}>
              <ThemedText style={[styles.statusTitle, { color: theme.success }]}>
                No Migraine Today
              </ThemedText>
              <ThemedText style={[styles.statusText, { color: theme.textSecondary }]}>
                Last episode was {todayStats.lastEpisode}
              </ThemedText>
            </ThemedView>
          </ThemedView>
        )}

        <ThemedView style={styles.section}>
          <ThemedText type="subtitle" style={styles.sectionTitle}>Quick Actions</ThemedText>
          <ThemedView style={styles.actionsGrid}>
            {quickActions.map((action, index) => {
              const actionCardStyle = {
                ...styles.actionCard,
                backgroundColor: theme.card,
                borderColor: theme.cardBorder,
              };
              const iconContainerStyle = {
                ...styles.actionIconContainer,
                backgroundColor: hexToRgba(action.color, 0.12),
              };
              return (
                <Link key={index} href={action.route} asChild>
                  <TouchableOpacity style={actionCardStyle}>
                    <ThemedView style={iconContainerStyle}>
                      <IconSymbol name={action.icon} size={24} color={action.color} />
                    </ThemedView>
                    <ThemedText style={styles.actionLabel}>{action.label}</ThemedText>
                  </TouchableOpacity>
                </Link>
              );
            })}
          </ThemedView>
        </ThemedView>

        <ThemedView style={styles.section}>
          <ThemedText type="subtitle" style={styles.sectionTitle}>Today's Stats</ThemedText>
          <ThemedView
            style={{
              ...styles.statsCard,
              backgroundColor: theme.card,
              borderColor: theme.cardBorder,
            }}
          >
            <ThemedView style={styles.statRow}>
              <ThemedView style={styles.statItem}>
                <ThemedText style={[styles.statValue, { color: theme.primary }]}>
                  {todayStats.streak}
                </ThemedText>
                <ThemedText style={[styles.statLabel, { color: theme.textSecondary }]}>
                  Day Streak
                </ThemedText>
              </ThemedView>
              <ThemedView style={[styles.statDivider, { backgroundColor: theme.border }]} />
              <ThemedView style={styles.statItem}>
                <ThemedText style={[styles.statValue, { color: theme.secondary }]}>
                  {todayStats.weeklyAverage}
                </ThemedText>
                <ThemedText style={[styles.statLabel, { color: theme.textSecondary }]}>
                  Weekly Avg
                </ThemedText>
              </ThemedView>
            </ThemedView>
          </ThemedView>
        </ThemedView>

        <ThemedView style={styles.section}>
          <ThemedText type="subtitle" style={styles.sectionTitle}>Recent Activity</ThemedText>
          <ThemedView
            style={{
              ...styles.activityCard,
              backgroundColor: theme.card,
              borderColor: theme.cardBorder,
            }}
          >
            {recentActivity.map((activity, index) => (
              <ThemedView
                key={index}
                style={{
                  ...styles.activityItem,
                  ...(index !== recentActivity.length - 1 && {
                    borderBottomColor: theme.border,
                    borderBottomWidth: 1,
                    paddingBottom: 16,
                    marginBottom: 16,
                  }),
                }}
              >
                <ThemedView style={styles.activityLeft}>
                  <ThemedView
                    style={{
                      ...styles.activityIcon,
                      backgroundColor: theme.backgroundSecondary,
                    }}
                  >
                    <IconSymbol name="bolt.fill" size={16} color={theme.warning} />
                  </ThemedView>
                  <ThemedView style={styles.activityInfo}>
                    <ThemedText style={styles.activityIntensity}>
                      Intensity: {activity.intensity}/10
                    </ThemedText>
                    <ThemedText style={[styles.activityTrigger, { color: theme.textSecondary }]}>
                      {activity.trigger}
                    </ThemedText>
                  </ThemedView>
                </ThemedView>
                <ThemedText style={[styles.activityTime, { color: theme.textSecondary }]}>
                  {activity.time}
                </ThemedText>
              </ThemedView>
            ))}
          </ThemedView>
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
    marginBottom: 24,
  },
  greeting: {
    fontSize: 14,
    textTransform: 'uppercase',
    letterSpacing: 0.5,
    marginBottom: 4,
  },
  dateTitle: {
    fontSize: 28,
  },
  alertCard: {
    flexDirection: 'row',
    padding: 20,
    borderRadius: 20,
    borderWidth: 1,
    marginBottom: 24,
    gap: 14,
    alignItems: 'flex-start',
  },
  alertContent: {
    flex: 1,
  },
  alertTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 4,
  },
  alertText: {
    fontSize: 14,
    lineHeight: 20,
  },
  statusCard: {
    flexDirection: 'row',
    padding: 20,
    borderRadius: 20,
    borderWidth: 1,
    marginBottom: 24,
    gap: 14,
    alignItems: 'flex-start',
  },
  statusContent: {
    flex: 1,
    backgroundColor: "transparent",
  },
  statusTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 4,
  },
  statusText: {
    fontSize: 14,
    lineHeight: 20,
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    marginBottom: 12,
  },
  actionsGrid: {
    flexDirection: 'row',
    gap: 12,
    flexWrap: 'wrap',
  },
  actionCard: {
    flex: 1,
    minWidth: '30%',
    padding: 18,
    borderRadius: 20,
    borderWidth: 1,
    alignItems: 'center',
    gap: 10,
  },
  actionIconContainer: {
    width: 52,
    height: 52,
    borderRadius: 16,
    alignItems: 'center',
    justifyContent: 'center',
  },
  actionLabel: {
    fontSize: 12,
    fontWeight: '500',
    textAlign: 'center',
  },
  statsCard: {
    padding: 24,
    borderRadius: 20,
    borderWidth: 1,
    backgroundColor: "transparent",
  },
  statRow: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: "transparent",
  },
  statItem: {
    flex: 1,
    alignItems: 'center',
    backgroundColor: "transparent",
  },
  statValue: {
    paddingTop: 15,
    fontSize: 32,
    fontWeight: '700',
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 14,
  },
  statDivider: {
    width: 1,
    height: 40,
    marginHorizontal: 20,
    backgroundColor: "transparent",
  },
  activityCard: {
    padding: 24,
    borderRadius: 20,
    borderWidth: 1,
  },
  activityItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: "transparent",
  },
  activityLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    flex: 1,
    backgroundColor: "transparent",
  },
  activityIcon: {
    width: 36,
    height: 36,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: "transparent",
  },
  activityInfo: {
    flex: 1,
    backgroundColor: "transparent",
  },
  activityIntensity: {
    fontSize: 15,
    fontWeight: '600',
    marginBottom: 2,
  },
  activityTrigger: {
    fontSize: 13,
  },
  activityTime: {
    fontSize: 12,
  },
});

