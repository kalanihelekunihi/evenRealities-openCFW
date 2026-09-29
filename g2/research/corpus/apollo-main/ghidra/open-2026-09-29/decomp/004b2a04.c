
undefined8
appSlaveLegAdvStart(undefined4 param_1,undefined4 *param_2,undefined4 param_3,undefined2 param_4)

{
  int iVar1;
  int *piVar2;
  char cVar3;
  undefined4 *local_18;
  undefined4 local_14;
  undefined4 local_10;
  
  piVar2 = DAT_004b2dcc;
  iVar1 = DAT_004b2dc8;
  local_10._2_2_ = *(ushort *)(*DAT_004b2dcc + (uint)*(byte *)(DAT_004b2dc8 + 0x57) * 2 + 6);
  local_18 = param_2;
  local_14 = param_3;
  if (local_10._2_2_ == 0) {
    *(undefined1 *)(DAT_004b2dc8 + 0x57) = 3;
  }
  else {
    local_10._0_2_ = param_4;
    cVar3 = FUN_004bac4e(0);
    if (cVar3 == '\0') {
      local_10 = (uint)local_10._2_2_ << 0x10;
      local_14 = 1;
      local_18 = &local_10;
      FUN_004b42f0(1,(int)&local_10 + 1,(int)&local_10 + 2,
                   *piVar2 + (uint)*(byte *)(iVar1 + 0x57) * 2);
    }
    else if (*DAT_004b2dd0 == '\0') {
      *DAT_004b2dd0 = '\x01';
      iVar1 = DAT_004b2dd4;
      *(undefined1 *)(DAT_004b2dd4 + 10) = 0x22;
      *(undefined2 *)(iVar1 + 8) = 0;
      *(undefined1 *)(iVar1 + 0xc) = *DAT_004b2dd8;
      WsfTimerStartMs(iVar1,200);
    }
  }
  return CONCAT44(local_14,local_18);
}

