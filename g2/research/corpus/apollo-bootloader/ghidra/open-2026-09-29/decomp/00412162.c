
int FUN_00412162(int param_1,undefined4 *param_2)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  
  iVar3 = 0;
  while( true ) {
    if (1 < iVar3) {
      param_2[2] = 0;
      iVar3 = FUN_00410544(param_1,0,param_1,4,*param_2,0,param_2 + 2,4);
      uVar2 = lfs_fromle32(param_2[2]);
      param_2[2] = uVar2;
      if ((iVar3 == 0) || (iVar3 == -0x54)) {
        if (0 < *(int *)(*(int *)(param_1 + 0x68) + 0x24)) {
          uVar2 = lfs_alignup(param_2[2],*(int *)(*(int *)(param_1 + 0x68) + 0x24) + 1U | 1);
          param_2[2] = uVar2;
        }
        param_2[3] = 4;
        param_2[4] = 0xffffffff;
        *(undefined2 *)(param_2 + 5) = 0;
        param_2[6] = 0xffffffff;
        param_2[7] = 0xffffffff;
        *(undefined1 *)((int)param_2 + 0x16) = 0;
        *(undefined1 *)((int)param_2 + 0x17) = 0;
        iVar3 = 0;
      }
      return iVar3;
    }
    iVar1 = FUN_00410e8e(param_1,param_2 + (iVar3 + 1) % 2);
    if (iVar1 != 0) break;
    iVar3 = iVar3 + 1;
  }
  return iVar1;
}

