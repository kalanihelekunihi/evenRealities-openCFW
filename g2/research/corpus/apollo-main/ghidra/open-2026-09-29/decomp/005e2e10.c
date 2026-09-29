
void smpScActCalcSharedSecret(int param_1,int param_2)

{
  int iVar1;
  undefined1 auStack_70 [32];
  undefined1 auStack_50 [32];
  undefined1 auStack_30 [32];
  
  FUN_00439be4(auStack_30,*(undefined4 *)(*(int *)(param_1 + 0x48) + 0x10),0x20);
  FUN_00439be4(auStack_70,*(undefined4 *)(*(int *)(param_1 + 0x48) + 8),0x20);
  FUN_00439be4(auStack_50,*(int *)(*(int *)(param_1 + 0x48) + 8) + 0x20,0x20);
  iVar1 = FUN_00536774(auStack_70,*(undefined1 *)(DAT_005e30f0 + 0xec),
                       *(undefined1 *)(param_1 + 0x3d),0x19);
  if (iVar1 == 0) {
    *(undefined1 *)(param_2 + 3) = 0xe0;
    *(undefined1 *)(param_2 + 2) = 3;
    smpSmExecute(param_1,param_2);
  }
  return;
}

