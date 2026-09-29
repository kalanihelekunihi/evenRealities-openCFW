
undefined4
at_core_dispatch_command(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  byte *pbVar1;
  uint uVar2;
  uint uVar3;
  int iVar4;
  uint uVar5;
  
  pbVar1 = DAT_00541580;
  if ((((*DAT_00541580 & 3) == 3) && (param_1 != 0)) &&
     (uVar2 = FUN_0044a43c(param_1), uVar2 < 0x100)) {
    for (uVar5 = 0; uVar5 < *(uint *)(pbVar1 + 0xc); uVar5 = uVar5 + 1) {
      uVar3 = FUN_0044a43c(*(undefined4 *)(*(int *)(pbVar1 + 8) + uVar5 * 0x10 + 4));
      if ((uVar3 == uVar2) &&
         (iVar4 = FUN_004751c8(*(undefined4 *)(*(int *)(pbVar1 + 8) + uVar5 * 0x10 + 4),param_1,
                               uVar2), iVar4 == 0)) {
        if ((*(int *)pbVar1 << 0x1d < 0) &&
           (-1 < (int)((uint)*(byte *)(*(int *)(pbVar1 + 8) + uVar5 * 0x10) << 0x1f))) {
          return param_4;
        }
        if (*(int *)(*(int *)(pbVar1 + 8) + uVar5 * 0x10 + 8) != 0) {
          if ((*(byte *)(*(int *)(pbVar1 + 8) + uVar5 * 0x10) & 3) >> 1 == 0) {
            (**(code **)(*(int *)(pbVar1 + 8) + uVar5 * 0x10 + 8))(param_2,param_3);
          }
          else {
            FUN_0057de0a(*(undefined4 *)(*(int *)(pbVar1 + 8) + uVar5 * 0x10 + 8),param_2,param_3);
          }
        }
      }
    }
  }
  return param_4;
}

