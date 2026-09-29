
undefined8
AppSetAdvType(undefined1 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  undefined4 local_10;
  undefined4 local_c;
  
  iVar2 = appSlaveAdvMode();
  iVar1 = DAT_004b2dc8;
  local_10 = param_3;
  local_c = param_4;
  if (iVar2 != 0) {
    *(undefined1 *)(DAT_004b2dc8 + 0x57) = 0;
    local_c = 1;
    local_10 = 0;
    FUN_004b4510(0,param_1,*(undefined2 *)(*DAT_004b2dcc + (uint)*(byte *)(iVar1 + 0x57) * 2 + 6),
                 *(undefined2 *)(*DAT_004b2dcc + (uint)*(byte *)(iVar1 + 0x57) * 2));
  }
  return CONCAT44(local_c,local_10);
}

