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

// API configuration
// For React Native/Expo: Use your computer's IP address instead of localhost
// Find your IP: Windows (ipconfig), Mac/Linux (ifconfig)
// Example: 'http://192.168.1.100:8000'
// For web/emulator, you can try: 'http://localhost:8000' or 'http://10.0.2.2:8000' (Android emulator)
const API_BASE_URL = __DEV__ 
  ? 'http://localhost:8000' // Change to your IP address for physical device
  : 'https://your-production-api.com'; // Production URL
const DEV_TOKEN = 'dev-token-12345'; // Development token

// Helper function to determine risk level from percentage
const getRiskLevelFromPercentage = (percentage: number): 'low' | 'medium' | 'high' => {
  if (percentage < 40) return 'low';
  if (percentage < 60) return 'medium';
  return 'high';
};

// Helper function to generate message from percentage
const getMessageFromPercentage = (percentage: number): string => {
  if (percentage < 20) {
    return 'Your migraine risk is very low today. Continue monitoring your health.';
  } else if (percentage < 40) {
    return 'Your migraine risk is low today. Maintain good sleep and hydration.';
  } else if (percentage < 60) {
    return 'Your migraine risk is moderate today. Consider taking preventive measures.';
  } else if (percentage < 80) {
    return 'Your migraine risk is high today. Avoid known triggers and ensure adequate rest.';
  } else {
    return 'Your migraine risk is very high today. Take preventive measures and consult your doctor.';
  }
};

// Fetch migraine risk from backend API
const fetchMigraineRisk = async (userId: string = '1'): Promise<{
  riskLevel: 'low' | 'medium' | 'high';
  riskPercentage: number;
  factors: string[];
  message: string;
}> => {
  try {
    const response = await fetch(`${API_BASE_URL}/get-migraine-data/${userId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': DEV_TOKEN, // Use Authorization header (React Native compatible)
      },
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`API error: ${response.status} ${response.statusText} - ${errorText}`);
    }

    const data = await response.json();

    if (!data.success) {
      throw new Error(data.error || 'Failed to fetch migraine data');
    }

    // Extract percentage from response (already a percentage 0-100)
    let riskPercentage = 0;
    let factors: string[] = [];

    if (data.probability !== undefined && data.probability !== null) {
      // Probability is already a percentage (0-100)
      riskPercentage = Math.round(data.probability);
    } else {
      // No probability available
      throw new Error(data.error || 'No prediction data available');
    }

    const riskLevel = getRiskLevelFromPercentage(riskPercentage);
    const message = getMessageFromPercentage(riskPercentage);

    return {
      riskLevel,
      riskPercentage,
      factors,
      message,
    };
  } catch (error) {
    
    // Return default/fallback values on error
    return {
      riskLevel: 'medium',
      riskPercentage: 45,
      factors: ['Unable to fetch prediction data'],
      message: `Unable to load migraine risk data: ${error instanceof Error ? error.message : 'Network error'}. Please check your connection and try again.`,
    };
  }
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
  
  // Generate 2 days starting from today (today and tomorrow)
  const days = [];
  const today = new Date();
  
  for (let i = 0; i < 2; i++) {
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


  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        // TODO: Get actual user_id from auth context/session
        // For now, using hardcoded user_id '1' (matches dev token)
        const userId = '1';
        
        const [riskResponse, actionsResponse, forecastResponse] = await Promise.all([
          fetchMigraineRisk(userId),
          fetchRecommendedActions(),
          fetchWeeklyRiskForecast(),
        ]);
        setRiskData(riskResponse);
        setRecommendedActions(actionsResponse.actions);
        setWeeklyForecast(forecastResponse);
      } catch (error) {
        // Error handled silently
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
          <ThemedText type="title" style={styles.dateTitle}>
            {dayName}, {monthName} {dayNumber}
          </ThemedText>
          <ThemedText style={{ ...styles.greeting, color: theme.textSecondary }}>Hey Julie!</ThemedText>
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
                <ThemedView style={styles.riskMessageContainer}>
                  <ThemedText style={{ ...styles.riskMessage, color: theme.text }}>
                    {riskData.message}
                  </ThemedText>
                </ThemedView>
                <ThemedView style={styles.riskPercentageContainer}>
                  <ThemedText style={{ ...styles.riskPercentage, color: theme.primaryDark }}>
                    {riskData.riskPercentage}%
                  </ThemedText>
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
    fontSize: 20,
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
    gap: 20,
    alignItems: 'center',
    minHeight: 100,
  },
  riskMessageContainer: {
    flex: 1,
    backgroundColor: "transparent",
    justifyContent: 'center',
  },
  riskPercentageContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    minWidth: 120,
    backgroundColor: "transparent",
  },
  riskPercentage: {
    fontSize: 48,
    fontWeight: '800',
    lineHeight: 56,
  },
  riskMessage: {
    fontSize: 15,
    lineHeight: 22,
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
    padding: 20,
    borderRadius: 16,
    borderWidth: 0,
    gap: 0,
    overflow: 'hidden',
  },
  calendarDay: {
    flex: 1,
    alignItems: 'center',
    gap: 12,
    justifyContent: 'flex-start',
    padding: 16,
    borderRadius: 12,
  },
  dayHeader: {
    alignItems: 'center',
    width: '100%',
    backgroundColor: "transparent",
    minHeight: 70,
    justifyContent: 'flex-start',
  },
  dayInfo: {
    alignItems: 'center',
    gap: 4,
    width: '100%',
    backgroundColor: "transparent",
  },
  badgeContainer: {
    minHeight: 20,
    marginTop: 4,
    justifyContent: 'center',
    alignItems: 'center',
  },
  dayName: {
    fontSize: 13,
    fontWeight: '600',
    backgroundColor: "transparent",
  },
  dayDate: {
    fontSize: 18,
    fontWeight: '700',
  },
  todayBadge: {
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 8,
    marginTop: 0,
  },
  todayBadgeText: {
    fontSize: 9,
    fontWeight: '600',
    textTransform: 'uppercase',
  },
  riskIndicator: {
    width: '100%',
    gap: 8,
    alignItems: 'center',
    marginTop: 4,
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
    backgroundColor: "transparent",
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

