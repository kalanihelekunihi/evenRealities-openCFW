
undefined8 FUN_004d3fc2(char param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  bool bVar1;
  char *pcVar2;
  byte *pbVar3;
  undefined4 uVar4;
  undefined4 local_18;
  uint local_14;
  undefined4 uStack_10;
  
  uVar4 = 0;
  local_18 = param_2;
  local_14 = param_3;
  uStack_10 = param_4;
  local_14 = FUN_00473940();
  pcVar2 = DAT_004d4090;
  if (param_1 == '\0') {
    if (*DAT_004d4090 != '\0') {
      *DAT_004d4090 = *DAT_004d4090 + -1;
    }
    pbVar3 = DAT_004d4094;
    if (*pcVar2 == '\0') {
      if (*DAT_004d4094 == 1) {
        FUN_0047f7ae(0x1c);
      }
      *pbVar3 = 0;
    }
    else {
      uVar4 = 3;
    }
  }
  else {
    *DAT_004d4090 = *DAT_004d4090 + '\x01';
    pbVar3 = DAT_004d4094;
    if (*DAT_004d4094 == 0) {
      *DAT_004d4094 = 1;
      FUN_0047f90c(0x1c,&local_18);
      if ((char)local_18 == '\0') {
        FUN_0047f5b8(0x1c);
      }
      else {
        *pbVar3 = *pbVar3 | 2;
      }
    }
  }
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    enableIRQinterrupts((local_14 & 1) == 1);
  }
  return CONCAT44(local_18,uVar4);
}

