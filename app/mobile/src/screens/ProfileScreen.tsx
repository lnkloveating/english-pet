import { useState } from "react";
import { Image, Pressable, SafeAreaView, StyleSheet, Text, View } from "react-native";
import { BedtimeScene } from "../ui/BedtimeScene";
import { QuietButton } from "../ui/Controls";
import { colors, fonts } from "../ui/theme";

const momo = require("../../assets/bedtime/momo-home.png");

function Toggle({ enabled, onPress, label }:{enabled:boolean;onPress:()=>void;label:string}) {
  return <Pressable accessibilityRole="switch" accessibilityLabel={label} accessibilityState={{checked:enabled}} onPress={onPress} style={[styles.toggle,enabled&&styles.toggleOn]}>
    <View style={[styles.toggleKnob,enabled&&styles.toggleKnobOn]}/>
  </Pressable>;
}

export function ProfileScreen({onBack,onOpenGarden}:{onBack:()=>void;onOpenGarden:()=>void}) {
  const [voice, setVoice] = useState(true);
  const [bedtime, setBedtime] = useState(true);

  return <BedtimeScene><SafeAreaView style={styles.safe}>
    <View style={styles.header}><QuietButton label="返回首页" text="‹" onPress={onBack}/><Text style={styles.headerTitle}>我的小岛</Text><View style={styles.headerSpace}/></View>

    <View style={styles.identity}>
      <View style={styles.avatar}><Image accessibilityLabel="Momo" source={momo} resizeMode="contain" style={styles.avatarImage}/></View>
      <View><Text style={styles.name}>小岛友</Text><Text style={styles.level}>一年级 · 和 Momo 相伴 7 天</Text></View>
    </View>

    <View style={styles.paper}>
      <Text style={styles.sectionLabel}>我的收藏</Text>
      <Pressable accessibilityRole="button" accessibilityLabel="打开声果花园，当前 24 枚" onPress={onOpenGarden} style={({pressed})=>[styles.rewardRow,pressed&&styles.rewardPressed]}>
        <View style={styles.fruit}><View style={styles.fruitLeaf}/></View>
        <View style={styles.rewardCopy}><View style={styles.rewardTitleRow}><Text style={styles.rewardNumber}>24 枚声果</Text><Text style={styles.chevron}>›</Text></View><Text style={styles.rewardHint}>让晚安小岛慢慢长大</Text><View style={styles.progressTrack}><View style={styles.progressFill}/></View><Text style={styles.nextReward}>再收集 6 枚，点亮一盏萤火灯</Text></View>
      </Pressable>
      <View style={styles.thread}/>
      <Text style={styles.sectionLabel}>今晚的设置</Text>
      <View style={styles.settingRow}><View><Text style={styles.settingTitle}>Momo 的声音</Text><Text style={styles.settingHint}>让 Momo 温柔地回应我</Text></View><Toggle label="Momo 的声音" enabled={voice} onPress={()=>setVoice(v=>!v)}/></View>
      <View style={styles.settingRow}><View><Text style={styles.settingTitle}>晚安模式</Text><Text style={styles.settingHint}>保持安静的夜间画面</Text></View><Toggle label="晚安模式" enabled={bedtime} onPress={()=>setBedtime(v=>!v)}/></View>
    </View>

    <Text style={styles.footer}>这里没有排名，只有你和 Momo 的故事。</Text>
  </SafeAreaView></BedtimeScene>;
}

const styles=StyleSheet.create({
  safe:{flex:1,paddingHorizontal:22,paddingTop:14},header:{height:50,flexDirection:"row",alignItems:"center",justifyContent:"space-between"},headerTitle:{color:colors.nightText,fontFamily:fonts.story,fontSize:20,fontWeight:"700"},headerSpace:{width:48},
  identity:{flexDirection:"row",alignItems:"center",gap:14,marginTop:24,marginBottom:18,paddingHorizontal:6},avatar:{width:76,height:76,borderRadius:38,overflow:"hidden",backgroundColor:colors.paper,borderWidth:2,borderColor:colors.moon},avatarImage:{width:"115%",height:"115%",marginLeft:"-7%",marginTop:"2%"},name:{color:colors.nightText,fontFamily:fonts.story,fontSize:24,fontWeight:"700"},level:{color:colors.mist,fontFamily:fonts.ui,fontSize:13,marginTop:5},
  paper:{backgroundColor:"rgba(242,226,197,.96)",borderRadius:24,borderWidth:1,borderColor:"#C7B38C",padding:20},sectionLabel:{color:"#785B46",fontFamily:fonts.ui,fontSize:12,fontWeight:"700",letterSpacing:1.4},rewardRow:{flexDirection:"row",alignItems:"center",gap:14,marginTop:10,paddingVertical:4,borderRadius:14},rewardPressed:{opacity:.72},fruit:{width:48,height:48,borderRadius:24,backgroundColor:colors.moss,alignItems:"center",justifyContent:"center",borderWidth:3,borderColor:"#849176"},fruitLeaf:{width:13,height:24,borderTopLeftRadius:12,borderBottomRightRadius:12,backgroundColor:colors.paper,transform:[{rotate:"-25deg"}]},rewardCopy:{flex:1},rewardTitleRow:{flexDirection:"row",alignItems:"center",justifyContent:"space-between"},rewardNumber:{color:colors.ink,fontFamily:fonts.story,fontSize:20,fontWeight:"700"},chevron:{color:"#785B46",fontSize:26,lineHeight:24},rewardHint:{color:"#657082",fontFamily:fonts.ui,fontSize:12,lineHeight:18,marginTop:1},progressTrack:{height:6,borderRadius:3,backgroundColor:"#D3C5A9",overflow:"hidden",marginTop:8},progressFill:{width:"80%",height:"100%",borderRadius:3,backgroundColor:colors.moss},nextReward:{color:"#785B46",fontFamily:fonts.ui,fontSize:11,marginTop:5},thread:{height:1,backgroundColor:"#C9B794",marginVertical:16},
  settingRow:{minHeight:68,flexDirection:"row",alignItems:"center",justifyContent:"space-between",borderBottomWidth:1,borderBottomColor:"rgba(151,126,92,.24)"},settingTitle:{color:colors.ink,fontFamily:fonts.ui,fontSize:16,fontWeight:"600"},settingHint:{color:"#657082",fontFamily:fonts.ui,fontSize:12,marginTop:4},toggle:{width:50,height:30,borderRadius:15,padding:3,backgroundColor:"#A9A79E"},toggleOn:{backgroundColor:colors.moss},toggleKnob:{width:24,height:24,borderRadius:12,backgroundColor:colors.paperLight},toggleKnobOn:{transform:[{translateX:20}]},
  footer:{position:"absolute",left:20,right:20,bottom:24,color:colors.mist,fontFamily:fonts.ui,fontSize:13,textAlign:"center"},
});
