
undefined8 FUN_004bfe60(int param_1,int param_2)

{
  bool bVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  
  iVar4 = 0;
  uVar2 = FUN_00473940();
  iVar3 = *(int *)(param_1 + 0x840);
  *(int *)(param_1 + 0x840) = param_2 + *(int *)(param_1 + 0x840);
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    enableIRQinterrupts((uVar2 & 1) == 1);
  }
  if ((iVar3 == 0) && (iVar4 = FUN_004bfd6e(param_1), iVar4 == 0)) {
    *(undefined4 *)(param_1 + 0x24) = 0;
    iVar4 = DAT_004c0990;
    *(undefined4 *)(DAT_004c0990 + *(int *)(param_1 + 4) * 0x1000 + 0x208) = 0x40;
    *(uint *)(iVar4 + *(int *)(param_1 + 4) * 0x1000 + 0x200) =
         *(uint *)(iVar4 + *(int *)(param_1 + 4) * 0x1000 + 0x200) | 0x40;
    *(undefined1 *)(param_1 + 0x83c) = 1;
    iVar4 = FUN_004bfdf4(param_1);
  }
  return CONCAT44(uVar2,iVar4);
}

