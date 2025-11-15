import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { IconSymbol } from '@/components/ui/icon-symbol';
import { Colors, Fonts } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';
import React, { useEffect, useRef, useState } from 'react';
import { ScrollView, StyleSheet, TextInput, TouchableOpacity, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';

type Answer = 'yes' | 'no' | null;

interface DailyQuestion {
  id: string;
  question: string;
}

export default function ReportScreen() {
  const colorScheme = useColorScheme();
  const theme = Colors[colorScheme ?? 'light'];
  const router = useRouter();
  const [dailyAnswers, setDailyAnswers] = useState<Record<string, Answer>>({});
  const [hadMigraine, setHadMigraine] = useState<Answer>(null);
  const [intensity, setIntensity] = useState<number | null>(null);
  const [description, setDescription] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const submitButtonRef = useRef<React.ElementRef<typeof TouchableOpacity>>(null);
  const redirectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const dailyQuestions: DailyQuestion[] = [
    { id: 'sleep_deprived', question: 'Were you sleep deprived?' },
    { id: 'stressed', question: 'Were you stressed?' },
    { id: 'emotional_changes', question: 'Did you experience extreme emotional changes?' },
    { id: 'exercise', question: 'Did you exercise?' },
    { id: 'physical_fatigue', question: 'Were you physically fatigued?' },
    { id: 'menstruating', question: 'Are you currently menstruating?' },
    { id: 'irregular_meals', question: 'Irregular meals?' },
    { id: 'overeating', question: 'Overeating?' },
    { id: 'excessive_alcohol', question: 'Excessive alcohol?' },
    { id: 'excessive_caffeine', question: 'Excessive caffeinated drinks?' },
    { id: 'excessive_smoking', question: 'Excessive smoking?' },
    { id: 'excessive_noise', question: 'Excessive noise?' },
    { id: 'specific_smells', question: 'Specific smells (cosmetics, perfume, etc.)?' },
    { id: 'travel_migraine', question: 'Travel migraine?' },
  ];

  const intensityLevels = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (redirectTimeoutRef.current) {
        clearTimeout(redirectTimeoutRef.current);
      }
      setShowSuccess(false);
    };
  }, []);

  // Reset migraine-specific fields when hadMigraine changes to 'no' or null
  useEffect(() => {
    if (hadMigraine !== 'yes') {
      setIntensity(null);
      setDescription('');
    }
  }, [hadMigraine]);

  const setDailyAnswer = (questionId: string, answer: Answer) => {
    setDailyAnswers(prev => ({
      ...prev,
      [questionId]: answer,
    }));
  };

  const isFormValid = () => {
    // Check all daily questions are answered
    const allDailyAnswered = dailyQuestions.every(q => dailyAnswers[q.id] !== null && dailyAnswers[q.id] !== undefined);
    // Check migraine question is answered
    if (hadMigraine === null) return false;
    // If migraine was yes, check migraine-specific fields
    if (hadMigraine === 'yes') {
      return intensity !== null;
    }
    return allDailyAnswered;
  };

  const handleSubmit = async () => {
    if (!isFormValid()) return;

    setIsSubmitting(true);
    try {
      // Mock API call
      await fetch('https://api.example.com/daily-report', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          dailyAnswers,
          hadMigraine,
          ...(hadMigraine === 'yes' && {
            intensity,
            description,
          }),
          timestamp: new Date().toISOString(),
        }),
      });

      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 1000));
    } catch (error) {
      // Mock API will fail, but we'll show success for demo purposes
      console.log('Mock API call (expected to fail):', error);
    } finally {
      setIsSubmitting(false);
      // Blur any focused elements to prevent accessibility issues
      if (submitButtonRef.current) {
        (submitButtonRef.current as any).blur?.();
      }
      // Show success indicator
      setShowSuccess(true);
      console.log('Success state set to true');
      // Redirect after 2 seconds
      redirectTimeoutRef.current = setTimeout(() => {
        console.log('Redirecting to today page');
        setShowSuccess(false);
        router.push('/(tabs)/today');
      }, 2000);
    }
  };

  const renderYesNoButtons = (answer: Answer, onAnswer: (answer: Answer) => void) => {
    return (
      <ThemedView style={styles.yesNoContainer}>
        <TouchableOpacity
          onPress={() => onAnswer('yes')}
          style={[
            styles.yesNoButton,
            {
              backgroundColor: answer === 'yes' ? theme.primary : theme.inputBackground,
              borderColor: answer === 'yes' ? theme.primary : theme.inputBorder,
            },
          ]}
        >
          <ThemedText
            style={[
              styles.yesNoText,
              { color: answer === 'yes' ? '#FFFFFF' : theme.text },
            ]}
          >
            Yes
          </ThemedText>
        </TouchableOpacity>
        <TouchableOpacity
          onPress={() => onAnswer('no')}
          style={[
            styles.yesNoButton,
            {
              backgroundColor: answer === 'no' ? theme.primary : theme.inputBackground,
              borderColor: answer === 'no' ? theme.primary : theme.inputBorder,
            },
          ]}
        >
          <ThemedText
            style={[
              styles.yesNoText,
              { color: answer === 'no' ? '#FFFFFF' : theme.text },
            ]}
          >
            No
          </ThemedText>
        </TouchableOpacity>
      </ThemedView>
    );
  };

  return (
    <View style={[styles.container, { backgroundColor: theme.background }]}>
      <SafeAreaView style={styles.safeArea} edges={['top']}>
        <ScrollView 
          style={styles.scrollView}
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
        >
        <ThemedView style={styles.header}>
          <ThemedText type="title" style={styles.title}>Daily Report</ThemedText>
          <ThemedText style={[styles.subtitle, { color: theme.textSecondary }]}>
            Complete your daily health report
          </ThemedText>
        </ThemedView>

        <ThemedView style={[styles.section, { backgroundColor: theme.card, borderColor: theme.cardBorder }]}>
          <ThemedText type="subtitle" style={styles.sectionTitle}>Daily Questions</ThemedText>
          <ThemedText style={[styles.sectionDescription, { color: theme.textSecondary }]}>
            Please answer all questions about your day
          </ThemedText>
          {dailyQuestions.map((question) => (
            <ThemedView key={question.id} style={styles.questionItem}>
              <ThemedText style={styles.questionText}>{question.question}</ThemedText>
              {renderYesNoButtons(dailyAnswers[question.id] || null, (answer) => setDailyAnswer(question.id, answer))}
            </ThemedView>
          ))}
        </ThemedView>

        <ThemedView style={[styles.section, { backgroundColor: theme.card, borderColor: theme.cardBorder }]}>
          <ThemedText type="subtitle" style={styles.sectionTitle}>Migraine</ThemedText>
          <ThemedText style={[styles.sectionDescription, { color: theme.textSecondary }]}>
            Did you get a migraine today?
          </ThemedText>
          {renderYesNoButtons(hadMigraine, setHadMigraine)}
        </ThemedView>

        {hadMigraine === 'yes' && (
          <>
            <ThemedView style={[styles.section, { backgroundColor: theme.card, borderColor: theme.cardBorder }]}>
              <ThemedText type="subtitle" style={styles.sectionTitle}>Pain Intensity</ThemedText>
              <ThemedText style={[styles.sectionDescription, { color: theme.textSecondary }]}>
                Rate your pain level from 1 to 10
              </ThemedText>
              <ThemedView style={styles.intensityContainer}>
                {intensityLevels.map(level => (
                  <TouchableOpacity
                    key={level}
                    onPress={() => setIntensity(level)}
                    style={[
                      styles.intensityButton,
                      {
                        backgroundColor: intensity === level ? theme.primary : theme.inputBackground,
                        borderColor: intensity === level ? theme.primary : theme.inputBorder,
                      },
                    ]}
                  >
                    <ThemedText
                      style={[
                        styles.intensityText,
                        { color: intensity === level ? '#FFFFFF' : theme.text },
                      ]}
                    >
                      {level}
                    </ThemedText>
                  </TouchableOpacity>
                ))}
              </ThemedView>
            </ThemedView>

            <ThemedView style={[styles.section, { backgroundColor: theme.card, borderColor: theme.cardBorder }]}>
              <ThemedText type="subtitle" style={styles.sectionTitle}>Description</ThemedText>
              <ThemedText style={[styles.sectionDescription, { color: theme.textSecondary }]}>
                Add any additional notes about your migraine episode (optional)
              </ThemedText>
              <TextInput
                style={[
                  styles.descriptionInput,
                  {
                    backgroundColor: theme.inputBackground,
                    borderColor: theme.inputBorder,
                    color: theme.text,
                    fontFamily: Fonts.sans,
                  },
                ]}
                placeholder="Enter any additional details..."
                placeholderTextColor={theme.textSecondary}
                value={description}
                onChangeText={setDescription}
                multiline
                numberOfLines={6}
                textAlignVertical="top"
              />
            </ThemedView>
          </>
        )}

        <TouchableOpacity
          ref={submitButtonRef}
          onPress={handleSubmit}
          style={[
            styles.submitButton,
            {
              backgroundColor: theme.primary,
              opacity: !isFormValid() || isSubmitting ? 0.5 : 1,
            },
          ]}
          disabled={!isFormValid() || isSubmitting}
        >
          <ThemedText style={styles.submitButtonText}>
            {isSubmitting ? 'Sending...' : 'Save Report'}
          </ThemedText>
        </TouchableOpacity>
        </ScrollView>
      </SafeAreaView>
      {showSuccess && (
        <View 
          style={styles.successOverlay} 
          pointerEvents="none"
          accessible={false}
          importantForAccessibility="no"
          onLayout={() => console.log('Success overlay rendered')}
        >
          <View style={styles.successIconContainer}>
            <IconSymbol name="checkmark.circle.fill" size={80} color={theme.success} />
          </View>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    position: 'relative',
  },
  safeArea: {
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
    padding: 24,
    borderRadius: 20,
    borderWidth: 1,
    marginBottom: 20,
  },
  sectionTitle: {
    marginBottom: 8,
  },
  sectionDescription: {
    fontSize: 14,
    marginBottom: 16,
  },
  questionItem: {
    marginBottom: 20,
    backgroundColor: "transparent",
  },
  questionText: {
    fontSize: 15,
    fontWeight: '500',
    marginBottom: 12,
  },
  yesNoContainer: {
    flexDirection: 'row',
    gap: 12,
    backgroundColor: "transparent",
  },
  yesNoButton: {
    flex: 1,
    paddingVertical: 14,
    paddingHorizontal: 20,
    borderRadius: 16,
    borderWidth: 2,
    alignItems: 'center',
    justifyContent: 'center',
  },
  yesNoText: {
    fontSize: 16,
    fontWeight: '600',
  },
  intensityContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    backgroundColor: "transparent",
  },
  intensityButton: {
    width: 52,
    height: 52,
    borderRadius: 16,
    borderWidth: 2,
    alignItems: 'center',
    justifyContent: 'center',
  },
  intensityText: {
    fontSize: 18,
    fontWeight: '600',
  },
  chipContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
    backgroundColor: "transparent",
  },
  chip: {
    paddingHorizontal: 18,
    paddingVertical: 12,
    borderRadius: 24,
    borderWidth: 1,
  },
  chipText: {
    fontSize: 14,
    fontWeight: '500',
  },
  descriptionInput: {
    minHeight: 120,
    padding: 16,
    borderRadius: 16,
    borderWidth: 1,
    fontSize: 15,
    lineHeight: 22,
  },
  submitButton: {
    paddingVertical: 18,
    borderRadius: 20,
    alignItems: 'center',
    marginTop: 8,
  },
  submitButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  successOverlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: 'rgba(255, 255, 255, 0.9)',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 99999,
    elevation: 99999,
  },
  successIconContainer: {
    backgroundColor: 'transparent',
    justifyContent: 'center',
    alignItems: 'center',
  },
});

