
int FUN_004caafa(int param_1,uint *param_2,undefined4 param_3,char param_4)

{
  undefined4 uVar1;
  int iVar2;
  
  if ((*param_2 != 0xffffffff) && (*param_2 != 0xfffffffe)) {
    if (*(uint *)(param_1 + 0x6c) <= *param_2) {
      FUN_004d09b4(DAT_004cb5a0,DAT_004cb594,0xb3);
    }
    uVar1 = lfs_alignup(param_2[2],*(undefined4 *)(*(int *)(param_1 + 0x68) + 0x18));
    iVar2 = (**(code **)(*(int *)(param_1 + 0x68) + 8))
                      (*(undefined4 *)(param_1 + 0x68),*param_2,param_2[1],param_2[3],uVar1);
    if (0 < iVar2) {
      FUN_004d09b4(DAT_004cb59c,DAT_004cb594,0xb7);
    }
    if (iVar2 != 0) {
      return iVar2;
    }
    if (param_4 != '\0') {
      FUN_004ca81a(param_1,param_3);
      iVar2 = FUN_004caa04(param_1,0,param_3,uVar1,*param_2,param_2[1],param_2[3],uVar1);
      if (iVar2 < 0) {
        return iVar2;
      }
      if (iVar2 != 0) {
        return -0x54;
      }
    }
    FUN_004ca822(param_1,param_2);
  }
  return 0;
}

