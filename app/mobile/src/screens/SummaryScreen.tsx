import { Image, SafeAreaView, StyleSheet, Text, View } from "react-native";
import { BedtimeScene } from "../ui/BedtimeScene";
import { PrimaryButton } from "../ui/Controls";
import { colors, fonts } from "../ui/theme";

const momo = require("../../assets/bedtime/momo-sleeping.png");
export function SummaryScreen({onGoodnight}:{onGoodnight:()=>void}) {
  return <BedtimeScene><SafeAreaView style={styles.safe}>
    <View style={styles.paper}>
      <Text style={styles.eyebrow}>今晚的小故事</Text><Text style={styles.title}>我们聊了 6 轮</Text>
      <View style={styles.divider}/><Text style={styles.remember}>你让我记住了一句话</Text><Text style={styles.phrase}>Every little thing can be a happy thing.</Text>
    </View>
    <View style={styles.fruits} accessibilityLabel="获得六枚声果">{[0,1,2,3,4,5].map(i=><View key={i} style={styles.fruit}><View style={[styles.leaf,{transform:[{rotate:i%2?"28deg":"-28deg"}]}]}/></View>)}</View>
    <Image accessibilityLabel="Momo 靠着故事书睡着了" source={momo} resizeMode="contain" style={styles.momo}/>
    <View style={styles.bottom}><Text style={styles.goodnight}>谢谢你陪我说英语。晚安。</Text><PrimaryButton label="和 Momo 说晚安" onPress={onGoodnight}>和 Momo 说晚安</PrimaryButton></View>
  </SafeAreaView></BedtimeScene>;
}
const styles=StyleSheet.create({
  safe:{flex:1,paddingHorizontal:22,paddingTop:18},paper:{backgroundColor:colors.paper,paddingHorizontal:22,paddingVertical:22,borderRadius:24,borderWidth:1,borderColor:"#C7B38C",alignItems:"center"},
  eyebrow:{color:"#785B46",fontFamily:fonts.ui,fontSize:13,letterSpacing:1},title:{color:colors.ink,fontFamily:fonts.story,fontSize:28,fontWeight:"700",marginTop:8},divider:{width:36,height:2,backgroundColor:colors.clay,marginVertical:14},
  remember:{color:"#526076",fontFamily:fonts.ui,fontSize:14},phrase:{color:colors.ink,fontFamily:fonts.story,fontSize:20,lineHeight:28,textAlign:"center",marginTop:9},
  fruits:{flexDirection:"row",justifyContent:"center",gap:8,marginTop:13},fruit:{width:38,height:38,borderRadius:19,backgroundColor:colors.paper,borderWidth:1,borderColor:"#C7B38C",alignItems:"center",justifyContent:"center"},leaf:{width:12,height:20,borderTopLeftRadius:10,borderBottomRightRadius:10,backgroundColor:colors.moss},
  momo:{position:"absolute",left:"2%",width:"96%",height:"38%",bottom:118},bottom:{position:"absolute",left:22,right:22,bottom:22,gap:11},goodnight:{color:colors.mist,fontFamily:fonts.ui,fontSize:14,textAlign:"center"},
});
