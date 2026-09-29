
int FUN_004cdf74(int param_1,int param_2)

{
  int iVar1;
  undefined4 *puVar2;
  ushort uVar3;
  undefined4 local_28;
  undefined4 uStack_24;
  uint local_20;
  undefined1 *local_1c;
  uint local_18;
  undefined4 local_14;
  
  puVar2 = &local_28;
  if (*(int *)(param_2 + 0x30) << 0xc < 0) {
    iVar1 = 0;
  }
  else {
    iVar1 = FUN_004cde54(param_1,param_2);
    if (iVar1 == 0) {
      if ((*(int *)(param_2 + 0x30) << 0xf < 0) && (iVar1 = FUN_004cadd0(param_2 + 8), iVar1 == 0))
      {
        if ((-1 < *(int *)(param_2 + 0x30) << 0xb) &&
           (iVar1 = FUN_004cabbc(param_1,param_1 + 0x10,param_1,0), iVar1 != 0)) {
          return iVar1;
        }
        if (*(int *)(param_2 + 0x30) << 0xb < 0) {
          uVar3 = 0x201;
          puVar2 = *(undefined4 **)(param_2 + 0x4c);
          local_20 = *(uint *)(param_2 + 0x2c);
        }
        else {
          uVar3 = 0x202;
          local_28 = *(undefined4 *)(param_2 + 0x28);
          uStack_24 = *(undefined4 *)(param_2 + 0x2c);
          FUN_004cb000(&local_28);
          local_20 = 8;
        }
        local_20 = local_20 | (uint)*(ushort *)(param_2 + 4) << 10 | (uint)uVar3 << 0x14;
        local_18 = *(uint *)(*(int *)(param_2 + 0x50) + 8) | (uint)*(ushort *)(param_2 + 4) << 10 |
                   0x10200000;
        local_14 = *(undefined4 *)(*(int *)(param_2 + 0x50) + 4);
        local_1c = (undefined1 *)puVar2;
        iVar1 = FUN_004cd388(param_1,param_2 + 8,&local_20,2);
        if (iVar1 != 0) {
          *(uint *)(param_2 + 0x30) = *(uint *)(param_2 + 0x30) | 0x80000;
          return iVar1;
        }
        *(uint *)(param_2 + 0x30) = *(uint *)(param_2 + 0x30) & 0xfffeffff;
      }
      iVar1 = 0;
    }
    else {
      *(uint *)(param_2 + 0x30) = *(uint *)(param_2 + 0x30) | 0x80000;
    }
  }
  return iVar1;
}

