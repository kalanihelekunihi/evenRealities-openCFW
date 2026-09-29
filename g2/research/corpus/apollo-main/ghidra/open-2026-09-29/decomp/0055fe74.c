
void semantic_TouchBuildAndSendFrame(int param_1,undefined1 param_2,int param_3,int param_4)

{
  undefined4 uVar1;
  undefined1 auStack_40 [4];
  undefined1 auStack_3c [36];
  int iStack_18;
  
  iStack_18 = param_4;
  semantic_TouchFrameInit(auStack_40);
  semantic_TouchFrameSetCommand(auStack_40,param_2);
  semantic_TouchFrameSetPayloadLength(auStack_40,param_4);
  if ((param_3 != 0) && (param_4 != 0)) {
    FUN_00439be4(auStack_3c,param_3,param_4);
  }
  uVar1 = semantic_TouchFrameChecksum16(auStack_40,param_4);
  semantic_TouchFrameSetChecksum(auStack_40,param_4,uVar1);
  semantic_TouchFrameSetTerminator(auStack_40,param_4);
  (**(code **)(param_1 + 8))(auStack_40,param_4 + 7U & 0xffff);
  return;
}

