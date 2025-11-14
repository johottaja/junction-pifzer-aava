import React, { useState } from 'react';
import { StyleSheet, ScrollView, TouchableOpacity, Platform } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { Colors } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { IconSymbol } from '@/components/ui/icon-symbol';

export default function ReportScreen() {
  const colorScheme = useColorScheme();
  const theme = Colors[colorScheme ?? 'light'];
  const [intensity, setIntensity] = useState<number | null>(null);
  const [selectedTriggers, setSelectedTriggers] = useState<string[]>([]);
  const [selectedSymptoms, setSelectedSymptoms] = useState<string[]>([]);

  const intensityLevels = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
  const triggers = ['Stress', 'Sleep', 'Weather', 'Hormones', 'Food', 'Light', 'Noise'];
  const symptoms = ['Nausea', 'Sensitivity to Light', 'Sensitivity to Sound', 'Aura', 'Dizziness'];

  const toggleTrigger = (trigger: string) => {
    setSelectedTriggers(prev =>
      prev.includes(trigger) ? prev.filter(t => t !== trigger) : [...prev, trigger]
    );
  };

  const toggleSymptom = (symptom: string) => {
    setSelectedSymptoms(prev =>
      prev.includes(symptom) ? prev.filter(s => s !== symptom) : [...prev, symptom]
    );
  };

  const handleSubmit = () => {
    // TODO: Implement submission logic
    console.log('Report submitted:', { intensity, triggers: selectedTriggers, symptoms: selectedSymptoms });
  };

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.background }]} edges={['top']}>
      <ScrollView 
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        <ThemedView style={styles.header}>
          <ThemedText type="title" style={styles.title}>Report Migraine</ThemedText>
          <ThemedText style={[styles.subtitle, { color: theme.textSecondary }]}>
            Track your migraine episode
          </ThemedText>
        </ThemedView>

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
          <ThemedText type="subtitle" style={styles.sectionTitle}>Possible Triggers</ThemedText>
          <ThemedText style={[styles.sectionDescription, { color: theme.textSecondary }]}>
            Select any triggers that may have contributed
          </ThemedText>
          <ThemedView style={styles.chipContainer}>
            {triggers.map(trigger => (
              <TouchableOpacity
                key={trigger}
                onPress={() => toggleTrigger(trigger)}
                style={[
                  styles.chip,
                  {
                    backgroundColor: selectedTriggers.includes(trigger)
                      ? theme.primary
                      : theme.inputBackground,
                    borderColor: selectedTriggers.includes(trigger)
                      ? theme.primary
                      : theme.inputBorder,
                  },
                ]}
              >
                <ThemedText
                  style={[
                    styles.chipText,
                    {
                      color: selectedTriggers.includes(trigger) ? '#FFFFFF' : theme.text,
                    },
                  ]}
                >
                  {trigger}
                </ThemedText>
              </TouchableOpacity>
            ))}
          </ThemedView>
        </ThemedView>

        <ThemedView style={[styles.section, { backgroundColor: theme.card, borderColor: theme.cardBorder }]}>
          <ThemedText type="subtitle" style={styles.sectionTitle}>Symptoms</ThemedText>
          <ThemedText style={[styles.sectionDescription, { color: theme.textSecondary }]}>
            Select symptoms you experienced
          </ThemedText>
          <ThemedView style={styles.chipContainer}>
            {symptoms.map(symptom => (
              <TouchableOpacity
                key={symptom}
                onPress={() => toggleSymptom(symptom)}
                style={[
                  styles.chip,
                  {
                    backgroundColor: selectedSymptoms.includes(symptom)
                      ? theme.secondary
                      : theme.inputBackground,
                    borderColor: selectedSymptoms.includes(symptom)
                      ? theme.secondary
                      : theme.inputBorder,
                  },
                ]}
              >
                <ThemedText
                  style={[
                    styles.chipText,
                    {
                      color: selectedSymptoms.includes(symptom) ? '#FFFFFF' : theme.text,
                    },
                  ]}
                >
                  {symptom}
                </ThemedText>
              </TouchableOpacity>
            ))}
          </ThemedView>
        </ThemedView>

        <TouchableOpacity
          onPress={handleSubmit}
          style={[
            styles.submitButton,
            {
              backgroundColor: theme.primary,
              opacity: intensity === null ? 0.5 : 1,
            },
          ]}
          disabled={intensity === null}
        >
          <ThemedText style={styles.submitButtonText}>Save Report</ThemedText>
        </TouchableOpacity>
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
    padding: 20,
    borderRadius: 16,
    borderWidth: 1,
    marginBottom: 20,
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
  sectionTitle: {
    marginBottom: 8,
  },
  sectionDescription: {
    fontSize: 14,
    marginBottom: 16,
  },
  intensityContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  intensityButton: {
    width: 48,
    height: 48,
    borderRadius: 12,
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
  },
  chip: {
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 20,
    borderWidth: 1,
  },
  chipText: {
    fontSize: 14,
    fontWeight: '500',
  },
  submitButton: {
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
    marginTop: 8,
  },
  submitButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
});

