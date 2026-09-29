
undefined8 FUN_004e2a5c(undefined4 param_1,undefined4 param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  
  if (param_3 == 10) {
    FUN_0045a568();
  }
  else if (param_3 == 0x48) {
    iVar1 = FUN_0045a568();
    if (iVar1 != 2) {
      even_ai_stream_event_forward(0x48,param_4);
    }
  }
  else if (param_3 == 0x44) {
    iVar1 = FUN_0045a568();
    if (iVar1 != 2) {
      even_ai_stream_event_forward(0x44,param_4);
    }
  }
  else if ((param_3 == 0x45) && (iVar1 = FUN_0045a568(), iVar1 != 2)) {
    even_ai_stream_event_forward(0x45,param_4);
  }
  return CONCAT44(param_4,1);
}

