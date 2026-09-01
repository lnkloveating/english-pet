import { StatusBar } from "expo-status-bar";
import { useState } from "react";
import { Platform, StyleSheet, View, useWindowDimensions, type ViewStyle } from "react-native";

import { ConversationScreen } from "./src/screens/ConversationScreen";
import { HomeScreen } from "./src/screens/HomeScreen";
import { ProfileScreen } from "./src/screens/ProfileScreen";
import { VoiceFruitGardenScreen } from "./src/screens/VoiceFruitGardenScreen";
import { SummaryScreen } from "./src/screens/SummaryScreen";
import { colors } from "./src/ui/theme";

type Screen = "home" | "conversation" | "summary" | "profile" | "garden";

export default function App() {
  const [screen, setScreen] = useState<Screen>("home");
  const { width, height } = useWindowDimensions();
  const framedWeb = Platform.OS === "web" && width > 520;

  return (
    <View style={[styles.stage, { minHeight: height }]}>
      <StatusBar style="light" />
      <View style={[styles.phone, {
        width: framedWeb ? Math.min(430, width - 48) : width,
        height: framedWeb ? Math.min(900, height - 40) : height,
      }, framedWeb && styles.phoneFramed]}>
        {screen === "home" && <HomeScreen onStart={() => setScreen("conversation")} onProfile={() => setScreen("profile")} />}
        {screen === "profile" && <ProfileScreen onBack={() => setScreen("home")} onOpenGarden={() => setScreen("garden")} />}
        {screen === "garden" && <VoiceFruitGardenScreen onBack={() => setScreen("profile")} />}
        {screen === "conversation" && <ConversationScreen onBack={() => setScreen("home")} onFinish={() => setScreen("summary")} />}
        {screen === "summary" && <SummaryScreen onGoodnight={() => setScreen("home")} />}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  stage: { flex: 1, alignItems: "center", justifyContent: "center", backgroundColor: colors.night950 },
  phone: { overflow: "hidden", backgroundColor: colors.night900 },
  phoneFramed: Platform.select({
    web: {
      borderRadius: 34, borderWidth: 1, borderColor: colors.night700,
      boxShadow: `0 22px 42px ${colors.shadow}`,
    },
    default: {
      borderRadius: 34, borderWidth: 1, borderColor: colors.night700,
      shadowColor: colors.shadow, shadowOffset: { width: 0, height: 22 }, shadowOpacity: 0.38, shadowRadius: 42,
      elevation: 16,
    },
  }) as ViewStyle,
});
