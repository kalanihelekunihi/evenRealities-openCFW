
undefined8 FUN_004bfbbc(uint param_1,int param_2,uint param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint local_28;
  undefined4 uStack_24;
  
  local_28 = param_3;
  if (param_1 < 4) {
    uVar4 = (param_3 >> 2) * -4 + param_3;
    uStack_24 = param_4;
    for (uVar5 = 0; iVar1 = DAT_004c0754, uVar5 < param_3 >> 2; uVar5 = uVar5 + 1) {
      local_28 = 0;
      iVar2 = FUN_00480826(param_4,DAT_004c0754 + param_1 * 0x1000 + 0x1c,0x3f,0);
      if (iVar2 != 0) goto LAB_004bfc56;
      *(undefined4 *)(param_2 + uVar5 * 4) = *(undefined4 *)(iVar1 + param_1 * 0x1000 + 0x14);
    }
    if (uVar4 != 0) {
      local_28 = 0;
      iVar2 = FUN_00480826(param_4,DAT_004c0754 + param_1 * 0x1000 + 0x1c,0x3f,0);
      if (iVar2 != 0) goto LAB_004bfc56;
      local_28 = *(uint *)(iVar1 + param_1 * 0x1000 + 0x14);
      for (uVar3 = 0; uVar3 < uVar4; uVar3 = uVar3 + 1) {
        *(undefined1 *)(param_2 + uVar5 * 4 + uVar3) = *(undefined1 *)((int)&local_28 + uVar3);
      }
    }
    iVar2 = 0;
  }
  else {
    iVar2 = 5;
  }
LAB_004bfc56:
  return CONCAT44(local_28,iVar2);
}

