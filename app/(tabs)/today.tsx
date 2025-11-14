import React from 'react';
import { StyleSheet, ScrollView, TouchableOpacity, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { Colors } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { IconSymbol } from '@/components/ui/icon-symbol';
import { Platform } from 'react-native';
import { Link } from 'expo-router';

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
            style={[
              styles.alertCard,
              {
                backgroundColor: theme.error + '15',
                borderColor: theme.error + '40',
              },
            ]}
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
            style={[
              styles.statusCard,
              {
                backgroundColor: theme.success + '15',
                borderColor: theme.success + '40',
              },
            ]}
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
            {quickActions.map((action, index) => (
              <Link key={index} href={action.route} asChild>
                <TouchableOpacity
                  style={[
                    styles.actionCard,
                    {
                      backgroundColor: theme.card,
                      borderColor: theme.cardBorder,
                    },
                  ]}
                >
                  <ThemedView
                    style={[
                      styles.actionIconContainer,
                      { backgroundColor: action.color + '20' },
                    ]}
                  >
                    <IconSymbol name={action.icon} size={24} color={action.color} />
                  </ThemedView>
                  <ThemedText style={styles.actionLabel}>{action.label}</ThemedText>
                </TouchableOpacity>
              </Link>
            ))}
          </ThemedView>
        </ThemedView>

        <ThemedView style={styles.section}>
          <ThemedText type="subtitle" style={styles.sectionTitle}>Today's Stats</ThemedText>
          <ThemedView
            style={[
              styles.statsCard,
              {
                backgroundColor: theme.card,
                borderColor: theme.cardBorder,
              },
            ]}
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
            style={[
              styles.activityCard,
              {
                backgroundColor: theme.card,
                borderColor: theme.cardBorder,
              },
            ]}
          >
            {recentActivity.map((activity, index) => (
              <ThemedView
                key={index}
                style={[
                  styles.activityItem,
                  index !== recentActivity.length - 1 && {
                    borderBottomColor: theme.border,
                    borderBottomWidth: 1,
                    paddingBottom: 16,
                    marginBottom: 16,
                  },
                ]}
              >
                <ThemedView style={styles.activityLeft}>
                  <ThemedView
                    style={[
                      styles.activityIcon,
                      { backgroundColor: theme.backgroundSecondary },
                    ]}
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
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    marginBottom: 24,
    gap: 12,
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
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    marginBottom: 24,
    gap: 12,
    alignItems: 'flex-start',
  },
  statusContent: {
    flex: 1,
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
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    alignItems: 'center',
    gap: 8,
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
  actionIconContainer: {
    width: 48,
    height: 48,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  actionLabel: {
    fontSize: 12,
    fontWeight: '500',
    textAlign: 'center',
  },
  statsCard: {
    padding: 20,
    borderRadius: 12,
    borderWidth: 1,
    ...Platform.select({
      ios: {
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 8,
      },
      android: {
        elevation: 2,
      },
    }),
  },
  statRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statItem: {
    flex: 1,
    alignItems: 'center',
  },
  statValue: {
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
  },
  activityCard: {
    padding: 20,
    borderRadius: 12,
    borderWidth: 1,
    ...Platform.select({
      ios: {
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 8,
      },
      android: {
        elevation: 2,
      },
    }),
  },
  activityItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  activityLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    flex: 1,
  },
  activityIcon: {
    width: 32,
    height: 32,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
  },
  activityInfo: {
    flex: 1,
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

