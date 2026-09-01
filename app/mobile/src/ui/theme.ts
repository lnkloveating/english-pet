import { Platform } from "react-native";

export const colors = {
  night950: "#0D1929", night900: "#13253C", night800: "#203A58", night700: "#294764",
  paper: "#F2E2C5", paperLight: "#F8ECD7", ink: "#17283F", moon: "#D8B46B",
  clay: "#B96850", clayPressed: "#98513F", moss: "#68765A", mist: "#AAB8C7",
  berry: "#B66461", nightText: "#F4E8D2", shadow: "#07111E",
};

export const fonts = {
  ui: Platform.select({ ios: "System", android: "sans-serif", web: "system-ui" }),
  story: Platform.select({ ios: "Iowan Old Style", android: "serif", web: "Georgia" }),
};
