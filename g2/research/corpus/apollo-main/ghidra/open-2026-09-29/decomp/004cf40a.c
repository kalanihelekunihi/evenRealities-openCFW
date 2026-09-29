
int FUN_004cf40a(undefined4 param_1,undefined4 param_2,int param_3,undefined4 param_4)

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
  FUN_00439c04(&uStack_20,DAT_004cfca0,0x10);
  do {
    iVar1 = FUN_004cadd0(param_3 + 0x18);
    if (iVar1 != 0) {
      return -2;
    }
    iVar1 = FUN_004cef18(param_3,&uStack_20);
    if (iVar1 < 0) {
      return -0x54;
    }
    iVar1 = FUN_004cadea(param_3 + 0x18,param_2);
    if (iVar1 == 0) {
      return 0;
    }
    iVar1 = FUN_004cbedc(param_1,param_3,param_3 + 0x18);
  } while (iVar1 == 0);
  return iVar1;
}

