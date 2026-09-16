import React from 'react';
import { View, ActivityIndicator, Text, StyleSheet } from 'react-native';

interface Props {
  text?: string;
}

export const Loader: React.FC<Props> = ({ text }) => {
  return (
    <View style={styles.container}>
      <ActivityIndicator size="large" color="#4ADE80" />
      {text && <Text style={styles.text}>{text}</Text>}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#121212',
  },
  text: {
    marginTop: 16,
    color: '#FFF',
    fontSize: 16,
  },
});
