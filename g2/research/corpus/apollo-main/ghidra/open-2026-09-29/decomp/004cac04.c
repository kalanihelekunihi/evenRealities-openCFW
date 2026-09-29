
undefined8
FUN_004cac04(int param_1,uint *param_2,undefined4 param_3,undefined4 param_4,uint param_5,
            uint param_6,int param_7,int param_8)

{
  int iVar1;
  uint uVar2;
  uint *puVar3;
  uint uVar4;
  
  puVar3 = param_2;
  if ((param_5 != 0xfffffffe) && (*(uint *)(param_1 + 0x6c) <= param_5)) {
    FUN_004d09b4(DAT_004cb5a4,DAT_004cb594,0xe8,param_4,param_2,param_3,param_4);
  }
  uVar4 = CONCAT31((int3)((uint)puVar3 >> 8),(char)param_4);
  if (*(uint *)(*(int *)(param_1 + 0x68) + 0x1c) < param_8 + param_6) {
    FUN_004d09b4(DAT_004cb5a8,DAT_004cb594,0xe9);
  }
  do {
    while( true ) {
      if (param_8 == 0) {
        iVar1 = 0;
        goto LAB_004cad2a;
      }
      if (((param_5 == *param_2) && (param_2[1] <= param_6)) &&
         (param_6 < *(int *)(*(int *)(param_1 + 0x68) + 0x28) + param_2[1])) break;
      if (*param_2 != 0xffffffff) {
        FUN_004d09b4(DAT_004cb95c,DAT_004cb594,0x106);
      }
      *param_2 = param_5;
      uVar2 = lfs_aligndown(param_6,*(undefined4 *)(*(int *)(param_1 + 0x68) + 0x18));
      param_2[1] = uVar2;
      param_2[2] = 0;
    }
    iVar1 = lfs_min(param_8,param_2[1] + (*(int *)(*(int *)(param_1 + 0x68) + 0x28) - param_6));
    FUN_00439be4(param_2[3] + (param_6 - param_2[1]),param_7,iVar1);
    param_7 = param_7 + iVar1;
    param_6 = iVar1 + param_6;
    param_8 = param_8 - iVar1;
    uVar2 = lfs_max(param_2[2],param_6 - param_2[1]);
    param_2[2] = uVar2;
  } while ((param_2[2] != *(uint *)(*(int *)(param_1 + 0x68) + 0x28)) ||
          (iVar1 = FUN_004caafa(param_1,param_2,param_3,uVar4 & 0xff), iVar1 == 0));
LAB_004cad2a:
  return CONCAT44(uVar4,iVar1);
}

