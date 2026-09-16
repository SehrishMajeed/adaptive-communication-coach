import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import type { PracticeSetup } from '../../../shared/types';

interface Props {
  setup: PracticeSetup;
}

export const PracticeContextCard: React.FC<Props> = ({ setup }) => {
  return (
    <View style={styles.card}>
      <Text style={styles.title}>Practice Context</Text>
      
      <Text style={styles.label}>Scenario:</Text>
      <Text style={styles.value}>{setup.scenario}</Text>

      <Text style={styles.label}>Audience:</Text>
      <Text style={styles.value}>{setup.audience}</Text>

      <Text style={styles.label}>Goal:</Text>
      <Text style={styles.value}>{setup.goal}</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#1E1E1E',
    padding: 16,
    borderRadius: 8,
    marginVertical: 12,
    borderWidth: 1,
    borderColor: '#333',
  },
  title: {
    fontSize: 16,
    fontWeight: '600',
    color: '#FFF',
    marginBottom: 12,
  },
  label: {
    fontSize: 12,
    color: '#AAA',
    marginTop: 8,
    textTransform: 'uppercase',
  },
  value: {
    fontSize: 14,
    color: '#EEE',
    marginTop: 2,
  },
});
