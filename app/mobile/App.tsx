import { StatusBar } from "expo-status-bar";
import { useState } from "react";
import {
  ActivityIndicator,
  Pressable,
  SafeAreaView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";

import type { LearnerProfile } from "../../shared/typescript/contracts";
import { sendSpeakingTurn } from "./src/api/client";

type PrimaryGrade = NonNullable<LearnerProfile["grade"]>;

const primaryGrades = [1, 2, 3, 4, 5, 6] as const satisfies readonly PrimaryGrade[];

const initialProfile: Omit<LearnerProfile, "grade"> = {
  level: 1 as const,
  confidence: 0.5,
  target_sentence_words: 4,
  interests: ["animals"],
  recent_topics: [],
};

export default function App() {
  const [grade, setGrade] = useState<PrimaryGrade>(1);
  const [transcript, setTranscript] = useState("I like dinosaur.");
  const [petReply, setPetReply] = useState("Hi! Tell me one thing you like.");
  const [voiceFruit, setVoiceFruit] = useState(0);
  const [busy, setBusy] = useState(false);

  async function speak() {
    setBusy(true);
    try {
      const turn = await sendSpeakingTurn({
        session_id: "local_demo_session",
        child_id: "local_anon_child",
        transcript,
        learner_profile: { ...initialProfile, grade },
      });
      setPetReply(turn.reply_text);
      setVoiceFruit((value) => value + turn.reward.base_voice_fruit + turn.reward.bonus_voice_fruit);
    } catch {
      setPetReply("I'm taking a tiny break. Let's try again!");
    } finally {
      setBusy(false);
    }
  }

  return (
    <SafeAreaView style={styles.screen}>
      <StatusBar style="dark" />
      <View style={styles.header}>
        <Text style={styles.title}>声生岛</Text>
        <Text style={styles.reward}>🍎 {voiceFruit}</Text>
      </View>
      <View style={styles.petCard}>
        <Text style={styles.pet}>🐾</Text>
        <Text style={styles.reply}>{petReply}</Text>
      </View>
      <Text style={styles.label}>选择孩子所在年级</Text>
      <View style={styles.gradeRow}>
        {primaryGrades.map((option) => {
          const selected = option === grade;
          return (
            <Pressable
              accessibilityLabel={`${option}年级`}
              accessibilityRole="button"
              accessibilityState={{ selected }}
              key={option}
              onPress={() => setGrade(option)}
              style={[styles.gradeButton, selected && styles.gradeButtonSelected]}
            >
              <Text style={[styles.gradeText, selected && styles.gradeTextSelected]}>{option}</Text>
            </Pressable>
          );
        })}
      </View>
      <Text style={styles.label}>MVP 转写输入（下一步替换为录音）</Text>
      <TextInput
        accessibilityLabel="English speaking transcript"
        style={styles.input}
        value={transcript}
        onChangeText={setTranscript}
        placeholder="Say something in English..."
      />
      <Pressable
        accessibilityRole="button"
        disabled={busy}
        onPress={speak}
        style={({ pressed }) => [styles.button, pressed && styles.buttonPressed]}
      >
        {busy ? <ActivityIndicator color="white" /> : <Text style={styles.buttonText}>我说完啦</Text>}
      </Pressable>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1, backgroundColor: "#FFF9E8", padding: 24, gap: 18 },
  header: { flexDirection: "row", justifyContent: "space-between", alignItems: "center" },
  title: { fontSize: 30, fontWeight: "800", color: "#275D50" },
  reward: { fontSize: 20, fontWeight: "700", color: "#8B552A" },
  petCard: {
    minHeight: 260,
    borderRadius: 28,
    backgroundColor: "#DDF5EB",
    alignItems: "center",
    justifyContent: "center",
    padding: 24,
    gap: 18,
  },
  pet: { fontSize: 88 },
  reply: { fontSize: 22, lineHeight: 30, textAlign: "center", color: "#173F36" },
  label: { color: "#5A625F" },
  gradeRow: { flexDirection: "row", gap: 8 },
  gradeButton: {
    flex: 1,
    minHeight: 42,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: "#A9D5C8",
    backgroundColor: "white",
    alignItems: "center",
    justifyContent: "center",
  },
  gradeButtonSelected: { borderColor: "#275D50", backgroundColor: "#DDF5EB" },
  gradeText: { color: "#5A625F", fontSize: 16, fontWeight: "700" },
  gradeTextSelected: { color: "#173F36" },
  input: {
    backgroundColor: "white",
    borderColor: "#A9D5C8",
    borderWidth: 2,
    borderRadius: 16,
    padding: 16,
    fontSize: 18,
  },
  button: { backgroundColor: "#EF7B45", padding: 17, borderRadius: 999, alignItems: "center" },
  buttonPressed: { opacity: 0.8 },
  buttonText: { color: "white", fontSize: 18, fontWeight: "800" },
});
