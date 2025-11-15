import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { IconSymbol } from '@/components/ui/icon-symbol';
import { Colors } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';
import React, { useEffect, useState } from 'react';
import { ActivityIndicator, ScrollView, StyleSheet } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

// Helper function to add opacity to hex colors
const hexToRgba = (hex: string, alpha: number): string => {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
};

// Mock API functions
const fetchMigraineRisk = async (): Promise<{
  riskLevel: 'low' | 'medium' | 'high';
  riskPercentage: number;
  factors: string[];
  message: string;
}> => {
  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 500));
  
  // Hardcoded mock response
  return {
    riskLevel: 'medium',
    riskPercentage: 45,
    factors: ['Weather changes', 'Stress levels elevated', 'Sleep quality decreased'],
    message: 'Your migraine risk is moderate today. Consider taking preventive measures.',
  };
};

const fetchRecommendedActions = async (): Promise<{
  actions: Array<{
    id: string;
    title: string;
    description: string;
    icon: string;
    priority: 'high' | 'medium' | 'low';
  }>;
}> => {
  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 500));
  
  // Hardcoded mock response
  return {
    actions: [
      {
        id: '1',
        title: 'Drink Water',
        description: 'Stay hydrated throughout the day',
        icon: 'drop.fill',
        priority: 'high',
      },
      {
        id: '2',
        title: 'Exercise',
        description: 'Light exercise can help reduce stress',
        icon: 'figure.run',
        priority: 'high',
      },
      {
        id: '3',
        title: 'Take Breaks',
        description: 'Rest your eyes every 20 minutes',
        icon: 'eye.fill',
        priority: 'medium',
      },
      {
        id: '4',
        title: 'Manage Stress',
        description: 'Practice deep breathing exercises',
        icon: 'lungs.fill',
        priority: 'medium',
      },
    ],
  };
};

const fetchWeeklyRiskForecast = async (): Promise<Array<{
  date: string; // ISO date string
  dayName: string; // e.g., "Monday"
  dayNumber: number; // e.g., 15
  monthName: string; // e.g., "January"
  riskLevel: 'low' | 'medium' | 'high';
  riskPercentage: number;
}>> => {
  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 500));
  
  // Generate 3 days starting from today
  const days = [];
  const today = new Date();
  
  for (let i = 0; i < 3; i++) {
    const date = new Date(today);
    date.setDate(today.getDate() + i);
    
    // Mock risk levels - varying for demonstration
    const riskLevels: Array<'low' | 'medium' | 'high'> = ['low', 'medium', 'high'];
    const riskPercentages = [25, 45, 70];
    const riskIndex = i % 3;
    
    days.push({
      date: date.toISOString().split('T')[0],
      dayName: date.toLocaleDateString('en-US', { weekday: 'short' }),
      dayNumber: date.getDate(),
      monthName: date.toLocaleDateString('en-US', { month: 'short' }),
      riskLevel: riskLevels[riskIndex],
      riskPercentage: riskPercentages[riskIndex],
    });
  }
  
  return days;
};

export default function TodayScreen() {
  const colorScheme = useColorScheme();
  const theme = Colors[colorScheme ?? 'light'];

  const [riskData, setRiskData] = useState<{
    riskLevel: 'low' | 'medium' | 'high';
    riskPercentage: number;
    factors: string[];
    message: string;
  } | null>(null);
  const [recommendedActions, setRecommendedActions] = useState<Array<{
    id: string;
    title: string;
    description: string;
    icon: string;
    priority: 'high' | 'medium' | 'low';
  }>>([]);
  const [weeklyForecast, setWeeklyForecast] = useState<Array<{
    date: string;
    dayName: string;
    dayNumber: number;
    monthName: string;
    riskLevel: 'low' | 'medium' | 'high';
    riskPercentage: number;
  }>>([]);
  const [loading, setLoading] = useState(true);

  // Get today's date
  const today = new Date();
  const dayName = today.toLocaleDateString('en-US', { weekday: 'long' });
  const monthName = today.toLocaleDateString('en-US', { month: 'long' });
  const dayNumber = today.getDate();

  const recentActivity = [
    { time: '2 days ago', intensity: 7, trigger: 'Stress' },
    { time: '5 days ago', intensity: 5, trigger: 'Sleep' },
    { time: '1 week ago', intensity: 8, trigger: 'Weather' },
  ];

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        const [riskResponse, actionsResponse, forecastResponse] = await Promise.all([
          fetchMigraineRisk(),
          fetchRecommendedActions(),
          fetchWeeklyRiskForecast(),
        ]);
        setRiskData(riskResponse);
        setRecommendedActions(actionsResponse.actions);
        setWeeklyForecast(forecastResponse);
      } catch (error) {
        console.error('Error loading data:', error);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel) {
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

  const getRiskIcon = (riskLevel: string) => {
    switch (riskLevel) {
      case 'high':
        return 'exclamationmark.triangle.fill';
      case 'medium':
        return 'exclamationmark.circle.fill';
      case 'low':
        return 'checkmark.circle.fill';
      default:
        return 'info.circle.fill';
    }
  };

  return (
    <SafeAreaView style={{ ...styles.container, backgroundColor: theme.background }} edges={['top']}>
      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        <ThemedView style={styles.header}>
          <ThemedText style={{ ...styles.greeting, color: theme.textSecondary }}>Today</ThemedText>
          <ThemedText type="title" style={styles.dateTitle}>
            {dayName}, {monthName} {dayNumber}
          </ThemedText>
        </ThemedView>

        {loading ? (
          <ThemedView style={styles.loadingContainer}>
            <ActivityIndicator size="large" color={theme.primary} />
            <ThemedText style={{ ...styles.loadingText, color: theme.textSecondary }}>
              Loading your risk assessment...
            </ThemedText>
          </ThemedView>
        ) : (
          <>
            {riskData && (
              <ThemedView
                style={{
                  ...styles.riskCard,
                  backgroundColor: hexToRgba(getRiskColor(riskData.riskLevel), 0.08),
                  borderColor: hexToRgba(getRiskColor(riskData.riskLevel), 0.25),
                }}
              >
                <IconSymbol name={getRiskIcon(riskData.riskLevel)} size={28} color={getRiskColor(riskData.riskLevel)} />
                <ThemedView style={styles.riskContent}>
                  <ThemedView style={styles.riskHeader}>
                    <ThemedText style={{ ...styles.riskTitle, color: getRiskColor(riskData.riskLevel) }}>
                      {riskData.riskLevel.charAt(0).toUpperCase() + riskData.riskLevel.slice(1)} Risk Today
                    </ThemedText>
                    <ThemedText style={{ ...styles.riskPercentage, color: getRiskColor(riskData.riskLevel) }}>
                      {riskData.riskPercentage}%
                    </ThemedText>
                  </ThemedView>
                  <ThemedText style={{ ...styles.riskMessage, color: theme.text }}>
                    {riskData.message}
                  </ThemedText>
                </ThemedView>
              </ThemedView>
            )}

            {weeklyForecast.length > 0 && (
              <ThemedView style={styles.section}>
                <ThemedText type="subtitle" style={styles.sectionTitle}>3-Day Forecast</ThemedText>
                <ThemedView
                  style={{
                    ...styles.calendarCard,
                    backgroundColor: theme.card,
                    borderColor: theme.cardBorder,
                  }}
                >
                  {weeklyForecast.map((day, index) => {
                    const isToday = index === 0;
                    const riskColor = getRiskColor(day.riskLevel);
                    return (
                      <ThemedView
                        key={day.date}
                        style={{
                          ...styles.calendarDay,
                          ...(index !== weeklyForecast.length - 1 && {
                            borderRightColor: theme.border,
                            borderRightWidth: 1,
                            marginRight: 12,
                            paddingRight: 12,
                          }),
                        }}
                      >
                        <ThemedView style={styles.dayHeader}>
                          <ThemedView style={styles.dayInfo}>
                            <ThemedText style={{ ...styles.dayName, color: isToday ? theme.primary : theme.text }}>
                              {day.dayName}
                            </ThemedText>
                            <ThemedText style={{ ...styles.dayDate, color: theme.textSecondary }}>
                              {day.dayNumber}
                            </ThemedText>
                            {isToday && (
                              <ThemedView
                                style={{
                                  ...styles.todayBadge,
                                  backgroundColor: hexToRgba(theme.primary, 0.12),
                                }}
                              >
                                <ThemedText style={{ ...styles.todayBadgeText, color: theme.primary }}>
                                  Today
                                </ThemedText>
                              </ThemedView>
                            )}
                          </ThemedView>
                        </ThemedView>
                        <ThemedView style={styles.riskIndicator}>
                          <ThemedView
                            style={{
                              ...styles.riskBar,
                              backgroundColor: hexToRgba(riskColor, 0.15),
                            }}
                          >
                            <ThemedView
                              style={{
                                ...styles.riskBarFill,
                                width: `${day.riskPercentage}%`,
                                backgroundColor: riskColor,
                              }}
                            />
                          </ThemedView>
                          <ThemedView style={styles.riskInfo}>
                            <ThemedText style={{ ...styles.riskLabel, color: riskColor }}>
                              {day.riskLevel.charAt(0).toUpperCase() + day.riskLevel.slice(1)}
                            </ThemedText>
                            <ThemedText style={{ ...styles.riskPercent, color: theme.textSecondary }}>
                              {day.riskPercentage}%
                            </ThemedText>
                          </ThemedView>
                        </ThemedView>
                      </ThemedView>
                    );
                  })}
                </ThemedView>
              </ThemedView>
            )}

            <ThemedView style={styles.section}>
              <ThemedText type="subtitle" style={styles.sectionTitle}>Recommended Actions</ThemedText>
              <ThemedView style={styles.actionsList}>
                {recommendedActions.map((action) => {
                  const priorityColor = action.priority === 'high' ? theme.primary : theme.secondary;
                  return (
                    <ThemedView
                      key={action.id}
                      style={{
                        ...styles.actionItem,
                        backgroundColor: theme.card,
                        borderColor: theme.cardBorder,
                      }}
                    >
                      <ThemedView
                        style={{
                          ...styles.actionIconContainer,
                          backgroundColor: hexToRgba(priorityColor, 0.12),
                        }}
                      >
                        <IconSymbol name={action.icon as any} size={24} color={priorityColor} />
                      </ThemedView>
                      <ThemedView style={{ ...styles.actionContent, backgroundColor: "transparent" }}>
                        <ThemedText style={{ ...styles.actionTitle, backgroundColor: "transparent" }}>{action.title}</ThemedText>
                        <ThemedText style={{ ...styles.actionDescription, color: theme.textSecondary, backgroundColor: "transparent" }}>
                          {action.description}
                        </ThemedText>
                      </ThemedView>
                      
                    </ThemedView>
                  );
                })}
              </ThemedView>
            </ThemedView>
          </>
        )}

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
  loadingContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    padding: 40,
    marginBottom: 24,
  },
  loadingText: {
    marginTop: 12,
    fontSize: 14,
  },
  riskCard: {
    flexDirection: 'row',
    padding: 20,
    borderRadius: 20,
    borderWidth: 1,
    marginBottom: 24,
    gap: 16,
    alignItems: 'flex-start',
  },
  riskContent: {
    flex: 1,
    backgroundColor: "transparent",
  },
  riskHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
    backgroundColor: "transparent",
  },
  riskTitle: {
    fontSize: 18,
    fontWeight: '600',
  },
  riskPercentage: {
    fontSize: 24,
    fontWeight: '700',
  },
  riskMessage: {
    fontSize: 14,
    lineHeight: 20,
    marginBottom: 12,
  },
  timeWindowContainer: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 10,
    marginTop: 12,
    marginBottom: 12,
    padding: 12,
    borderRadius: 12,
    backgroundColor: 'rgba(0, 0, 0, 0.02)',
  },
  timeWindowContent: {
    flex: 1,
    backgroundColor: "transparent",
  },
  timeWindowLabel: {
    fontSize: 12,
    fontWeight: '500',
    marginBottom: 4,
  },
  timeWindowValue: {
    fontSize: 14,
    fontWeight: '600',
  },
  calendarCard: {
    flexDirection: 'row',
    padding: 16,
    borderRadius: 20,
    borderWidth: 1,
    gap: 0,
  },
  calendarDay: {
    flex: 1,
    alignItems: 'center',
    gap: 8,
  },
  dayHeader: {
    alignItems: 'center',
    width: '100%',
  },
  dayInfo: {
    alignItems: 'center',
    gap: 4,
    width: '100%',
  },
  dayName: {
    fontSize: 13,
    fontWeight: '600',
  },
  dayDate: {
    fontSize: 18,
    fontWeight: '700',
  },
  todayBadge: {
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 8,
    marginTop: 4,
  },
  todayBadgeText: {
    fontSize: 9,
    fontWeight: '600',
    textTransform: 'uppercase',
  },
  riskIndicator: {
    width: '100%',
    gap: 6,
    alignItems: 'center',
  },
  riskBar: {
    width: '100%',
    height: 4,
    borderRadius: 2,
    overflow: 'hidden',
  },
  riskBarFill: {
    height: '100%',
    borderRadius: 2,
  },
  riskInfo: {
    flexDirection: 'column',
    alignItems: 'center',
    gap: 2,
  },
  riskLabel: {
    fontSize: 11,
    fontWeight: '600',
  },
  riskPercent: {
    fontSize: 12,
    fontWeight: '500',
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    marginBottom: 12,
  },
  actionsList: {
    gap: 12,
  },
  actionItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    borderRadius: 16,
    borderWidth: 1,
    gap: 12,
    backgroundColor: "transparent",
  },
  actionIconContainer: {
    width: 48,
    height: 48,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: "transparent",
  },
  actionContent: {
    flex: 1,
  },
  actionTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 4,
  },
  actionDescription: {
    fontSize: 13,
    lineHeight: 18,
  },
  priorityBadge: {
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
  },
  priorityText: {
    fontSize: 11,
    fontWeight: '600',
    textTransform: 'uppercase',
  },
  statsCard: {
    padding: 24,
    borderRadius: 20,
    borderWidth: 1,
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
    fontSize: 32,
    fontWeight: '700',
    marginBottom: 4,
    backgroundColor: "transparent",
  },
  statLabel: {
    fontSize: 14,
    backgroundColor: "transparent",
  },
  statDivider: {
    width: 1,
    height: 40,
    marginHorizontal: 20,
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

