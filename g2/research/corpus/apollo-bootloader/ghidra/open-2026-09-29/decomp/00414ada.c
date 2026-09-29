
int FUN_00414ada(undefined4 param_1,undefined4 param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uStack_20;
  undefined4 uStack_1c;
  int iStack_18;
  undefined4 uStack_14;
  
  *(undefined4 *)(param_3 + 0x18) = 0;
  *(undefined4 *)(param_3 + 0x1c) = 1;
  uStack_20 = param_1;
  uStack_1c = param_2;
  iStack_18 = param_3;
  uStack_14 = param_4;
  FUN_004156ac(&uStack_20,DAT_004152c4,0x10);
  do {
    iVar1 = FUN_00410ad8(param_3 + 0x18);
    if (iVar1 != 0) {
      return -2;
    }
    iVar1 = FUN_004145fc(param_3,&uStack_20);
    if (iVar1 < 0) {
      return -0x54;
    }
    iVar1 = FUN_00410af2(param_3 + 0x18,param_2);
    if (iVar1 == 0) {
      return 0;
    }
    iVar1 = FUN_00411be4(param_1,param_3,param_3 + 0x18);
  } while (iVar1 == 0);
  return iVar1;
}

