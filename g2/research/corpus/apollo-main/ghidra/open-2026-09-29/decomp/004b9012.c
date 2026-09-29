
undefined8 _tplReponse(char param_1,undefined4 param_2,undefined4 param_3,byte param_4)

{
  char cVar1;
  int iVar2;
  int iVar3;
  
  iVar3 = DAT_004b99ec;
  *(char *)(DAT_004b99ec + 2) = (char)param_2;
  *(char *)(iVar3 + 6) = (char)param_3;
  *(byte *)(iVar3 + 7) = *(byte *)(iVar3 + 7) & 0xe1 | (param_4 & 0xf) << 1;
  cVar1 = '\0';
  if (param_1 == '\0') {
    if (*(int *)(DAT_004b90e8 + 0x10) != 0) {
      cVar1 = (**(code **)(DAT_004b90e8 + 0x10))(iVar3,8);
    }
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_2 = 0x16c;
      param_3 = DAT_004b99f0;
      FUN_0043d574(1,PTR_s_prot_tran_004b9100,DAT_004b90fc,DAT_004b99f4,0x16c,DAT_004b99f0,
                   *(byte *)(iVar3 + 1) >> 4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_004b99f8,DAT_004b99f8,*(byte *)(iVar3 + 1) >> 4);
    }
  }
  if (cVar1 != '\0') {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_2 = 0x171;
      param_3 = DAT_004b99fc;
      FUN_0043d574(1,PTR_s_prot_tran_004b9100,DAT_004b90fc,DAT_004b99f4,0x171,DAT_004b99fc,cVar1);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_004b9a00,DAT_004b9a00,cVar1);
    }
  }
  return CONCAT44(param_3,param_2);
}

