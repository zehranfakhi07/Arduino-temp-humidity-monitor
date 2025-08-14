### Mobile (Expo React Native)

- Install Node 18+ and Expo CLI: `npm i -g expo-cli` (or use `npx expo`)
- Configure API base URL for your device:
  - Create `.env` in `mobile/` with:

```bash
EXPO_PUBLIC_API_BASE=http://<your_host_ip>:8000
```

- Install deps and run:

```bash
cd mobile
npm install
npm run start
```

- Open on Android/iOS using Expo Go, or run `npm run android` / `npm run ios`.