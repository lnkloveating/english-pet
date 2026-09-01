import { SafeAreaView, StyleSheet, Text, View } from "react-native";
import { BedtimeScene } from "../ui/BedtimeScene";
import { QuietButton } from "../ui/Controls";
import { colors, fonts } from "../ui/theme";

function Leaf({left,top,rotate,small=false}:{left:number;top:number;rotate:string;small?:boolean}) {
  return <View style={[styles.leaf,{left,top,width:small?13:18,height:small?24:32,transform:[{rotate}]}]}/>;
}

export function VoiceFruitGardenScreen({onBack}:{onBack:()=>void}) {
  return <BedtimeScene><SafeAreaView style={styles.safe}>
    <View style={styles.header}><QuietButton label="返回个人中心" text="‹" onPress={onBack}/><View style={styles.headerCopy}><Text style={styles.title}>声果花园</Text><Text style={styles.subtitle}>你的每句话，都在这里生长</Text></View><View style={styles.headerSpace}/></View>

    <View style={styles.garden} accessibilityLabel="晚安树已经长出嫩芽，下一步将点亮萤火灯">
      <View style={styles.moon}/><View style={styles.glowOne}/><View style={styles.glowTwo}/>
      <View style={styles.treeCrown}/><View style={styles.trunk}/>
      <Leaf left={101} top={91} rotate="-38deg"/><Leaf left={139} top={72} rotate="24deg"/><Leaf left={167} top={108} rotate="48deg"/><Leaf left={116} top={127} rotate="-64deg" small/><Leaf left={156} top={143} rotate="32deg" small/>
      <View style={styles.ground}/><Text style={styles.stageName}>嫩芽长大了</Text><Text style={styles.stageHint}>24 枚声果正在照顾这棵晚安树</Text>
    </View>

    <View style={styles.paper}>
      <View style={styles.countRow}><View><Text style={styles.countLabel}>下一份小惊喜</Text><Text style={styles.count}>24 / 30</Text></View><View style={styles.lantern}><View style={styles.lanternGlow}/></View></View>
      <View style={styles.track}><View style={styles.fill}/></View>
      <Text style={styles.goal}>再勇敢开口 6 次，树下会亮起第一盏萤火灯。</Text>
      <View style={styles.rule}/>
      <View style={styles.howRow}><View style={styles.number}><Text style={styles.numberText}>1</Text></View><Text style={styles.howText}>说完一句有效的英语，获得 1 枚声果</Text></View>
      <View style={styles.howRow}><View style={styles.number}><Text style={styles.numberText}>2</Text></View><Text style={styles.howText}>声果不会被花掉，会一直记录你的勇敢</Text></View>
      <View style={styles.howRow}><View style={styles.number}><Text style={styles.numberText}>3</Text></View><Text style={styles.howText}>花园长大后，会带来新话题和小岛装饰</Text></View>
    </View>
    <Text style={styles.footer}>不需要连续打卡，想说的时候再回来。</Text>
  </SafeAreaView></BedtimeScene>;
}

const styles=StyleSheet.create({
  safe:{flex:1,paddingHorizontal:20,paddingTop:14},header:{height:54,flexDirection:"row",alignItems:"center",justifyContent:"space-between"},headerCopy:{alignItems:"center"},title:{color:colors.nightText,fontFamily:fonts.story,fontSize:21,fontWeight:"700"},subtitle:{color:colors.mist,fontFamily:fonts.ui,fontSize:11,marginTop:2},headerSpace:{width:48},
  garden:{height:265,marginTop:12,borderRadius:26,overflow:"hidden",backgroundColor:"rgba(18,39,61,.86)",borderWidth:1,borderColor:"rgba(216,180,107,.45)"},moon:{position:"absolute",right:28,top:24,width:38,height:38,borderRadius:19,backgroundColor:colors.paper},glowOne:{position:"absolute",left:54,top:62,width:7,height:7,borderRadius:4,backgroundColor:colors.moon},glowTwo:{position:"absolute",right:75,top:92,width:5,height:5,borderRadius:3,backgroundColor:colors.moon},treeCrown:{position:"absolute",left:82,top:42,width:120,height:142,borderTopLeftRadius:70,borderTopRightRadius:64,borderBottomLeftRadius:46,borderBottomRightRadius:54,backgroundColor:"#53654D",borderWidth:4,borderColor:"#71806A"},trunk:{position:"absolute",left:135,top:148,width:20,height:66,borderRadius:9,backgroundColor:"#7B593E"},leaf:{position:"absolute",zIndex:2,borderTopLeftRadius:18,borderBottomRightRadius:18,backgroundColor:"#D4B76E",borderWidth:1,borderColor:"#E4CE8D"},ground:{position:"absolute",left:32,right:32,bottom:42,height:28,borderRadius:50,backgroundColor:"#334C42"},stageName:{position:"absolute",left:0,right:0,bottom:20,color:colors.nightText,fontFamily:fonts.story,fontSize:17,fontWeight:"700",textAlign:"center"},stageHint:{position:"absolute",left:0,right:0,bottom:4,color:colors.mist,fontFamily:fonts.ui,fontSize:10,textAlign:"center"},
  paper:{marginTop:12,backgroundColor:"rgba(242,226,197,.97)",borderRadius:24,borderWidth:1,borderColor:"#C7B38C",padding:18},countRow:{flexDirection:"row",alignItems:"center",justifyContent:"space-between"},countLabel:{color:"#785B46",fontFamily:fonts.ui,fontSize:12},count:{color:colors.ink,fontFamily:fonts.story,fontSize:24,fontWeight:"700",marginTop:2},lantern:{width:44,height:44,borderRadius:22,borderWidth:2,borderColor:colors.moon,alignItems:"center",justifyContent:"center"},lanternGlow:{width:18,height:25,borderRadius:9,backgroundColor:"#D9CBA8",opacity:.55},track:{height:8,borderRadius:4,backgroundColor:"#D3C5A9",overflow:"hidden",marginTop:10},fill:{width:"80%",height:"100%",backgroundColor:colors.moss},goal:{color:colors.ink,fontFamily:fonts.ui,fontSize:13,lineHeight:19,marginTop:10},rule:{height:1,backgroundColor:"#C9B794",marginVertical:13},howRow:{flexDirection:"row",alignItems:"center",gap:10,marginBottom:9},number:{width:24,height:24,borderRadius:12,backgroundColor:colors.moss,alignItems:"center",justifyContent:"center"},numberText:{color:colors.paperLight,fontFamily:fonts.ui,fontSize:12,fontWeight:"700"},howText:{flex:1,color:"#4E5D6E",fontFamily:fonts.ui,fontSize:12,lineHeight:17},footer:{position:"absolute",left:20,right:20,bottom:16,color:colors.mist,fontFamily:fonts.ui,fontSize:12,textAlign:"center"},
});
