
void FUN_0048ed00(undefined1 *param_1,undefined4 param_2,undefined4 param_3)

{
  undefined4 uVar1;
  
  *param_1 = 0x54;
  param_1[1] = 0x50;
  param_1[2] = 0x46;
  param_1[3] = 0x31;
  FUN_0048ece2(param_1 + 4,3);
  FUN_0048ece2(param_1 + 6,0x20);
  uVar1 = FUN_0047dd08();
  FUN_0048ecec(param_1 + 8,uVar1);
  FUN_0048ecec(param_1 + 0xc,0x200);
  FUN_0048ecec(param_1 + 0x10,param_2);
  FUN_0048ecec(param_1 + 0x14,param_3);
  FUN_0048ecec(param_1 + 0x18,DAT_0048edac);
  uVar1 = FUN_0048ecae(param_1,0x1c);
  FUN_0048ecec(param_1 + 0x1c,uVar1);
  return;
}

