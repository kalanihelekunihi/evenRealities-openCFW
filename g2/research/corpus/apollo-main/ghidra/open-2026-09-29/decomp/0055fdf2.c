
void semantic_TouchSendCommandRetry(int param_1,undefined4 param_2,undefined1 param_3,uint param_4)

{
  int iVar1;
  char cVar2;
  uint local_18;
  
  local_18 = param_4 & 0xffffff00;
  cVar2 = 'd';
  do {
    if (cVar2 == '\0') {
      return;
    }
    FUN_004910f4(1);
    iVar1 = (**(code **)(param_1 + 0xc))(param_2,param_3);
    if (iVar1 == 0) {
      semantic_TouchValidateReply(param_3,param_2,&local_18);
      if ((char)local_18 != '\0') {
        return;
      }
    }
    cVar2 = cVar2 + -1;
  } while( true );
}

