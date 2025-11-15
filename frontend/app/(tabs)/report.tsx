import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { IconSymbol } from '@/components/ui/icon-symbol';
import { Colors } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';
import React, { useRef, useState } from 'react';
import { ScrollView, StyleSheet, TouchableOpacity, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter } from 'expo-router';

export default function ReportScreen() {
  const colorScheme = useColorScheme();
  const theme = Colors[colorScheme ?? 'light'];
  const router = useRouter();
  const [intensity, setIntensity] = useState<number | null>(null);
  const [selectedTriggers, setSelectedTriggers] = useState<string[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const submitButtonRef = useRef<TouchableOpacity>(null);

  const intensityLevels = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
  const triggers = ['Stress', 'Sleep', 'Weather', 'Hormones', 'Food', 'Light', 'Noise'];

  const toggleTrigger = (trigger: string) => {
    setSelectedTriggers(prev =>
      prev.includes(trigger) ? prev.filter(t => t !== trigger) : [...prev, trigger]
    );
  };

  const handleSubmit = async () => {
    if (intensity === null) return;

    setIsSubmitting(true);
    try {
      // Mock API call
      await fetch('https://api.example.com/migraine-report', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          intensity,
          triggers: selectedTriggers,
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
      setTimeout(() => {
        console.log('Redirecting to today page');
        router.push('/(tabs)/today');
      }, 2000);
    }
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

        <TouchableOpacity
          ref={submitButtonRef}
          onPress={handleSubmit}
          style={[
            styles.submitButton,
            {
              backgroundColor: theme.primary,
              opacity: intensity === null || isSubmitting ? 0.5 : 1,
            },
          ]}
          disabled={intensity === null || isSubmitting}
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

