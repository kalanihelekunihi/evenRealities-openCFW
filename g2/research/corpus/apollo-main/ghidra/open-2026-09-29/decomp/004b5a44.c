
undefined4
GattSendServiceChangedInd(char param_1,undefined2 param_2,undefined2 param_3,undefined4 param_4)

{
  char *pcVar1;
  int iVar2;
  byte bVar3;
  undefined4 local_10;
  
  pcVar1 = DAT_004b5ad8;
  local_10 = param_4;
  if (*DAT_004b5ad8 != '\0') {
    local_10 = CONCAT13((char)((ushort)param_3 >> 8),CONCAT12((char)param_3,param_2));
    if (param_1 == '\0') {
      for (bVar3 = 1; bVar3 < 4; bVar3 = bVar3 + 1) {
        iVar2 = AttsCccEnabled(bVar3,pcVar1[1]);
        if (iVar2 != 0) {
          AttsHandleValueInd(bVar3,0x12,4,&local_10);
        }
      }
    }
    else {
      iVar2 = AttsCccEnabled(param_1,DAT_004b5ad8[1]);
      if (iVar2 != 0) {
        AttsHandleValueInd(param_1,0x12,4,&local_10);
      }
    }
  }
  return local_10;
}

