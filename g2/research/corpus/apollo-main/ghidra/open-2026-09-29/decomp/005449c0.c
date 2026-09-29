
undefined1 FUN_005449c0(int param_1,char *param_2)

{
  undefined1 uVar1;
  uint uVar2;
  undefined4 uVar3;
  int iVar4;
  uint uVar5;
  uint uVar6;
  undefined1 auStack_f8 [4];
  undefined1 auStack_f4 [24];
  undefined1 auStack_dc [68];
  undefined1 auStack_98 [88];
  undefined1 auStack_40 [32];
  
  uVar1 = 0;
  if (*param_2 == '\x02') {
    FUN_005448b4(param_1,0,param_2,0);
  }
  uVar2 = FUN_00544814(param_1,auStack_f4,*(undefined4 *)(param_2 + 8));
  if (uVar2 == 0xffffffff) {
    return 7;
  }
  if ((*(char *)(param_1 + 0x31) != '\0') && (*param_2 == '\x03')) {
    FUN_0043c0e4(auStack_dc,0x41,0);
    uVar3 = FUN_0044b5a0(auStack_dc,param_2 + 0x10,param_2[2]);
    iVar4 = FUN_0054447a(param_1,uVar3,auStack_98);
    if (iVar4 != 0) {
      uVar1 = 0;
      goto LAB_00544adc;
    }
  }
  iVar4 = *(int *)(param_2 + 8);
  FUN_005446b8(param_1,auStack_f4,*(undefined4 *)(param_2 + 8),0);
  FUN_005858d8(param_1,uVar2,auStack_f8,6,1,0);
  uVar5 = iVar4 - 4;
  for (uVar6 = 0; uVar6 < uVar5; uVar6 = iVar4 + uVar6) {
    if (uVar6 + 0x20 < uVar5) {
      iVar4 = 0x20;
    }
    else {
      iVar4 = uVar5 - uVar6;
    }
    FUN_00585a12(param_1,uVar6 + *(int *)(param_2 + 0x50) + 4,auStack_40,iVar4);
    uVar1 = FUN_00585a52(param_1,uVar6 + uVar2 + 4,auStack_40,iVar4,1);
  }
  FUN_005858d8(param_1,uVar2,auStack_f8,6,2,1);
  FUN_00543cec(param_1,*(int *)(param_1 + 0xc) * (uVar2 / *(uint *)(param_1 + 0xc)),
               *(int *)(param_2 + 0xc) + uVar2 + (byte)param_2[2] + 0x18);
  FUN_00543d1c(param_1,param_2 + 0x10,param_2[2],uVar2);
LAB_00544adc:
  FUN_005448b4(param_1,0,param_2,1);
  return uVar1;
}

