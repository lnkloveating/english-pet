import type { PropsWithChildren } from "react";
import { ImageBackground, StyleSheet, View } from "react-native";

const bedroom = require("../../assets/bedtime/bedroom-night-v2.png");

export function BedtimeScene({ children }: PropsWithChildren) {
  return (
    <ImageBackground
      accessibilityIgnoresInvertColors
      source={bedroom}
      resizeMode="cover"
      style={styles.scene}
      imageStyle={styles.background}
    >
      <View pointerEvents="none" style={styles.nightWash} />
      <View pointerEvents="none" style={styles.readabilityWash} />
      {children}
    </ImageBackground>
  );
}

const styles = StyleSheet.create({
  scene: {
    flex: 1,
    overflow: "hidden",
    backgroundColor: "#0D1929",
  },
  background: {
    opacity: 0.88,
  },
  nightWash: {
    position: "absolute",
    top: 0,
    right: 0,
    bottom: 0,
    left: 0,
    backgroundColor: "rgba(9, 22, 39, 0.25)",
  },
  readabilityWash: {
    position: "absolute",
    top: 0,
    left: 0,
    right: 0,
    height: 235,
    backgroundColor: "rgba(9, 22, 39, 0.42)",
  },
});
