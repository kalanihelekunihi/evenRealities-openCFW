
int FUN_004cf4da(undefined4 param_1,undefined4 *param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 local_30;
  undefined4 local_2c;
  undefined4 local_28;
  undefined1 auStack_24 [16];
  undefined4 uStack_14;
  
  *(undefined4 *)(param_3 + 0x18) = 0;
  *(undefined4 *)(param_3 + 0x1c) = 1;
  uStack_14 = param_4;
  FUN_00439c04(auStack_24,DAT_004cfca4,0x10);
  while( true ) {
    iVar1 = FUN_004cadd0(param_3 + 0x18);
    if (iVar1 != 0) {
      return -2;
    }
    iVar1 = FUN_004cef18(param_3,auStack_24);
    if (iVar1 < 0) break;
    local_2c = *param_2;
    local_28 = param_2[1];
    local_30 = param_1;
    iVar1 = FUN_004cb968(param_1,param_3,param_3 + 0x18,DAT_004cfcac,DAT_004cfc98,0,DAT_004cfca8,
                         &local_30);
    if ((iVar1 != 0) && (iVar1 != -2)) {
      return iVar1;
    }
  }
  return iVar1;
}

