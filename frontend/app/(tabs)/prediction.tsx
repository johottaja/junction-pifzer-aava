import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { IconSymbol } from '@/components/ui/icon-symbol';
import { Colors } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';
import React from 'react';
import { ScrollView, StyleSheet, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

// Helper function to add opacity to hex colors
const hexToRgba = (hex: string, alpha: number): string => {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
};

export default function PredictionScreen() {
  const colorScheme = useColorScheme();
  const theme = Colors[colorScheme ?? 'light'];

  // Mock data - will be replaced with actual predictions
  const upcomingPredictions = [
    { date: 'Today', time: '2:00 PM', probability: 75, risk: 'high' },
    { date: 'Tomorrow', time: '10:00 AM', probability: 45, risk: 'medium' },
    { date: 'Dec 28', time: '3:30 PM', probability: 30, risk: 'low' },
  ];

  const stats = {
    totalEpisodes: 12,
    averageIntensity: 6.5,
    mostCommonTrigger: 'Stress',
    averageDuration: '8 hours',
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'high':
        return theme.error;
      case 'medium':
        return theme.warning;
      case 'low':
        return theme.success;
      default:
        return theme.textSecondary;
    }
  };

  const getRiskLabel = (risk: string) => {
    switch (risk) {
      case 'high':
        return 'High Risk';
      case 'medium':
        return 'Medium Risk';
      case 'low':
        return 'Low Risk';
      default:
        return 'Unknown';
    }
  };

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.background }]} edges={['top']}>
      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        <ThemedView style={styles.header}>
          <ThemedText type="title" style={styles.title}>Predictions</ThemedText>
          <ThemedText style={[styles.subtitle, { color: theme.textSecondary, backgroundColor: "transparent" }]}>
            AI-powered migraine forecasts
          </ThemedText>
        </ThemedView>

        <ThemedView style={[styles.card, { backgroundColor: theme.card, borderColor: theme.cardBorder }]}>
          <ThemedView style={styles.cardHeader}>
            <IconSymbol name="brain.head.profile" size={24} color={theme.primary} />
            <ThemedText type="subtitle" style={styles.cardTitle}>Upcoming Predictions</ThemedText>
          </ThemedView>
          <ThemedText style={[styles.cardDescription, { color: theme.textSecondary }]}>
            Based on your historical data and patterns
          </ThemedText>

          <ThemedView style={styles.predictionsList}>
            {upcomingPredictions.map((prediction, index) => (
              <ThemedView
                key={index}
                style={[
                  styles.predictionItem,
                  {
                    backgroundColor: theme.backgroundSecondary,
                    borderColor: theme.border,
                  },
                ]}
              >
                <ThemedView style={styles.predictionHeader}>
                  <ThemedView style={{ backgroundColor: "transparent" }}>
                    <ThemedText style={styles.predictionDate}>{prediction.date}</ThemedText>
                    <ThemedText style={[styles.predictionTime, { color: theme.textSecondary }]}>
                      {prediction.time}
                    </ThemedText>
                  </ThemedView>
                  <ThemedView
                    style={[
                      styles.riskBadge,
                      { backgroundColor: hexToRgba(getRiskColor(prediction.risk), 0.12) },
                    ]}
                  >
                    <ThemedText
                      style={[styles.riskText, { color: getRiskColor(prediction.risk) }]}
                    >
                      {getRiskLabel(prediction.risk)}
                    </ThemedText>
                  </ThemedView>
                </ThemedView>
                <ThemedView style={styles.probabilityContainer}>
                  <ThemedView style={styles.probabilityBar}>
                    <View
                      style={[
                        styles.probabilityFill,
                        {
                          width: `${prediction.probability}%`,
                          backgroundColor: getRiskColor(prediction.risk),
                        },
                      ]}
                    />
                  </ThemedView>
                  <ThemedText style={[styles.probabilityText, { color: theme.textSecondary }]}>
                    {prediction.probability}% probability
                  </ThemedText>
                </ThemedView>
              </ThemedView>
            ))}
          </ThemedView>
        </ThemedView>

        <ThemedView style={[styles.card, { backgroundColor: theme.card, borderColor: theme.cardBorder }]}>
          <ThemedView style={styles.cardHeader}>
            <IconSymbol name="chart.bar.fill" size={24} color={theme.secondary} />
            <ThemedText type="subtitle" style={styles.cardTitle}>Your Statistics</ThemedText>
          </ThemedView>

          <ThemedView style={styles.statsGrid}>
            <ThemedView style={[styles.statItem, { backgroundColor: theme.backgroundSecondary }]}>
              <ThemedText style={[styles.statValue, { color: theme.primary }]}>
                {stats.totalEpisodes}
              </ThemedText>
              <ThemedText style={[styles.statLabel, { color: theme.textSecondary }]}>
                Total Episodes
              </ThemedText>
            </ThemedView>

            <ThemedView style={[styles.statItem, { backgroundColor: theme.backgroundSecondary }]}>
              <ThemedText style={[styles.statValue, { color: theme.secondary }]}>
                {stats.averageIntensity}
              </ThemedText>
              <ThemedText style={[styles.statLabel, { color: theme.textSecondary }]}>
                Avg Intensity
              </ThemedText>
            </ThemedView>

            <ThemedView style={[styles.statItem, { backgroundColor: theme.backgroundSecondary }]}>
              <ThemedText style={[styles.statValue, { color: theme.accent }]}>
                {stats.averageDuration}
              </ThemedText>
              <ThemedText style={[styles.statLabel, { color: theme.textSecondary }]}>
                Avg Duration
              </ThemedText>
            </ThemedView>

            <ThemedView style={[styles.statItem, { backgroundColor: theme.backgroundSecondary }]}>
              <ThemedText style={[styles.statValue, { color: theme.info }]}>
                {stats.mostCommonTrigger}
              </ThemedText>
              <ThemedText style={[styles.statLabel, { color: theme.textSecondary }]}>
                Top Trigger
              </ThemedText>
            </ThemedView>
          </ThemedView>
        </ThemedView>

        <ThemedView
          style={[
            styles.infoCard,
            {
              backgroundColor: theme.backgroundSecondary,
              borderColor: theme.border,
            },
          ]}
        >
          <IconSymbol name="info.circle.fill" size={20} color={theme.info} />
          <ThemedText style={[styles.infoText, { color: theme.textSecondary }]}>
            Predictions improve as you log more episodes. Keep tracking for better accuracy.
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
  card: {
    padding: 24,
    borderRadius: 20,
    borderWidth: 1,
    marginBottom: 20,
  },
  cardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    backgroundColor: "transparent",
    marginBottom: 8,
  },
  cardTitle: {
    flex: 1,
    backgroundColor: "transparent",
  },
  cardDescription: {
    fontSize: 14,
    marginBottom: 20,
    backgroundColor: "transparent",
  },
  predictionsList: {
    gap: 12,
    backgroundColor: "transparent",
  },
  predictionItem: {
    padding: 18,
    borderRadius: 16,
    borderWidth: 1,
    backgroundColor: "transparent",
  },
  predictionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
    backgroundColor: "transparent",
  },
  predictionDate: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 4,
    backgroundColor: "transparent",
  },
  predictionTime: {
    fontSize: 14,
    backgroundColor: "transparent",
  },
  riskBadge: {
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 16,
    backgroundColor: "transparent",
  },
  riskText: {
    fontSize: 12,
    fontWeight: '600',
    backgroundColor: "transparent",
  },
  probabilityContainer: {
    gap: 8,
    backgroundColor: "transparent",
  },
  probabilityBar: {
    height: 8,
    borderRadius: 4,
    backgroundColor: '#E5E7EB',
    overflow: 'hidden',
  },
  probabilityFill: {
    height: '100%',
    borderRadius: 3,
  },
  probabilityText: {
    fontSize: 12,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
    backgroundColor: "transparent",
  },
  statItem: {
    flex: 1,
    minWidth: '45%',
    padding: 18,
    borderRadius: 16,
    alignItems: 'center',
  },
  statValue: {
    fontSize: 24,
    fontWeight: '700',
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    textAlign: 'center',
  },
  infoCard: {
    flexDirection: 'row',
    padding: 20,
    borderRadius: 20,
    borderWidth: 1,
    gap: 14,
    alignItems: 'flex-start',
  },
  infoText: {
    flex: 1,
    fontSize: 14,
    lineHeight: 20,
  },
});

