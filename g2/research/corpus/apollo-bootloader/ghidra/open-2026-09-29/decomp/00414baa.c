
int FUN_00414baa(undefined4 param_1,undefined4 *param_2,int param_3,undefined4 param_4)

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
  FUN_004156ac(auStack_24,DAT_004152c8,0x10);
  while( true ) {
    iVar1 = FUN_00410ad8(param_3 + 0x18);
    if (iVar1 != 0) {
      return -2;
    }
    iVar1 = FUN_004145fc(param_3,auStack_24);
    if (iVar1 < 0) break;
    local_2c = *param_2;
    local_28 = param_2[1];
    local_30 = param_1;
    iVar1 = FUN_00411670(param_1,param_3,param_3 + 0x18,DAT_004152d0,DAT_004152bc,0,DAT_004152cc,
                         &local_30);
    if ((iVar1 != 0) && (iVar1 != -2)) {
      return iVar1;
    }
  }
  return iVar1;
}

