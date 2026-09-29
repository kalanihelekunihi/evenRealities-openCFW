
undefined8 FUN_00413e58(int param_1,int param_2,uint param_3,int param_4)

{
  int iVar1;
  uint uVar2;
  uint local_20;
  int iStack_1c;
  
  local_20 = param_3;
  iStack_1c = param_4;
  if (-1 < (int)((uint)*(byte *)(param_2 + 0x30) << 0x1e)) {
    FUN_00415734(DAT_00413ff4,DAT_00413f04,0xe4b);
  }
  if ((-1 < *(int *)(param_2 + 0x30) << 0xd) || (iVar1 = FUN_004139a4(param_1,param_2), iVar1 == 0))
  {
    if ((*(int *)(param_2 + 0x30) << 0x14 < 0) &&
       (*(uint *)(param_2 + 0x34) < *(uint *)(param_2 + 0x2c))) {
      *(undefined4 *)(param_2 + 0x34) = *(undefined4 *)(param_2 + 0x2c);
    }
    if (*(uint *)(param_1 + 0x74) < (uint)(param_4 + *(int *)(param_2 + 0x34))) {
      iVar1 = -0x1b;
    }
    else if ((*(int *)(param_2 + 0x30) << 0xe < 0) ||
            (*(uint *)(param_2 + 0x34) <= *(uint *)(param_2 + 0x2c))) {
LAB_00413ee6:
      iVar1 = FUN_00413cf0(param_1,param_2,param_3,param_4);
      if (-1 < iVar1) {
        *(uint *)(param_2 + 0x30) = *(uint *)(param_2 + 0x30) & 0xfff7ffff;
      }
    }
    else {
      uVar2 = *(uint *)(param_2 + 0x34);
      *(undefined4 *)(param_2 + 0x34) = *(undefined4 *)(param_2 + 0x2c);
      do {
        if (uVar2 <= *(uint *)(param_2 + 0x34)) goto LAB_00413ee6;
        local_20 = local_20 & 0xffffff00;
        iVar1 = FUN_00413cf0(param_1,param_2,&local_20,1);
      } while (-1 < iVar1);
    }
  }
  return CONCAT44(local_20,iVar1);
}

