
undefined8 FUN_0058956e(undefined4 param_1,int param_2,int param_3)

{
  int *piVar1;
  uint uVar2;
  int iVar3;
  undefined4 uVar4;
  int iVar5;
  char cVar6;
  int local_18;
  int local_14;
  
  iVar3 = DAT_00589934;
  local_18 = param_2;
  local_14 = param_3;
  if ((*(char *)(DAT_00589934 + 0xc2) != '\0') && (*(char *)(DAT_00589934 + 0xc3) == '\0')) {
    piVar1 = (int *)(DAT_00589934 + (uint)*(byte *)(DAT_00589934 + 0xc0) * 0xc);
    local_18 = *piVar1;
    local_14 = piVar1[1];
    iVar5 = piVar1[2];
    uVar2 = *(byte *)(DAT_00589934 + 0xc0) + 1;
    *(char *)(DAT_00589934 + 0xc0) = (char)uVar2 + (char)(uVar2 / 0x10) * -0x10;
    *(char *)(iVar3 + 0xc2) = *(char *)(iVar3 + 0xc2) + -1;
    if (iVar5 == 0) {
      iVar5 = 200;
    }
    cVar6 = local_18 != 0;
    if (local_14 != 0) {
      cVar6 = cVar6 + '\x01';
    }
    if (cVar6 == '\0') {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        local_14 = DAT_0058994c;
        local_18 = 0xa4;
        FUN_0043d574(2,DAT_00589944,DAT_00589940,DAT_00589950);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x8000000,DAT_00589954,DAT_00589954);
      }
      FUN_0058956e();
    }
    else {
      *(char *)(iVar3 + 0xc4) = cVar6;
      *(undefined1 *)(iVar3 + 0xc3) = 1;
      uVar4 = osKernelGetTickCount();
      *(undefined4 *)(iVar3 + 200) = uVar4;
      *(int *)(iVar3 + 0xcc) = iVar5 + 0x96;
      if (local_18 != 0) {
        FUN_0058c6c4(local_18,iVar5,DAT_00589958);
      }
      if (local_14 != 0) {
        FUN_0058c622(local_14,iVar5,DAT_00589958);
        FUN_005894d6(local_14);
      }
    }
  }
  return CONCAT44(local_14,local_18);
}

