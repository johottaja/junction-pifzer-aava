import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { IconSymbol } from '@/components/ui/icon-symbol';
import { Colors } from '@/constants/theme';
import { useColorScheme } from '@/hooks/use-color-scheme';
import Constants from 'expo-constants';
import React, { useState, useRef, useEffect } from 'react';
import { ScrollView, StyleSheet, TextInput, TouchableOpacity, View, KeyboardAvoidingView, Platform } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

interface Message {
  id: string;
  text: string;
  isUser: boolean;
  timestamp: Date;
}

// Get AGENT_AUTH from environment at module level
const getAgentAuth = (): string => {
  try {
    const auth = Constants.expoConfig?.extra?.AGENT_AUTH;
    if (auth && typeof auth === 'string') {
      return auth;
    }
    return '';
  } catch (error) {
    console.warn('Error reading AGENT_AUTH:', error);
    return '';
  }
};

// Get AI_ENDPOINT from environment at module level
const getAIEndpoint = (): string => {
  try {
    const endpoint = Constants.expoConfig?.extra?.AI_ENDPOINT;
    if (endpoint && typeof endpoint === 'string') {
      return endpoint;
    }
    return '';
  } catch (error) {
    console.warn('Error reading AI_ENDPOINT:', error);
    return '';
  }
};

export default function AIAssistantScreen() {
  const colorScheme = useColorScheme();
  const theme = Colors[colorScheme ?? 'light'];
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: "Hello! I'm your AI assistant. I can help you understand your migraine patterns, provide insights, and answer questions about your health data. How can I help you today?",
      isUser: false,
      timestamp: new Date(),
    },
  ]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const scrollViewRef = useRef<ScrollView>(null);

  useEffect(() => {
    // Scroll to bottom when new messages are added
    setTimeout(() => {
      scrollViewRef.current?.scrollToEnd({ animated: true });
    }, 100);
  }, [messages]);

  const handleSend = async (messageOverride?: string) => {
    const messageToSend = messageOverride || inputText.trim();
    if (!messageToSend) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: messageToSend,
      isUser: true,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    if (!messageOverride) {
      setInputText('');
    }
    setIsTyping(true);
    setError(null);

    try {
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
      };

      // Add auth header if AGENT_AUTH is configured
      const agentAuth = getAgentAuth();
      if (agentAuth && agentAuth.trim() !== '') {
        headers['auth'] = agentAuth;
      }
      const body = {
        message: String(messageToSend),
        sessionId: '123',
      };

      const apiEndpoint = getAIEndpoint();
      const response = await fetch(apiEndpoint, {
        method: 'POST',
        headers,
        body: JSON.stringify(body),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();
      
      // Extract the response text from the API response
      // The API returns the text in the "reponse" field
      let responseText = data.output;

      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        text: responseText,
        isUser: false,
        timestamp: new Date(),
      };
      
      setMessages(prev => [...prev, aiResponse]);
    } catch (err) {
      console.error('Error calling AI API:', err);
      setError('Failed to get response. Please try again.');
      
      const errorResponse: Message = {
        id: (Date.now() + 1).toString(),
        text: "I'm sorry, I'm having trouble connecting right now. Please try again in a moment.",
        isUser: false,
        timestamp: new Date(),
      };
      
      setMessages(prev => [...prev, errorResponse]);
    } finally {
      setIsTyping(false);
    }
  };

  const quickActions = [
    { id: '1', text: 'What are my triggers?', icon: 'exclamationmark.triangle.fill' },
    { id: '2', text: 'How can I prevent migraines?', icon: 'shield.fill' },
    { id: '3', text: 'Show my patterns', icon: 'chart.line.uptrend.xyaxis' },
    { id: '4', text: 'Analyze my data', icon: 'brain.head.profile' },
  ];

  const handleQuickAction = (actionText: string) => {
    handleSend(actionText);
  };

  return (
    <SafeAreaView style={[styles.container, { backgroundColor: theme.background }]} edges={['top']}>
      <KeyboardAvoidingView
        style={styles.keyboardView}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        keyboardVerticalOffset={Platform.OS === 'ios' ? 90 : 0}
      >
        <ThemedView style={styles.header}>
          <ThemedView style={styles.headerContent}>
            <IconSymbol name="sparkles" size={24} color={theme.primary} />
            <ThemedText type="title" style={styles.title}>AI Assistant</ThemedText>
          </ThemedView>
          <ThemedText style={[styles.subtitle, { color: theme.textSecondary, backgroundColor: "transparent" }]}>
            Your personal health companion
          </ThemedText>
        </ThemedView>

        <ScrollView
          ref={scrollViewRef}
          style={styles.messagesContainer}
          contentContainerStyle={styles.messagesContent}
          showsVerticalScrollIndicator={false}
        >
          {messages.map((message) => (
            <ThemedView
              key={message.id}
              style={[
                styles.messageWrapper,
                message.isUser ? styles.userMessageWrapper : styles.aiMessageWrapper,
              ]}
            >
              <ThemedView
                style={[
                  styles.messageBubble,
                  {
                    backgroundColor: message.isUser
                      ? theme.primary
                      : theme.card,
                    borderColor: message.isUser ? theme.primary : theme.cardBorder,
                  },
                ]}
              >
                {!message.isUser && (
                  <IconSymbol
                    name="sparkles"
                    size={16}
                    color={theme.primary}
                    style={styles.messageIcon}
                  />
                )}
                <ThemedText
                  style={[
                    styles.messageText,
                    {
                      color: message.isUser ? '#FFFFFF' : theme.text,
                    },
                  ]}
                >
                  {message.text}
                </ThemedText>
              </ThemedView>
            </ThemedView>
          ))}

          {isTyping && (
            <ThemedView style={styles.typingIndicator}>
              <ThemedView
                style={[
                  styles.messageBubble,
                  {
                    backgroundColor: theme.card,
                    borderColor: theme.cardBorder,
                  },
                ]}
              >
                <IconSymbol
                  name="sparkles"
                  size={16}
                  color={theme.primary}
                  style={styles.messageIcon}
                />
                <ThemedView style={styles.typingDots}>
                  <View style={[styles.dot, { backgroundColor: theme.textSecondary }]} />
                  <View style={[styles.dot, { backgroundColor: theme.textSecondary }]} />
                  <View style={[styles.dot, { backgroundColor: theme.textSecondary }]} />
                </ThemedView>
              </ThemedView>
            </ThemedView>
          )}

          {error && (
            <ThemedView style={styles.errorContainer}>
              <ThemedText style={[styles.errorText, { color: theme.error }]}>
                {error}
              </ThemedText>
            </ThemedView>
          )}

          {messages.length === 1 && (
            <ThemedView style={styles.quickActionsContainer}>
              <ThemedText style={[styles.quickActionsTitle, { color: theme.textSecondary }]}>
                Quick Actions
              </ThemedText>
              <ThemedView style={styles.quickActionsGrid}>
                {quickActions.map((action) => (
                  <TouchableOpacity
                    key={action.id}
                    onPress={() => handleQuickAction(action.text)}
                    style={[
                      styles.quickActionButton,
                      {
                        backgroundColor: theme.backgroundSecondary,
                        borderColor: theme.border,
                      },
                    ]}
                  >
                    <IconSymbol name={action.icon as any} size={18} color={theme.primary} />
                    <ThemedText style={[styles.quickActionText, { color: theme.text }]}>
                      {action.text}
                    </ThemedText>
                  </TouchableOpacity>
                ))}
              </ThemedView>
            </ThemedView>
          )}
        </ScrollView>

        <ThemedView
          style={[
            styles.inputContainer,
            {
              backgroundColor: theme.background,
              borderTopColor: theme.border,
            },
          ]}
        >
          <TextInput
            style={[
              styles.input,
              {
                backgroundColor: theme.inputBackground,
                borderColor: theme.inputBorder,
                color: theme.text,
              },
            ]}
            placeholder="Ask me anything..."
            placeholderTextColor={theme.textSecondary}
            value={inputText}
            onChangeText={setInputText}
            multiline
            maxLength={500}
            onSubmitEditing={() => handleSend()}
            returnKeyType="send"
          />
          <TouchableOpacity
            onPress={() => handleSend()}
            disabled={!inputText.trim()}
            style={[
              styles.sendButton,
              {
                backgroundColor: inputText.trim() ? theme.primary : theme.inputBackground,
                opacity: inputText.trim() ? 1 : 0.5,
              },
            ]}
          >
            <IconSymbol
              name="arrow.up.circle.fill"
              size={28}
              color={inputText.trim() ? '#FFFFFF' : theme.textSecondary}
            />
          </TouchableOpacity>
        </ThemedView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  keyboardView: {
    flex: 1,
  },
  header: {
    padding: 20,
    paddingBottom: 16,
  },
  headerContent: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    marginBottom: 8,
    backgroundColor: "transparent",
  },
  title: {
    flex: 1,
  },
  subtitle: {
    fontSize: 16,
    marginLeft: 36,
  },
  messagesContainer: {
    flex: 1,
  },
  messagesContent: {
    padding: 20,
    paddingBottom: 20,
  },
  messageWrapper: {
    marginBottom: 16,
    backgroundColor: "transparent",
  },
  userMessageWrapper: {
    alignItems: 'flex-end',
  },
  aiMessageWrapper: {
    alignItems: 'flex-start',
  },
  messageBubble: {
    maxWidth: '80%',
    padding: 16,
    borderRadius: 20,
    borderWidth: 1,
    flexDirection: 'row',
    alignItems: 'flex-start',
    gap: 10,
  },
  messageIcon: {
    marginTop: 2,
  },
  messageText: {
    flex: 1,
    fontSize: 15,
    lineHeight: 22,
  },
  typingIndicator: {
    alignItems: 'flex-start',
    marginBottom: 16,
    backgroundColor: "transparent",
  },
  typingDots: {
    flexDirection: 'row',
    gap: 6,
    alignItems: 'center',
  },
  dot: {
    width: 8,
    height: 8,
    borderRadius: 4,
  },
  quickActionsContainer: {
    marginTop: 24,
    backgroundColor: "transparent",
  },
  quickActionsTitle: {
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 12,
    backgroundColor: "transparent",
  },
  quickActionsGrid: {
    gap: 12,
    backgroundColor: "transparent",
  },
  quickActionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    padding: 16,
    borderRadius: 16,
    borderWidth: 1,
  },
  quickActionText: {
    flex: 1,
    fontSize: 14,
    fontWeight: '500',
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    padding: 16,
    paddingBottom: 20,
    borderTopWidth: 1,
    gap: 12,
  },
  input: {
    flex: 1,
    minHeight: 44,
    maxHeight: 120,
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderRadius: 22,
    borderWidth: 1,
    fontSize: 15,
    lineHeight: 20,
  },
  sendButton: {
    width: 44,
    height: 44,
    borderRadius: 22,
    alignItems: 'center',
    justifyContent: 'center',
  },
  errorContainer: {
    padding: 12,
    marginTop: 8,
    marginBottom: 8,
    backgroundColor: "transparent",
  },
  errorText: {
    fontSize: 14,
    textAlign: 'center',
  },
});
