
undefined8 FUN_005300e2(int param_1,int param_2,int param_3)

{
  bool bVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  byte bVar5;
  uint uVar6;
  
  uVar6 = *(int *)(param_1 + 0x10) * param_3;
  uVar2 = FUN_00473940(0);
  if (*(uint *)(param_1 + 8) < uVar6) {
    bVar5 = 0;
  }
  else {
    for (uVar3 = 0; uVar3 < uVar6; uVar3 = uVar3 + 1) {
      if (param_2 != 0) {
        *(undefined1 *)(param_2 + uVar3) =
             *(undefined1 *)(*(int *)(param_1 + 0x14) + *(int *)(param_1 + 4));
      }
      uVar4 = *(int *)(param_1 + 4) + 1;
      *(uint *)(param_1 + 4) = uVar4 - *(uint *)(param_1 + 0xc) * (uVar4 / *(uint *)(param_1 + 0xc))
      ;
    }
    *(uint *)(param_1 + 8) = *(int *)(param_1 + 8) - uVar6;
    bVar5 = 1;
  }
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    enableIRQinterrupts((uVar2 & 1) == 1);
  }
  return CONCAT44(uVar2,(uint)bVar5);
}

