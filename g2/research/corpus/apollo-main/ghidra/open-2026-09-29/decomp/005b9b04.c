
void FUN_005b9b04(int *param_1)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  undefined1 auStack_2c [20];
  
  if ((((param_1 != (int *)0x0) && (param_1[1] != 0)) &&
      (iVar1 = FUN_0043e2ea(param_1[1]), iVar1 != 0)) &&
     (iVar1 = FUN_005b8a6a((char)param_1[2]), -1 < iVar1)) {
    health_lock_storage();
    uVar3 = *(undefined4 *)(iVar1 * 0x18 + DAT_005b9ce0 + 0xc);
    uVar2 = *(undefined4 *)(DAT_005b9ce0 + iVar1 * 0x18 + 0x14);
    health_unlock_storage();
    FUN_0043c0e4(auStack_2c,0x10,0);
    FUN_005b8a9c(uVar3,(char)param_1[2],uVar2,auStack_2c,0x10);
    FUN_0049942e(param_1[1],auStack_2c);
    if ((*param_1 != 0) && (iVar1 = FUN_0043e2ea(*param_1), iVar1 == 1)) {
      FUN_0043f6d6(param_1[1],*param_1,0x14,8,0);
    }
  }
  return;
}

