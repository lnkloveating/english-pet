import type { PropsWithChildren } from "react";
import { ImageBackground, Pressable, StyleSheet, Text, View } from "react-native";
import { colors, fonts } from "./theme";

const clayLinen = require("../../assets/bedtime/clay-linen-v2.png");

export function PrimaryButton({children,onPress,label}:PropsWithChildren<{onPress:()=>void;label:string}>) {
  return <Pressable accessibilityRole="button" accessibilityLabel={label} onPress={onPress} style={({pressed})=>[styles.primary,pressed&&styles.primaryPressed]}>
    <ImageBackground source={clayLinen} resizeMode="cover" imageStyle={styles.primaryTexture} style={styles.primaryTextureFrame}>
      <View pointerEvents="none" style={styles.stitchLine}/>
      <View pointerEvents="none" style={styles.buttonFlourish}><View style={styles.flourishLine}/><View style={styles.flourishLeaf}/><View style={[styles.flourishLeaf,styles.flourishLeafRight]}/></View>
      <Text style={styles.primaryText}>{children}</Text>
    </ImageBackground>
  </Pressable>;
}
export function QuietButton({label,text,onPress}:{label:string;text:string;onPress:()=>void}) {
  return <Pressable accessibilityRole="button" accessibilityLabel={label} onPress={onPress} style={({pressed})=>[styles.quiet,pressed&&styles.quietPressed]}><Text style={styles.quietText}>{text}</Text></Pressable>;
}
export function MicIcon({active=false}:{active?:boolean}) {
  return <View style={styles.micIcon}><View style={[styles.micCapsule,active&&styles.micActive]}/><View style={styles.micArc}/><View style={styles.micStem}/><View style={styles.micFoot}/></View>;
}
const styles=StyleSheet.create({
  primary:{minHeight:64,borderRadius:21,overflow:"hidden",backgroundColor:colors.clay,borderWidth:1,borderColor:"#D8A17E",shadowColor:colors.shadow,shadowOpacity:.28,shadowRadius:8,shadowOffset:{width:0,height:4},elevation:4},
  primaryPressed:{opacity:.88,transform:[{scale:.985}]},
  primaryTextureFrame:{minHeight:62,alignItems:"center",justifyContent:"center",paddingHorizontal:24,backgroundColor:"rgba(185,104,80,.76)"},primaryTexture:{opacity:.28},
  stitchLine:{position:"absolute",top:5,right:5,bottom:5,left:5,borderRadius:16,borderWidth:1,borderStyle:"dashed",borderColor:"rgba(248,236,215,.48)"},
  buttonFlourish:{position:"absolute",bottom:7,flexDirection:"row",alignItems:"center",gap:2},flourishLine:{width:18,height:1,backgroundColor:"rgba(248,236,215,.58)"},
  flourishLeaf:{width:7,height:4,borderTopLeftRadius:7,borderBottomRightRadius:7,backgroundColor:"rgba(248,236,215,.58)",transform:[{rotate:"-28deg"}]},flourishLeafRight:{transform:[{rotate:"28deg"}]},
  primaryText:{color:colors.paperLight,fontFamily:fonts.story,fontSize:19,fontWeight:"700",letterSpacing:.3,textShadowColor:"rgba(74,35,28,.28)",textShadowOffset:{width:0,height:1},textShadowRadius:1},
  quiet:{width:48,height:48,borderRadius:24,alignItems:"center",justifyContent:"center",backgroundColor:colors.paper,borderWidth:1,borderColor:"#CBB991"},
  quietPressed:{backgroundColor:"#DFCBAA",transform:[{scale:.97}]},quietText:{color:colors.ink,fontSize:22,fontWeight:"700"},
  micIcon:{width:56,height:64,alignItems:"center"},micCapsule:{width:22,height:36,borderRadius:12,backgroundColor:colors.ink},micActive:{backgroundColor:colors.clay},
  micArc:{width:40,height:28,marginTop:-22,borderWidth:4,borderTopWidth:0,borderColor:colors.ink,borderBottomLeftRadius:22,borderBottomRightRadius:22},
  micStem:{width:4,height:11,backgroundColor:colors.ink},micFoot:{width:28,height:4,borderRadius:2,backgroundColor:colors.ink},
});
