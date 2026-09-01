import { Image, Pressable, SafeAreaView, StyleSheet, Text, View } from "react-native";
import { BedtimeScene } from "../ui/BedtimeScene";
import { PrimaryButton } from "../ui/Controls";
import { colors, fonts } from "../ui/theme";

const momo = require("../../assets/bedtime/momo-home.png");

export function HomeScreen({onStart,onProfile}:{onStart:()=>void;onProfile:()=>void}) {
  return <BedtimeScene><SafeAreaView style={styles.safe}>
    <View style={styles.header}>
      <View accessibilityLabel="声生岛晚安篇" style={styles.brand}><View style={styles.logoMark}><View style={styles.earLeft}/><View style={styles.earRight}/><View style={styles.island}/><View style={styles.logoLeaf}/></View><View><Text style={styles.brandText}>声生岛</Text><Text style={styles.edition}>晚安篇</Text></View></View>
      <Pressable accessibilityRole="button" accessibilityLabel="打开个人中心" onPress={onProfile} hitSlop={8} style={({pressed})=>[styles.profile,pressed&&styles.profilePressed]}><View style={styles.profileHead}/><View style={styles.profileBody}/></Pressable>
    </View>
    <View style={styles.copy}><Text style={styles.title}>晚上好，小朋友</Text><Text style={styles.subtitle}>今天想和 Momo 聊什么呢？</Text></View>
    <Image accessibilityLabel="Momo 坐在睡前故事书旁等你" source={momo} resizeMode="contain" style={styles.momo}/>
    <View style={styles.bottom}><Text style={styles.hint}>一段三分钟的晚安英语</Text><PrimaryButton label="开始今晚的故事" onPress={onStart}>开始今晚的故事</PrimaryButton></View>
  </SafeAreaView></BedtimeScene>;
}
const styles=StyleSheet.create({
  safe:{flex:1,paddingHorizontal:24,paddingTop:14},header:{height:48,flexDirection:"row",alignItems:"center",justifyContent:"space-between"},brand:{flexDirection:"row",alignItems:"center",gap:9},
  logoMark:{width:34,height:30,position:"relative"},earLeft:{position:"absolute",left:6,top:1,width:11,height:12,backgroundColor:colors.moon,borderTopLeftRadius:9,transform:[{rotate:"-18deg"}]},earRight:{position:"absolute",right:6,top:1,width:11,height:12,backgroundColor:colors.moon,borderTopRightRadius:9,transform:[{rotate:"18deg"}]},island:{position:"absolute",left:3,right:3,bottom:2,height:14,borderTopLeftRadius:16,borderTopRightRadius:16,borderBottomLeftRadius:6,borderBottomRightRadius:6,backgroundColor:colors.moon},logoLeaf:{position:"absolute",width:9,height:5,left:13,bottom:6,borderTopLeftRadius:8,borderBottomRightRadius:8,backgroundColor:colors.moss,transform:[{rotate:"-24deg"}]},
  brandText:{color:colors.moon,fontFamily:fonts.story,fontSize:15,fontWeight:"700",letterSpacing:1.2,lineHeight:17},edition:{color:colors.mist,fontFamily:fonts.ui,fontSize:10,letterSpacing:2,lineHeight:12},
  profile:{width:44,height:44,borderRadius:22,borderWidth:1.5,borderColor:colors.moon,alignItems:"center",justifyContent:"center",backgroundColor:"rgba(13,25,41,.62)"},profilePressed:{opacity:.72,transform:[{scale:.96}]},profileHead:{width:9,height:9,borderRadius:5,backgroundColor:colors.paper},profileBody:{width:17,height:9,marginTop:3,borderTopLeftRadius:9,borderTopRightRadius:9,backgroundColor:colors.paper},
  copy:{marginTop:36,alignItems:"center"},
  title:{color:colors.nightText,fontFamily:fonts.story,fontSize:29,lineHeight:38,fontWeight:"700",textAlign:"center"},subtitle:{color:colors.mist,fontFamily:fonts.ui,fontSize:16,lineHeight:24,marginTop:8,textAlign:"center"},
  momo:{position:"absolute",width:"92%",height:"51%",left:"4%",bottom:132},bottom:{position:"absolute",left:24,right:24,bottom:24,gap:12},
  hint:{color:colors.mist,textAlign:"center",fontFamily:fonts.ui,fontSize:13,letterSpacing:.5},
});
