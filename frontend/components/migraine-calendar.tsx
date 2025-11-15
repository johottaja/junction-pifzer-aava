import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { ReportModal } from '@/components/report-modal';
import { Colors } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';
import React, { useState } from 'react';
import { StyleSheet, TouchableOpacity, View } from 'react-native';

interface MigraineCalendarProps {
  migraineDates: string[]; // Array of dates in YYYY-MM-DD format
  currentMonth?: Date; // Optional: specify which month to show (defaults to current month)
  onMonthChange?: (date: Date) => void; // Optional: callback when month changes
  userId?: string; // User ID for fetching reports
  apiBaseUrl?: string; // API base URL
  apiToken?: string; // API authentication token
}

interface ReportData {
  had_migraine?: boolean;
  stress?: boolean;
  oversleep?: boolean;
  sleep_deprivation?: boolean;
  exercise?: boolean;
  fatigue?: boolean;
  menstrual?: boolean;
  emotional_distress?: boolean;
  excessive_noise?: boolean;
  excessive_smells?: boolean;
  excessive_alcohol?: boolean;
  irregular_meals?: boolean;
  overeating?: boolean;
  excessive_caffeine?: boolean;
  excessive_smoking?: boolean;
  travel?: boolean;
  created_at?: string;
}

export function MigraineCalendar({ 
  migraineDates, 
  currentMonth = new Date(),
  onMonthChange,
  userId = '1',
  apiBaseUrl = __DEV__ ? 'http://localhost:8000' : 'https://your-production-api.com',
  apiToken = 'dev-token-12345',
}: MigraineCalendarProps) {
  const colorScheme = useColorScheme();
  const theme = Colors[colorScheme ?? 'light'];
  
  // Modal state
  const [modalVisible, setModalVisible] = useState(false);
  const [selectedDate, setSelectedDate] = useState<string | null>(null);
  const [reportData, setReportData] = useState<ReportData | null>(null);
  const [loadingReport, setLoadingReport] = useState(false);
  const [reportError, setReportError] = useState<string | null>(null);


  // Convert migraine dates to a Set for O(1) lookup
  const migraineDatesSet = new Set(migraineDates);

  // Get first day of month and number of days
  const year = currentMonth.getFullYear();
  const month = currentMonth.getMonth();
  const firstDay = new Date(year, month, 1);
  const lastDay = new Date(year, month + 1, 0);
  const daysInMonth = lastDay.getDate();
  const startingDayOfWeek = firstDay.getDay(); // 0 = Sunday, 6 = Saturday

  // Day names
  const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  // Check if a date had a migraine (works for any month/year)
  const hasMigraine = (day: number, checkYear: number, checkMonth: number): boolean => {
    const dateStr = `${checkYear}-${String(checkMonth + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
    return migraineDatesSet.has(dateStr);
  };

  // Format date as YYYY-MM-DD
  const formatDate = (day: number, checkYear: number, checkMonth: number): string => {
    return `${checkYear}-${String(checkMonth + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
  };

  // Fetch report for a specific date
  const fetchReport = async (date: string) => {
    setLoadingReport(true);
    setReportError(null);
    try {
      const response = await fetch(`${apiBaseUrl}/report-by-date/${userId}?date=${date}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': apiToken,
        },
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.success && data.report) {
        setReportData(data.report);
      } else {
        setReportError(data.error || 'No report found for this date.');
        setReportData(null);
      }
    } catch (error) {
      setReportError('Failed to load report. Please try again.');
      setReportData(null);
    } finally {
      setLoadingReport(false);
    }
  };

  // Handle day press
  const handleDayPress = (day: number, dayYear: number, dayMonth: number) => {
    const dateStr = formatDate(day, dayYear, dayMonth);
    if (hasMigraine(day, dayYear, dayMonth)) {
      setSelectedDate(dateStr);
      setModalVisible(true);
      fetchReport(dateStr);
    }
  };

  // Close modal
  const closeModal = () => {
    setModalVisible(false);
    setSelectedDate(null);
    setReportData(null);
    setReportError(null);
  };

  // Navigate to previous month
  const goToPreviousMonth = () => {
    const newDate = new Date(year, month - 1, 1);
    onMonthChange?.(newDate);
  };

  // Navigate to next month
  const goToNextMonth = () => {
    const newDate = new Date(year, month + 1, 1);
    onMonthChange?.(newDate);
  };

  // Get month name
  const monthName = currentMonth.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });

  // Generate calendar days - always 6 rows (42 days)
  interface CalendarDay {
    day: number;
    year: number;
    month: number;
    isCurrentMonth: boolean;
  }

  const calendarDays: CalendarDay[] = [];
  
  // Calculate days from previous month to show
  const prevMonth = month === 0 ? 11 : month - 1;
  const prevYear = month === 0 ? year - 1 : year;
  const prevMonthLastDay = new Date(prevYear, prevMonth + 1, 0).getDate();
  
  // Add days from previous month
  for (let i = startingDayOfWeek - 1; i >= 0; i--) {
    const day = prevMonthLastDay - i;
    calendarDays.push({
      day,
      year: prevYear,
      month: prevMonth,
      isCurrentMonth: false,
    });
  }
  
  // Add days of the current month
  for (let day = 1; day <= daysInMonth; day++) {
    calendarDays.push({
      day,
      year,
      month,
      isCurrentMonth: true,
    });
  }
  
  // Calculate how many more days needed to fill 6 rows (42 days total)
  const totalDaysSoFar = calendarDays.length;
  const daysNeeded = 42 - totalDaysSoFar;
  
  // Add days from next month
  const nextMonth = month === 11 ? 0 : month + 1;
  const nextYear = month === 11 ? year + 1 : year;
  for (let day = 1; day <= daysNeeded; day++) {
    calendarDays.push({
      day,
      year: nextYear,
      month: nextMonth,
      isCurrentMonth: false,
    });
  }

  return (
    <ThemedView style={[styles.container, { backgroundColor: theme.card, borderColor: theme.cardBorder }]}>
      {/* Header with month navigation */}
      <View style={styles.header}>
        <TouchableOpacity onPress={goToPreviousMonth} style={styles.navButton}>
          <ThemedText style={[styles.navButtonText, { color: theme.primary }]}>‹</ThemedText>
        </TouchableOpacity>
        <ThemedText type="subtitle" style={styles.monthTitle}>{monthName}</ThemedText>
        <TouchableOpacity onPress={goToNextMonth} style={styles.navButton}>
          <ThemedText style={[styles.navButtonText, { color: theme.primary }]}>›</ThemedText>
        </TouchableOpacity>
      </View>

      {/* Day names */}
      <View style={styles.dayNamesRow}>
        {dayNames.map((dayName) => (
          <View key={dayName} style={styles.dayNameCell}>
            <ThemedText style={[styles.dayNameText, { color: theme.textSecondary }]}>
              {dayName}
            </ThemedText>
          </View>
        ))}
      </View>

      {/* Calendar grid */}
      <View style={styles.calendarGrid}>
        {calendarDays.map((calendarDay, index) => {
          const { day, year: dayYear, month: dayMonth, isCurrentMonth } = calendarDay;
          
          const isMigraineDay = hasMigraine(day, dayYear, dayMonth);
          const today = new Date();
          const isToday = 
            day === today.getDate() &&
            dayMonth === today.getMonth() &&
            dayYear === today.getFullYear();

          // For migraine days, always show fully visible; for others, gray out if not current month
          const dayOpacity = isMigraineDay ? 1 : (isCurrentMonth ? 1 : 0.4);

          return (
            <View key={index} style={styles.dayCell}>
              {isMigraineDay ? (
                <TouchableOpacity
                  onPress={() => handleDayPress(day, dayYear, dayMonth)}
                  activeOpacity={0.7}
                  style={{ width: '100%', height: '100%', alignItems: 'center', justifyContent: 'center' }}
                >
                  <View
                    style={[
                      styles.dayCircle,
                      {
                        backgroundColor: theme.primary,
                        opacity: dayOpacity,
                      },
                    ]}
                  >
                    <ThemedText
                      style={[
                        styles.dayText,
                        {
                          color: '#FFFFFF',
                          fontWeight: isToday ? '600' : '400',
                        },
                      ]}
                    >
                      {day}
                    </ThemedText>
                  </View>
                </TouchableOpacity>
              ) : (
                <View
                  style={[
                    styles.dayCircle,
                    {
                      backgroundColor: isToday 
                        ? theme.inputBackground 
                        : 'transparent',
                      borderColor: isToday ? theme.primary : 'transparent',
                      borderWidth: isToday ? 2 : 0,
                      opacity: dayOpacity,
                    },
                  ]}
                >
                  <ThemedText
                    style={[
                      styles.dayText,
                      {
                        color: isToday 
                          ? theme.primary 
                          : isCurrentMonth
                            ? theme.text
                            : theme.textSecondary,
                        fontWeight: isToday ? '600' : '400',
                      },
                    ]}
                  >
                    {day}
                  </ThemedText>
                </View>
              )}
            </View>
          );
        })}
      </View>

      {/* Legend */}
      <View style={styles.legend}>
        <View style={styles.legendItem}>
          <View style={[styles.legendDot, { backgroundColor: theme.primary }]} />
          <ThemedText style={[styles.legendText, { color: theme.textSecondary }]}>
            Migraine day (tap to view)
          </ThemedText>
        </View>
        <View style={styles.legendItem}>
          <View style={[styles.legendDot, { borderColor: theme.primary, borderWidth: 2, backgroundColor: 'transparent' }]} />
          <ThemedText style={[styles.legendText, { color: theme.textSecondary }]}>
            Today
          </ThemedText>
        </View>
      </View>

      {/* Report Modal */}
      <ReportModal
        visible={modalVisible}
        date={selectedDate}
        report={reportData}
        loading={loadingReport}
        error={reportError}
        onClose={closeModal}
        userId={userId}
      />
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 20,
    borderRadius: 20,
    borderWidth: 1,
    marginBottom: 20,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 20,
  },
  navButton: {
    width: 40,
    height: 40,
    alignItems: 'center',
    justifyContent: 'center',
  },
  navButtonText: {
    fontSize: 28,
    fontWeight: '600',
  },
  monthTitle: {
    fontSize: 18,
    fontWeight: '600',
  },
  dayNamesRow: {
    flexDirection: 'row',
    marginBottom: 8,
  },
  dayNameCell: {
    flex: 1,
    alignItems: 'center',
    paddingVertical: 8,
  },
  dayNameText: {
    fontSize: 12,
    fontWeight: '600',
    textTransform: 'uppercase',
  },
  calendarGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  dayCell: {
    width: '14.28%', // 100% / 7 days
    aspectRatio: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 4,
  },
  dayCircle: {
    width: '100%',
    aspectRatio: 1,
    borderRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
    maxWidth: 40,
    maxHeight: 40,
  },
  dayText: {
    fontSize: 14,
    fontWeight: '400',
  },
  legend: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginTop: 16,
    gap: 24,
  },
  legendItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  legendDot: {
    width: 12,
    height: 12,
    borderRadius: 6,
  },
  legendText: {
    fontSize: 12,
  },
});

