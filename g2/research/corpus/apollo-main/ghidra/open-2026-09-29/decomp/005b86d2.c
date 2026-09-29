
undefined8 FUN_005b86d2(int param_1,undefined4 *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  int iStack_20;
  undefined4 *puStack_1c;
  undefined4 uStack_18;
  undefined4 uStack_14;
  
  iStack_20 = param_1;
  puStack_1c = param_2;
  if (((param_1 != 0) && (*(int *)(param_1 + 4) != 0)) &&
     (uStack_18 = param_3, uStack_14 = param_4, iVar1 = FUN_0043e2ea(*(undefined4 *)(param_1 + 4)),
     iVar1 != 0)) {
    uVar2 = *param_2;
    FUN_0043c0e4(&iStack_20,0x10,0);
    FUN_0044b728(&iStack_20,0x10,&DAT_005b8988,uVar2);
    FUN_0049942e(*(undefined4 *)(param_1 + 4),&iStack_20);
    FUN_005b7a4c(param_1);
  }
  return CONCAT44(puStack_1c,iStack_20);
}

