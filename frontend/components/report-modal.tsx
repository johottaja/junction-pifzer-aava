import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { Colors } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';
import React from 'react';
import { ActivityIndicator, Modal, ScrollView, StyleSheet, TouchableOpacity, View, Platform } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

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

interface ReportModalProps {
  visible: boolean;
  date: string | null; // YYYY-MM-DD format
  report: ReportData | null;
  loading: boolean;
  error: string | null;
  onClose: () => void;
  userId?: string;
}

// Map database fields to display labels
const fieldLabels: Record<string, string> = {
  stress: 'Were you stressed?',
  sleep_deprivation: 'Were you sleep deprived?',
  emotional_distress: 'Did you experience extreme emotional changes?',
  exercise: 'Did you exercise?',
  fatigue: 'Were you physically fatigued?',
  menstrual: 'Are you currently menstruating?',
  irregular_meals: 'Irregular meals?',
  overeating: 'Overeating?',
  excessive_alcohol: 'Excessive alcohol?',
  excessive_caffeine: 'Excessive caffeinated drinks?',
  excessive_smoking: 'Excessive smoking?',
  excessive_noise: 'Excessive noise?',
  excessive_smells: 'Specific smells (cosmetics, perfume, etc.)?',
  travel: 'Travel migraine?',
  oversleep: 'Did you oversleep?',
};

export function ReportModal({
  visible,
  date,
  report,
  loading,
  error,
  onClose,
}: ReportModalProps) {
  const colorScheme = useColorScheme();
  const theme = Colors[colorScheme ?? 'light'];


  // Format date for display
  const formatDate = (dateStr: string | null): string => {
    if (!dateStr) return '';
    try {
      const date = new Date(dateStr + 'T00:00:00');
      return date.toLocaleDateString('en-US', { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
      });
    } catch {
      return dateStr;
    }
  };

  // Get all answered questions
  const getAnsweredQuestions = () => {
    if (!report) return [];
    
    const questions: Array<{ label: string; answer: boolean }> = [];
    
    // Iterate through all keys in the report
    Object.keys(report).forEach((key) => {
      // Skip non-question fields
      if (key === 'had_migraine' || key === 'created_at' || key === 'user_id' || key === 'log_id') {
        return;
      }
      
      // Get the label from fieldLabels, or use the key as fallback
      const label = fieldLabels[key] || key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
      const value = report[key as keyof ReportData];
      
      // Include all boolean fields (true, false, or null treated as false)
      if (typeof value === 'boolean' || value === null) {
        questions.push({ label, answer: value === true });
      }
    });
    return questions;
  };

  if (!visible) {
    return null;
  }

  return (
    <Modal
      visible={visible}
      transparent
      animationType="fade"
      onRequestClose={onClose}
      statusBarTranslucent
      presentationStyle={Platform.OS === 'ios' ? 'overFullScreen' : undefined}
    >
      <SafeAreaView style={styles.modalOverlay} edges={['top', 'bottom']}>
        <View style={styles.modalOverlayInner}>
          <ThemedView style={[styles.modalContent, { backgroundColor: theme.card, borderColor: theme.cardBorder }]}>
            {/* Header */}
            <View style={styles.header}>
              <ThemedText type="title" style={styles.title}>
                Daily Report
              </ThemedText>
              <TouchableOpacity onPress={onClose} style={styles.closeButton}>
                <ThemedText style={[styles.closeButtonText, { color: theme.text }]}>✕</ThemedText>
              </TouchableOpacity>
            </View>

            {/* Date */}
            {date && (
              <ThemedText style={[styles.dateText, { color: theme.textSecondary }]}>
                {formatDate(date)}
              </ThemedText>
            )}

            {/* Content */}
            <ScrollView 
              style={styles.content} 
              contentContainerStyle={styles.contentContainer}
              showsVerticalScrollIndicator={true}
            >
            {loading && (
              <View style={styles.loadingContainer}>
                <ActivityIndicator size="large" color={theme.primary} />
                <ThemedText style={[styles.loadingText, { color: theme.textSecondary }]}>
                  Loading report...
                </ThemedText>
              </View>
            )}

            {!loading && error && (
              <View style={styles.errorContainer}>
                <ThemedText style={[styles.errorText, { color: theme.error || '#FF3B30' }]}>
                  {error}
                </ThemedText>
              </View>
            )}

            {!loading && report && (
              <>
                {/* Migraine Status */}
                <View style={[styles.section, { backgroundColor: theme.inputBackground }]}>
                  <ThemedText style={[styles.sectionTitle, { color: theme.text }]}>
                    Migraine Status
                  </ThemedText>
                  <View style={styles.statusRow}>
                    <View
                      style={[
                        styles.statusBadge,
                        {
                          backgroundColor: report.had_migraine === true
                            ? theme.primary
                            : theme.inputBackground,
                        },
                      ]}
                    >
                      <ThemedText
                        style={[
                          styles.statusText,
                          {
                            color: report.had_migraine === true ? '#FFFFFF' : theme.text,
                          },
                        ]}
                      >
                        {report.had_migraine === true ? 'Had Migraine' : 'No Migraine'}
                      </ThemedText>
                    </View>
                  </View>
                </View>

                {/* Daily Questions */}
                <View style={styles.section}>
                  <ThemedText style={[styles.sectionTitle, { color: theme.text }]}>
                    Daily Questions
                  </ThemedText>
                  {getAnsweredQuestions().length > 0 ? (
                    getAnsweredQuestions().map((q, index) => (
                      <View key={index} style={styles.questionRow}>
                        <ThemedText style={[styles.questionText, { color: theme.text }]}>
                          {q.label}
                        </ThemedText>
                        <View
                          style={[
                            styles.answerBadge,
                            {
                              backgroundColor: q.answer
                                ? theme.primary
                                : theme.inputBackground,
                            },
                            ]}
                          >
                            <ThemedText
                            style={[
                              styles.answerText,
                              {
                                color: q.answer ? '#FFFFFF' : theme.text,
                              },
                            ]}
                          >
                            {q.answer ? 'Yes' : 'No'}
                          </ThemedText>
                        </View>
                      </View>
                    ))
                  ) : (
                    <ThemedText style={[styles.emptyText, { color: theme.textSecondary }]}>
                      No daily questions were answered for this report.
                    </ThemedText>
                  )}
                </View>
              </>
            )}

            {!loading && !report && !error && (
              <View style={styles.section}>
                <ThemedText style={[styles.emptyText, { color: theme.textSecondary }]}>
                  No report data available.
                </ThemedText>
              </View>
            )}
          </ScrollView>
        </ThemedView>
        </View>
      </SafeAreaView>
    </Modal>
  );
}

const styles = StyleSheet.create({
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
  },
  modalOverlayInner: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  modalContent: {
    width: '100%',
    maxWidth: 500,
    height: 600,
    borderRadius: 20,
    borderWidth: 1,
    overflow: 'hidden',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    paddingBottom: 12,
  },
  title: {
    fontSize: 24,
    fontWeight: '700',
  },
  closeButton: {
    width: 32,
    height: 32,
    alignItems: 'center',
    justifyContent: 'center',
  },
  closeButtonText: {
    fontSize: 24,
    fontWeight: '600',
  },
  dateText: {
    fontSize: 16,
    paddingHorizontal: 20,
    paddingBottom: 16,
  },
  content: {
    height: 400,
  },
  contentContainer: {
    paddingHorizontal: 20,
    paddingBottom: 20,
  },
  loadingContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 40,
  },
  loadingText: {
    marginTop: 12,
    fontSize: 14,
  },
  errorContainer: {
    paddingVertical: 20,
  },
  errorText: {
    fontSize: 14,
    textAlign: 'center',
  },
  section: {
    marginBottom: 20,
    padding: 16,
    borderRadius: 12,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 12,
  },
  statusRow: {
    flexDirection: 'row',
  },
  statusBadge: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
  },
  statusText: {
    fontSize: 14,
    fontWeight: '600',
  },
  questionRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: 'rgba(0, 0, 0, 0.1)',
  },
  questionText: {
    flex: 1,
    fontSize: 14,
    marginRight: 12,
  },
  answerBadge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    minWidth: 50,
    alignItems: 'center',
  },
  answerText: {
    fontSize: 12,
    fontWeight: '600',
  },
  emptyText: {
    fontSize: 14,
    textAlign: 'center',
    paddingVertical: 20,
  },
});

