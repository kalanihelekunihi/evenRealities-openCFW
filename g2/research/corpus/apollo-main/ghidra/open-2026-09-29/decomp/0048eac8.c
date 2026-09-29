
undefined8 FUN_0048eac8(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  bool bVar1;
  char *pcVar2;
  uint uVar3;
  int iVar4;
  undefined4 local_18;
  undefined4 local_14;
  undefined4 uStack_10;
  
  local_18 = param_2;
  local_14 = param_3;
  uStack_10 = param_4;
  uVar3 = FUN_0047dce4();
  pcVar2 = DAT_0048ed88;
  if (*DAT_0048ed88 == '\0') {
    iVar4 = FUN_0048e900();
    if (iVar4 == 0) {
      FUN_0048e99c();
    }
    else if (*(int *)(DAT_0048ed78 + 0x10) == *(int *)(DAT_0048ed78 + 8)) {
      *DAT_0048ed8c = 0;
    }
    else {
      *DAT_0048ed8c = 1;
    }
    *pcVar2 = '\x01';
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      enableIRQinterrupts((uVar3 & 1) == 1);
    }
    local_18 = FUN_0047dcec(uVar3);
    local_14 = FUN_0047dd08();
    FUN_0048ea66(DAT_0048ed90,2,&local_18);
  }
  else {
    bVar1 = (bool)isCurrentModePrivileged();
    if (bVar1) {
      enableIRQinterrupts((uVar3 & 1) == 1);
    }
  }
  return CONCAT44(local_14,local_18);
}

