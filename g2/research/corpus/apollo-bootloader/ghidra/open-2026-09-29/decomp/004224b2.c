
undefined8 FUN_004224b2(char param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

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
  local_14 = critical_save();
  pcVar2 = DAT_00422580;
  if (param_1 == '\0') {
    if (*DAT_00422580 != '\0') {
      *DAT_00422580 = *DAT_00422580 + -1;
    }
    pbVar3 = DAT_00422584;
    if (*pcVar2 == '\0') {
      if (*DAT_00422584 == 1) {
        FUN_0041c17a(0x1c);
      }
      *pbVar3 = 0;
    }
    else {
      uVar4 = 3;
    }
  }
  else {
    *DAT_00422580 = *DAT_00422580 + '\x01';
    pbVar3 = DAT_00422584;
    if (*DAT_00422584 == 0) {
      *DAT_00422584 = 1;
      FUN_0041c2d8(0x1c,&local_18);
      if ((char)local_18 == '\0') {
        FUN_0041bf84(0x1c);
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

