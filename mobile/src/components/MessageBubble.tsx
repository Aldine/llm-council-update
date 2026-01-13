import React, { useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import Markdown from 'react-native-markdown-display';
import { Colors, Spacing, Typography, BorderRadius } from '../constants/theme';
import type { Message } from '../types';

interface MessageBubbleProps {
  message: Message;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const [expandedStage, setExpandedStage] = useState<1 | 2 | 3 | null>(null);

  if (message.role === 'user') {
    return (
      <View style={styles.userMessage}>
        <Text style={styles.userText}>{message.content}</Text>
      </View>
    );
  }

  // Assistant message with stages
  return (
    <View style={styles.assistantMessage}>
      {/* Stage 1: Council Responses */}
      {message.stage1 && (
        <View style={styles.stageContainer}>
          <TouchableOpacity
            style={styles.stageHeader}
            onPress={() => setExpandedStage(expandedStage === 1 ? null : 1)}
          >
            <Text style={styles.stageTitle}>
              Stage 1: Council Responses ({message.stage1.length} models)
            </Text>
            <Text style={styles.expandIcon}>
              {expandedStage === 1 ? '▼' : '▶'}
            </Text>
          </TouchableOpacity>

          {expandedStage === 1 && (
            <View style={styles.stageContent}>
              {message.stage1.map((response, idx) => (
                <View key={idx} style={styles.modelResponse}>
                  <Text style={styles.modelName}>{response.model}</Text>
                  <Markdown style={markdownStyles}>{response.response}</Markdown>
                </View>
              ))}
            </View>
          )}
        </View>
      )}

      {/* Stage 2: Rankings */}
      {message.stage2 && (
        <View style={styles.stageContainer}>
          <TouchableOpacity
            style={styles.stageHeader}
            onPress={() => setExpandedStage(expandedStage === 2 ? null : 2)}
          >
            <Text style={styles.stageTitle}>
              Stage 2: Peer Review
            </Text>
            <Text style={styles.expandIcon}>
              {expandedStage === 2 ? '▼' : '▶'}
            </Text>
          </TouchableOpacity>

          {expandedStage === 2 && (
            <View style={styles.stageContent}>
              {message.stage2.map((ranking, idx) => (
                <View key={idx} style={styles.modelResponse}>
                  <Text style={styles.modelName}>{ranking.model}</Text>
                  <Markdown style={markdownStyles}>{ranking.evaluation}</Markdown>
                  {ranking.ranking && ranking.ranking.length > 0 && (
                    <View style={styles.rankingList}>
                      <Text style={styles.rankingTitle}>Ranking:</Text>
                      {ranking.ranking.map((rank, i) => (
                        <Text key={i} style={styles.rankingItem}>
                          {i + 1}. {rank}
                        </Text>
                      ))}
                    </View>
                  )}
                </View>
              ))}
            </View>
          )}
        </View>
      )}

      {/* Stage 3: Final Synthesis */}
      {message.stage3 && (
        <View style={[styles.stageContainer, styles.stage3Container]}>
          <View style={styles.stageHeader}>
            <Text style={[styles.stageTitle, styles.stage3Title]}>
              Stage 3: Final Answer
            </Text>
          </View>
          <View style={styles.stageContent}>
            <Markdown style={markdownStyles}>{message.stage3}</Markdown>
          </View>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  userMessage: {
    alignSelf: 'flex-end',
    backgroundColor: Colors.primary,
    borderRadius: BorderRadius.lg,
    padding: Spacing.md,
    marginBottom: Spacing.md,
    maxWidth: '80%',
  },
  userText: {
    ...Typography.body,
    color: Colors.primaryForeground,
  },
  assistantMessage: {
    alignSelf: 'flex-start',
    width: '100%',
    marginBottom: Spacing.lg,
  },
  stageContainer: {
    backgroundColor: Colors.card,
    borderRadius: BorderRadius.lg,
    marginBottom: Spacing.sm,
    overflow: 'hidden',
  },
  stage3Container: {
    backgroundColor: Colors.primary,
  },
  stageHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: Spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: Colors.border,
  },
  stageTitle: {
    ...Typography.h3,
    color: Colors.foreground,
    flex: 1,
  },
  stage3Title: {
    color: Colors.primaryForeground,
  },
  expandIcon: {
    ...Typography.body,
    color: Colors.mutedForeground,
  },
  stageContent: {
    padding: Spacing.md,
  },
  modelResponse: {
    marginBottom: Spacing.lg,
  },
  modelName: {
    ...Typography.small,
    color: Colors.primary,
    fontWeight: '700',
    marginBottom: Spacing.xs,
  },
  rankingList: {
    marginTop: Spacing.sm,
    paddingLeft: Spacing.sm,
  },
  rankingTitle: {
    ...Typography.small,
    color: Colors.mutedForeground,
    fontWeight: '600',
    marginBottom: Spacing.xs,
  },
  rankingItem: {
    ...Typography.small,
    color: Colors.foreground,
    marginBottom: Spacing.xs,
  },
});

const markdownStyles = StyleSheet.create({
  body: {
    ...Typography.body,
    color: Colors.foreground,
  },
  heading1: {
    ...Typography.h2,
    color: Colors.foreground,
    marginTop: Spacing.sm,
    marginBottom: Spacing.xs,
  },
  heading2: {
    ...Typography.h3,
    color: Colors.foreground,
    marginTop: Spacing.sm,
    marginBottom: Spacing.xs,
  },
  paragraph: {
    ...Typography.body,
    color: Colors.foreground,
    marginBottom: Spacing.sm,
  },
  code_inline: {
    backgroundColor: Colors.muted,
    color: Colors.accent,
    paddingHorizontal: Spacing.xs,
    borderRadius: BorderRadius.sm,
    ...Typography.small,
  },
  code_block: {
    backgroundColor: Colors.muted,
    padding: Spacing.sm,
    borderRadius: BorderRadius.md,
    marginVertical: Spacing.sm,
  },
  fence: {
    backgroundColor: Colors.muted,
    padding: Spacing.sm,
    borderRadius: BorderRadius.md,
    marginVertical: Spacing.sm,
  },
  list_item: {
    ...Typography.body,
    color: Colors.foreground,
    marginBottom: Spacing.xs,
  },
});
