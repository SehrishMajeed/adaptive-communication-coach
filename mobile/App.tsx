import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { RootStackParamList } from './src/app/NavigationTypes';

import { SetupScreen } from './src/screens/SetupScreen';
import { RecordScreen } from './src/screens/RecordScreen';
import { ReviewScreen } from './src/screens/ReviewScreen';
import { FeedbackScreen } from './src/screens/FeedbackScreen';

const Stack = createNativeStackNavigator<RootStackParamList>();

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator initialRouteName="Setup" screenOptions={{ headerShown: false }}>
        <Stack.Screen name="Setup" component={SetupScreen} />
        <Stack.Screen name="Record" component={RecordScreen} />
        <Stack.Screen name="Review" component={ReviewScreen} />
        <Stack.Screen name="Feedback" component={FeedbackScreen} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
