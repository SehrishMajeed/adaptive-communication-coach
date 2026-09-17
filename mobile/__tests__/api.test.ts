import { apiBase } from '../src/services/api';

describe('mobile API configuration', () => {
  it('uses localhost in dev so adb reverse can connect a real Android device to the backend', () => {
    expect(apiBase()).toBe('http://localhost:8000');
  });
});
