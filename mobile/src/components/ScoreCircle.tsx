import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

interface Props {
  score: number;
  label: string;
}

export const ScoreCircle: React.FC<Props> = ({ score, label }) => {
  const getColor = (s: number) => {
    if (s >= 90) return '#4ADE80';
    if (s >= 70) return '#FBBF24';
    return '#F87171';
  };

  const color = getColor(score);

  return (
    <View style={styles.container}>
      <View style={[styles.circle, { borderColor: color }]}>
        <Text style={[styles.score, { color }]}>{score}</Text>
      </View>
      <Text style={styles.label}>{label}</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    alignItems: 'center',
    marginHorizontal: 8,
    width: 80,
  },
  circle: {
    width: 64,
    height: 64,
    borderRadius: 32,
    borderWidth: 4,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 8,
    backgroundColor: '#1E1E1E',
  },
  score: {
    fontSize: 20,
    fontWeight: 'bold',
  },
  label: {
    fontSize: 12,
    color: '#CCC',
    textAlign: 'center',
  },
});
