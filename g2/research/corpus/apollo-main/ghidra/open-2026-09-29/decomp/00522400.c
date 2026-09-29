
void FUN_00522400(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
                 undefined4 param_5,undefined4 param_6)

{
  undefined4 *puVar1;
  uint *puVar2;
  undefined4 uVar3;
  uint uVar4;
  bool bVar5;
  
  puVar1 = DAT_00522564;
  uVar3 = FUN_005155d6();
  *puVar1 = uVar3;
  FUN_00522920(&DAT_005225d4,1,0x16);
  FUN_00522920(&DAT_005225dc,1,0x17);
  FUN_00514846(0x388,1);
  FUN_00522920(&DAT_005225e4,1,0x15);
  FUN_00522920(&DAT_005225ec,1,0x14);
  FUN_00522920(&LAB_005225f4,1,0x13);
  puVar2 = DAT_00522568;
  FUN_005155e4(param_1,param_2,param_3,param_4,param_5,param_6);
  uVar4 = FUN_0051562e();
  *puVar2 = uVar4;
  uVar3 = FUN_005155d6();
  *puVar1 = uVar3;
  FUN_00515304();
  uVar4 = *puVar2;
  bVar5 = (*(byte *)(uVar4 + 0x10) & 3) == 0;
  if (bVar5) {
    uVar4 = (uint)*(byte *)(uVar4 + 0x14);
  }
  if (!bVar5 || (uVar4 & 3) != 0) {
    FUN_0051565c(0x2000000);
  }
  FUN_005675b4();
  FUN_005675a8(*(undefined4 *)(*puVar2 + 0x10),*(undefined4 *)(*puVar2 + 0x14));
  return;
}

