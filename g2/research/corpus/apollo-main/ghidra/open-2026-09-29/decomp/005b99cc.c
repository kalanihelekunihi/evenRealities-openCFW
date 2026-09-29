
void FUN_005b99cc(int *param_1,undefined4 *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined1 auStack_24 [16];
  undefined4 uStack_14;
  
  if (((param_1 != (int *)0x0) && (param_1[1] != 0)) &&
     (uStack_14 = param_4, iVar1 = FUN_0043e2ea(param_1[1]), iVar1 != 0)) {
    uVar2 = *param_2;
    FUN_0043c0e4(auStack_24,0x10,0);
    FUN_004b4728(auStack_24,&DAT_005b9c5c,uVar2);
    FUN_0049942e(param_1[1],auStack_24);
    if ((*param_1 != 0) && (iVar1 = FUN_0043e2ea(*param_1), iVar1 == 1)) {
      FUN_0043f6d6(param_1[1],*param_1,0x14,8,0);
    }
  }
  return;
}

