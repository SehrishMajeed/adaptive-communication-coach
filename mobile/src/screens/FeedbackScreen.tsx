import React from 'react';
import { View, Text, StyleSheet, ScrollView, SafeAreaView, TouchableOpacity } from 'react-native';
import type { NativeStackScreenProps } from '@react-navigation/native-stack';
import type { RootStackParamList } from '../app/NavigationTypes';
import { PracticeContextCard } from '../components/PracticeContextCard';
import { ScoreCircle } from '../components/ScoreCircle';

type Props = NativeStackScreenProps<RootStackParamList, 'Feedback'>;

export const FeedbackScreen: React.FC<Props> = ({ navigation, route }) => {
  const { setup, result } = route.params;

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView contentContainerStyle={styles.container}>
        <Text style={styles.header}>Your Feedback</Text>
        
        <PracticeContextCard setup={setup} />
        
        <View style={styles.scoresContainer}>
          <ScoreCircle score={Math.round(((result.feedback.evaluation.clarity || 0) + (result.feedback.evaluation.structure || 0) + (result.feedback.evaluation.conciseness || 0) + (result.feedback.evaluation.audience_awareness || 0)) / 4 * 10)} label="Overall" />
          <ScoreCircle score={(result.feedback.evaluation.clarity || 0) * 10} label="Clarity" />
          <ScoreCircle score={(result.feedback.evaluation.structure || 0) * 10} label="Structure" />
        </View>

        <View style={styles.feedbackSection}>
          <Text style={styles.sectionTitle}>What You Did Well</Text>
          <Text style={styles.feedbackText}>{result.feedback.evaluation.strengths.join('\n')}</Text>
        </View>

        <View style={styles.feedbackSection}>
          <Text style={styles.sectionTitle}>Areas for Improvement</Text>
          <Text style={styles.feedbackText}>{result.feedback.evaluation.weaknesses.join('\n')}</Text>
        </View>

        <TouchableOpacity 
          style={styles.doneButton} 
          onPress={() => navigation.navigate('Setup')}
          accessibilityRole="button"
          accessibilityLabel="Done"
          accessibilityHint="Returns to the Setup screen"
        >
          <Text style={styles.doneText}>Done</Text>
        </TouchableOpacity>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#121212',
  },
  container: {
    padding: 16,
  },
  header: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#FFF',
    marginBottom: 16,
    textAlign: 'center',
  },
  scoresContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    marginVertical: 24,
  },
  feedbackSection: {
    backgroundColor: '#1E1E1E',
    padding: 16,
    borderRadius: 8,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#333',
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#4ADE80',
    marginBottom: 8,
  },
  feedbackText: {
    fontSize: 16,
    color: '#EEE',
    lineHeight: 24,
  },
  doneButton: {
    backgroundColor: '#3B82F6',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 16,
    marginBottom: 40,
  },
  doneText: {
    color: '#FFF',
    fontSize: 18,
    fontWeight: 'bold',
  },
});
