import AsyncStorage from '@react-native-async-storage/async-storage';

const OWNER_TOKEN_KEY = 'aura_coach_owner_token';

const randomId = () => {
  return `id-${Date.now()}-${Math.random().toString(16).slice(2)}`;
};

export async function getOwnerToken(): Promise<string> {
  try {
    let token = await AsyncStorage.getItem(OWNER_TOKEN_KEY);
    if (!token) {
      token = randomId();
      await AsyncStorage.setItem(OWNER_TOKEN_KEY, token);
    }
    return token;
  } catch (e) {
    // Fallback if AsyncStorage fails, token will be valid for the session
    return randomId();
  }
}
