import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { Colors } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { Platform, ScrollView, StyleSheet, TouchableOpacity, View, Modal, ActivityIndicator } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import MaterialIcons from '@expo/vector-icons/MaterialIcons';
import { useState, useEffect } from 'react';

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

type ConnectionStep = 'hold' | 'found' | 'connected';

export default function DevicesScreen() {
  const colorScheme = useColorScheme();
  const theme = Colors[colorScheme ?? 'light'];
  const [modalVisible, setModalVisible] = useState(false);
  const [connectionStep, setConnectionStep] = useState<ConnectionStep>('hold');
  const [deviceName, setDeviceName] = useState('');
  const [connectedDevices, setConnectedDevices] = useState<Set<string>>(new Set());
  const [disconnectModalVisible, setDisconnectModalVisible] = useState(false);
  const [deviceToDisconnect, setDeviceToDisconnect] = useState<string>('');

  useEffect(() => {
    if (!modalVisible) {
      setConnectionStep('hold');
      return;
    }

    // Step 1: "Hold your device close" - 3 seconds
    const timer1 = setTimeout(() => {
      setConnectionStep('found');
    }, 3000);

    // Step 2: "Device found" - 3 seconds
    const timer2 = setTimeout(() => {
      setConnectionStep('connected');
    }, 6000);

    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
    };
  }, [modalVisible]);

  const handleDevicePress = (name: string) => {
    if (connectedDevices.has(name)) {
      // Device is connected, show disconnect confirmation
      setDeviceToDisconnect(name);
      setDisconnectModalVisible(true);
    } else {
      // Device is not connected, start connection flow
      setDeviceName(name);
      setModalVisible(true);
    }
  };

  const handleContinue = () => {
    // Mark device as connected
    setConnectedDevices(prev => new Set(prev).add(deviceName));
    setModalVisible(false);
    setConnectionStep('hold');
  };

  const handleDisconnectConfirm = () => {
    setConnectedDevices(prev => {
      const newSet = new Set(prev);
      newSet.delete(deviceToDisconnect);
      return newSet;
    });
    setDisconnectModalVisible(false);
    setDeviceToDisconnect('');
  };

  const handleDisconnectCancel = () => {
    setDisconnectModalVisible(false);
    setDeviceToDisconnect('');
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
              HeadSync connects with a wide range of fitness devices and health apps. Sync your activity data seamlessly to get comprehensive insights into your health patterns and migraine predictions.
            </ThemedText>
          </ThemedView>

          <ThemedView style={styles.deviceList}>
            {devices.map((device, index) => (
              <ThemedView
                key={index}
                style={{
                  ...styles.deviceRow,
                  backgroundColor: theme.card,
                  borderColor: theme.cardBorder,
                }}
              >
                <View style={styles.deviceIconContainer}>
                  <MaterialIcons 
                    name="watch" 
                    size={32} 
                    color={theme.icon} 
                  />
                </View>
                <View style={styles.deviceInfo}>
                  <ThemedText style={styles.deviceName}>{device.name}</ThemedText>
                </View>
                <TouchableOpacity
                  style={{
                    ...styles.connectButton,
                    backgroundColor: connectedDevices.has(device.name) 
                      ? theme.error 
                      : theme.primary,
                  }}
                  onPress={() => handleDevicePress(device.name)}
                >
                  <ThemedText style={styles.connectButtonText}>
                    {connectedDevices.has(device.name) ? 'Disconnect' : 'Connect'}
                  </ThemedText>
                </TouchableOpacity>
              </ThemedView>
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

      <Modal
        visible={modalVisible}
        transparent={true}
        animationType="fade"
        onRequestClose={() => setModalVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <ThemedView style={[styles.modalContent, { backgroundColor: theme.card }]}>
            {connectionStep === 'hold' && (
              <View style={styles.modalStep}>
                <MaterialIcons name="bluetooth" size={64} color={theme.primary} />
                <ThemedText type="title" style={styles.modalTitle}>Hold your device close</ThemedText>
                <ThemedText style={[styles.modalDescription, { color: theme.textSecondary }]}>
                  Make sure your {deviceName} device is nearby and turned on
                </ThemedText>
              </View>
            )}

            {connectionStep === 'found' && (
              <View style={styles.modalStep}>
                <ActivityIndicator size="large" color={theme.primary} />
                <ThemedText type="title" style={styles.modalTitle}>Device found, keep it close to finish connecting</ThemedText>
                <ThemedText style={[styles.modalDescription, { color: theme.textSecondary }]}>
                  Please wait while we establish the connection
                </ThemedText>
              </View>
            )}

            {connectionStep === 'connected' && (
              <View style={styles.modalStep}>
                <MaterialIcons name="check-circle" size={64} color={theme.success} />
                <ThemedText type="title" style={styles.modalTitle}>Device connected</ThemedText>
                <ThemedText style={[styles.modalDescription, { color: theme.textSecondary }]}>
                  Your {deviceName} device is now connected and ready to use
                </ThemedText>
                <TouchableOpacity
                  style={[styles.continueButton, { backgroundColor: theme.primary }]}
                  onPress={handleContinue}
                >
                  <ThemedText style={styles.continueButtonText}>Continue</ThemedText>
                </TouchableOpacity>
              </View>
            )}
          </ThemedView>
        </View>
      </Modal>

      <Modal
        visible={disconnectModalVisible}
        transparent={true}
        animationType="fade"
        onRequestClose={handleDisconnectCancel}
      >
        <View style={styles.modalOverlay}>
          <ThemedView style={[styles.modalContent, { backgroundColor: theme.card }]}>
            <View style={styles.modalStep}>
              <MaterialIcons name="warning" size={64} color={theme.error} />
              <ThemedText type="title" style={styles.modalTitle}>Disconnect Device?</ThemedText>
              <ThemedText style={[styles.modalDescription, { color: theme.textSecondary }]}>
                Are you sure you want to disconnect your {deviceToDisconnect} device? You'll need to reconnect it to sync data again.
              </ThemedText>
              <View style={styles.confirmButtonRow}>
                <TouchableOpacity
                  style={[styles.confirmButton, styles.cancelButton, { borderColor: theme.border }]}
                  onPress={handleDisconnectCancel}
                >
                  <ThemedText style={[styles.confirmButtonText, { color: theme.text }]}>Cancel</ThemedText>
                </TouchableOpacity>
                <TouchableOpacity
                  style={[styles.confirmButton, styles.disconnectButton, { backgroundColor: theme.error }]}
                  onPress={handleDisconnectConfirm}
                >
                  <ThemedText style={[styles.confirmButtonText, { color: '#FFFFFF' }]}>Disconnect</ThemedText>
                </TouchableOpacity>
              </View>
            </View>
          </ThemedView>
        </View>
      </Modal>
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
  deviceList: {
    marginBottom: 24,
  },
  deviceRow: {
    flexDirection: 'row',
    alignItems: 'center',
    borderRadius: 12,
    borderWidth: 1,
    padding: 16,
    marginBottom: 12,
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
  deviceIconContainer: {
    marginRight: 16,
  },
  deviceInfo: {
    flex: 1,
  },
  deviceName: {
    fontSize: 16,
    fontWeight: '600',
  },
  connectButton: {
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 8,
    minWidth: 90,
    alignItems: 'center',
    justifyContent: 'center',
  },
  connectButtonText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '600',
  },
  differentDeviceLink: {
    alignItems: 'center',
    paddingVertical: 12,
  },
  differentDeviceText: {
    fontSize: 16,
    fontWeight: '500',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  modalContent: {
    borderRadius: 20,
    padding: 32,
    width: '100%',
    maxWidth: 400,
    alignItems: 'center',
    ...Platform.select({
      ios: {
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 4 },
        shadowOpacity: 0.3,
        shadowRadius: 8,
      },
      android: {
        elevation: 8,
      },
    }),
  },
  modalStep: {
    alignItems: 'center',
    width: '100%',
  },
  modalTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    marginTop: 24,
    marginBottom: 12,
    textAlign: 'center',
  },
  modalDescription: {
    fontSize: 16,
    lineHeight: 24,
    textAlign: 'center',
    marginBottom: 32,
  },
  continueButton: {
    paddingHorizontal: 32,
    paddingVertical: 14,
    borderRadius: 12,
    marginTop: 8,
    minWidth: 200,
    alignItems: 'center',
    justifyContent: 'center',
  },
  continueButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  confirmButtonRow: {
    flexDirection: 'row',
    gap: 12,
    width: '100%',
    marginTop: 8,
  },
  confirmButton: {
    flex: 1,
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  cancelButton: {
    borderWidth: 1,
    backgroundColor: 'transparent',
  },
  disconnectButton: {
    // backgroundColor set inline
  },
  confirmButtonText: {
    fontSize: 16,
    fontWeight: '600',
  },
});

