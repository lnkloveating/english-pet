import { requestRecordingPermissionsAsync, setAudioModeAsync, useAudioStream } from "expo-audio";
import * as Speech from "expo-speech";
import { useCallback, useEffect, useRef, useState } from "react";
import { Image, Pressable, SafeAreaView, StyleSheet, Text, View } from "react-native";
import { BedtimeScene } from "../ui/BedtimeScene";
import { MicIcon, QuietButton } from "../ui/Controls";
import { colors, fonts } from "../ui/theme";
import { resamplePcm16, sessionStart, VOICE_URL, type VoiceServerEvent } from "../voice/protocol";

const momo = require("../../assets/bedtime/momo-listening.png");
type VoiceState="connecting"|"ready"|"listening"|"thinking"|"speaking"|"error";
const prompts=["What made you smile today?","Who did you play with today?","What do you want to dream about?"];

export function ConversationScreen({onBack,onFinish}:{onBack:()=>void;onFinish:()=>void}) {
  const [state,setState]=useState<VoiceState>("connecting");
  const [turn,setTurn]=useState(0);
  const [transcript,setTranscript]=useState("");
  const [reply,setReply]=useState("");
  const [errorText,setErrorText]=useState("");
  const socketRef=useRef<WebSocket|null>(null);
  const recordingRef=useRef(false);
  const sessionReadyRef=useRef(false);
  const sessionIdRef=useRef(`bedtime_${Date.now()}`);

  const onAudioBuffer=useCallback(({data,sampleRate}:{data:ArrayBuffer;sampleRate:number})=>{
    const socket=socketRef.current;
    if(!recordingRef.current||!socket||socket.readyState!==WebSocket.OPEN)return;
    socket.send(resamplePcm16(data,sampleRate));
  },[]);
  const {stream}=useAudioStream({sampleRate:16000,channels:1,encoding:"int16",onBuffer:onAudioBuffer});

  const finishSpeaking=useCallback(()=>{
    setTurn(value=>value+1);
    setState("ready");
  },[]);

  const connect=useCallback(()=>{
    socketRef.current?.close();
    sessionReadyRef.current=false;
    setState("connecting");
    setErrorText("");
    const socket=new WebSocket(VOICE_URL);
    socket.binaryType="arraybuffer";
    socketRef.current=socket;
    socket.onopen=()=>socket.send(JSON.stringify(sessionStart(sessionIdRef.current,{
      grade:1,level:1,confidence:.5,target_sentence_words:4,interests:["animals","bedtime stories"],recent_topics:[],
    })));
    socket.onmessage=async event=>{
      if(typeof event.data!=="string")return;
      const message=JSON.parse(event.data) as VoiceServerEvent;
      if(message.type==="session.ready"){
        sessionReadyRef.current=true;
        setState("ready");
      }else if(message.type==="input.ready"){
        try{
          await stream.start();
          recordingRef.current=true;
          setTranscript("");
          setReply("");
          setState("listening");
        }catch{
          setErrorText("麦克风暂时没有准备好，再试一次吧。");
          setState("error");
        }
      }else if(message.type==="asr.partial"||message.type==="asr.final"){
        setTranscript(message.text);
        if(message.type==="asr.final")setState("thinking");
      }else if(message.type==="agent.reply"){
        setTranscript(message.transcript);
        setReply(message.turn.reply_text);
        setState("speaking");
        Speech.stop().finally(()=>Speech.speak(message.turn.reply_text,{
          language:"en-US",rate:.82,pitch:1.08,onDone:finishSpeaking,onStopped:finishSpeaking,onError:finishSpeaking,
        }));
      }else if(message.type==="error"){
        recordingRef.current=false;
        stream.stop();
        const friendly=message.error.code==="no_speech"?"我没有听清，再慢慢说一次吧。":"语音小路暂时有点堵，再试一次吧。";
        setErrorText(friendly);
        setState("error");
      }
    };
    socket.onerror=()=>{
      setErrorText("还没有连接到 Momo 的语音服务。");
      setState("error");
    };
    socket.onclose=()=>{
      sessionReadyRef.current=false;
      if(socketRef.current===socket&&state!=="error"){
        setErrorText("和 Momo 的连接断开了，点一下重新连接。");
        setState("error");
      }
    };
  },[finishSpeaking,stream]);

  useEffect(()=>{
    connect();
    return()=>{
      recordingRef.current=false;
      stream.stop();
      Speech.stop();
      const socket=socketRef.current;
      if(socket?.readyState===WebSocket.OPEN)socket.send(JSON.stringify({type:"session.close"}));
      socket?.close();
    };
  },[]);

  async function pressMic(){
    if(state==="error"){
      connect();
      return;
    }
    const socket=socketRef.current;
    if(state==="ready"){
      const permission=await requestRecordingPermissionsAsync();
      if(!permission.granted){
        setErrorText("需要打开麦克风权限，Momo 才能听见你。");
        setState("error");
        return;
      }
      await setAudioModeAsync({allowsRecording:true,playsInSilentMode:true,interruptionMode:"doNotMix"});
      if(!sessionReadyRef.current||!socket||socket.readyState!==WebSocket.OPEN){connect();return;}
      setState("connecting");
      socket.send(JSON.stringify({type:"input.start"}));
    }else if(state==="listening"){
      recordingRef.current=false;
      stream.stop();
      setState("thinking");
      socket?.send(JSON.stringify({type:"input.commit"}));
    }
  }

  const labels:{[K in VoiceState]:string}={connecting:"Momo 正在准备耳朵……",ready:"点一下，说给我听",listening:"我在听，再点一下结束",thinking:"让我想一想……",speaking:"Momo 正在回答",error:errorText||"再试一次吧"};
  const disabled=state==="connecting"||state==="thinking"||state==="speaking";
  return <BedtimeScene><SafeAreaView style={styles.safe}>
    <View style={styles.top}><QuietButton label="返回首页" text="‹" onPress={onBack}/><View style={styles.progress} accessibilityLabel={`今晚第 ${turn+1} 轮`}><View style={styles.progressFill}/><View style={turn>0?styles.progressFill:styles.progressEmpty}/><View style={turn>1?styles.progressFill:styles.progressEmpty}/></View><Pressable accessibilityRole="button" accessibilityLabel="结束今晚的对话" onPress={onFinish} style={styles.finish}><Text style={styles.finishText}>结束</Text></Pressable></View>
    <View style={styles.paper}><Text style={styles.question}>{reply||prompts[turn%prompts.length]}</Text><Text style={styles.translation}>{transcript?`你说：${transcript}`:(turn===0?"今天有什么让你开心的事吗？":"慢慢说，我会认真听。")}</Text></View>
    <Image accessibilityLabel="Momo 正认真听你说话" source={momo} resizeMode="contain" style={styles.momo}/>
    <View style={styles.micZone}>
      <View accessibilityLiveRegion="polite"><Text style={[styles.stateText,state==="error"&&styles.errorText]}>{labels[state]}</Text></View>
      <Pressable disabled={disabled} accessibilityRole="button" accessibilityLabel={labels[state]} accessibilityState={{disabled}} onPress={pressMic} style={({pressed})=>[styles.micButton,state==="listening"&&styles.micListening,state==="error"&&styles.micError,pressed&&styles.micPressed]}><MicIcon active={state==="listening"}/></Pressable>
      <View style={styles.waves}>{[12,24,38,20,30].map((height,index)=><View key={index} style={[styles.wave,{height},state==="listening"&&styles.waveActive]}/>)}</View>
    </View>
  </SafeAreaView></BedtimeScene>;
}
const styles=StyleSheet.create({
  safe:{flex:1,paddingHorizontal:20,paddingTop:10},top:{flexDirection:"row",alignItems:"center",justifyContent:"space-between"},progress:{flexDirection:"row",gap:6},progressFill:{width:22,height:5,borderRadius:3,backgroundColor:colors.moon},progressEmpty:{width:22,height:5,borderRadius:3,backgroundColor:colors.night700},
  finish:{minWidth:48,minHeight:48,alignItems:"center",justifyContent:"center"},finishText:{color:colors.mist,fontFamily:fonts.ui,fontSize:15},
  paper:{marginTop:20,backgroundColor:colors.paper,paddingHorizontal:22,paddingVertical:20,borderRadius:24,borderWidth:1,borderColor:"#C7B38C",alignItems:"center",minHeight:104},
  question:{color:colors.ink,fontFamily:fonts.story,fontWeight:"700",fontSize:23,lineHeight:30,textAlign:"center"},translation:{color:"#526076",fontFamily:fonts.ui,fontSize:13,lineHeight:20,textAlign:"center",marginTop:7},
  momo:{position:"absolute",left:"8%",width:"84%",height:"47%",top:"31%"},micZone:{position:"absolute",left:20,right:20,bottom:18,alignItems:"center"},stateText:{color:colors.nightText,fontFamily:fonts.ui,fontSize:15,marginBottom:10},errorText:{color:colors.paperLight},
  micButton:{width:126,height:126,borderRadius:63,backgroundColor:colors.paperLight,borderWidth:10,borderColor:colors.moss,alignItems:"center",justifyContent:"center"},micListening:{borderColor:colors.clay},micError:{borderColor:colors.berry},micPressed:{transform:[{scale:.98}]},
  waves:{position:"absolute",right:16,bottom:46,height:40,flexDirection:"row",alignItems:"center",gap:4},wave:{width:3,borderRadius:2,backgroundColor:colors.night700},waveActive:{backgroundColor:colors.moon},
});
