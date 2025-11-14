import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { IconSymbol } from '@/components/ui/icon-symbol';
import { Colors } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { Platform, ScrollView, StyleSheet, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

const devices = [
  { name: 'GARMIN', logo: 'GARMIN.' },
  { name: 'POLAR', logo: 'POLAR' },
  { name: 'ZWIFT', logo: 'ZWIFT' },
  { name: 'SUUNTO', logo: 'SUUNTO' },
  { name: 'wahoo', logo: 'wahoo' },
  { name: 'PELOTON', logo: 'PELOTON' },
  { name: 'amazfit', logo: 'amazfit' },
  { name: 'COROS', logo: 'COROS' },
  { name: 'SAMSUNG', logo: 'SAMSUNG' },
  { name: 'fitbit', logo: 'fitbit' },
  { name: 'Nike', logo: 'Nike' },
  { name: 'ŌURA', logo: 'ŌURA' },
  { name: 'HUAWEI', logo: 'HUAWEI' },
];

export default function DevicesScreen() {
  const colorScheme = useColorScheme();
  const theme = Colors[colorScheme ?? 'light'];

  const handleDevicePress = (deviceName: string) => {
    // TODO: Implement device connection logic
    console.log('Connect to:', deviceName);
  };

  return (
    <SafeAreaView style={{ ...styles.container, backgroundColor: theme.background }} edges={['top']}>
      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        <ThemedView style={styles.content}>
          <ThemedView style={styles.header}>
            <ThemedText type="title" style={styles.title}>Connect Your Device</ThemedText>
            <ThemedText style={{ ...styles.description, color: theme.textSecondary }}>
              Strava pairs with almost every fitness device and app. Get seamless activity uploads - plus a fuller picture of your performance and recovery.
            </ThemedText>
          </ThemedView>

          <ThemedView style={styles.deviceGrid}>
            {devices.map((device, index) => (
              <TouchableOpacity
                key={index}
                style={{
                  ...styles.deviceButton,
                  backgroundColor: theme.card,
                  borderColor: theme.cardBorder,
                }}
                onPress={() => handleDevicePress(device.name)}
              >
                <ThemedText style={styles.deviceName}>{device.logo}</ThemedText>
              </TouchableOpacity>
            ))}
          </ThemedView>

          <TouchableOpacity
            style={styles.differentDeviceLink}
            onPress={() => {
              // TODO: Handle different device
              console.log('Different device');
            }}
          >
            <ThemedText style={{ ...styles.differentDeviceText, color: theme.primary }}>
              I have a different device
            </ThemedText>
          </TouchableOpacity>
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
  content: {
    flex: 1,
  },
  header: {
    marginBottom: 32,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    marginBottom: 16,
  },
  description: {
    fontSize: 16,
    lineHeight: 24,
  },
  deviceGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
    marginBottom: 24,
  },
  deviceButton: {
    width: '47%',
    aspectRatio: 2.5,
    borderRadius: 12,
    borderWidth: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 16,
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
  deviceName: {
    fontSize: 16,
    fontWeight: '600',
    textAlign: 'center',
  },
  differentDeviceLink: {
    alignItems: 'center',
    paddingVertical: 12,
  },
  differentDeviceText: {
    fontSize: 16,
    fontWeight: '500',
  },
});

