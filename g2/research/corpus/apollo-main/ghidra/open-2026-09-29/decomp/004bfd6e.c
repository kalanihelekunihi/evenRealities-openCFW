
undefined8 FUN_004bfd6e(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  byte bVar3;
  undefined4 uVar4;
  int iVar5;
  undefined4 local_18;
  
  iVar2 = DAT_004c0990;
  iVar1 = DAT_004c098c;
  *(undefined4 *)(DAT_004c0990 + *(int *)(param_1 + 4) * 0x1000 + 0x2b4) = 0x800000;
  iVar5 = iVar1;
  while (*(int *)(iVar2 + *(int *)(param_1 + 4) * 0x1000 + 0x2a0) << 0x1f < 0) {
    if (*(int *)(iVar2 + *(int *)(param_1 + 4) * 0x1000 + 0x2ac) << 0x1c < 0) {
      bVar3 = (byte)(*(uint *)(iVar2 + *(int *)(param_1 + 4) * 0x1000 + 0x2b8) >> 7) & 1;
    }
    else {
      bVar3 = 0;
    }
    if (bVar3 != 0) break;
    if (iVar5 == 0) {
      uVar4 = 4;
      local_18 = param_4;
      goto LAB_004bfdee;
    }
    FUN_004807a0(1);
    iVar5 = iVar5 + -1;
  }
  local_18 = 1;
  uVar4 = FUN_00480826(iVar1,iVar2 + *(int *)(param_1 + 4) * 0x1000 + 0x104,1,0);
LAB_004bfdee:
  return CONCAT44(local_18,uVar4);
}

