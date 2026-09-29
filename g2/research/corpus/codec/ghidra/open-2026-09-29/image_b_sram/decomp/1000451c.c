
undefined4 FUN_1000451c(uint param_1,undefined4 param_2)

{
  uint uVar1;
  undefined4 uVar2;
  uint uVar3;
  int iVar4;
  
  if (1 < param_1) {
    return 0xffffffff;
  }
  gx8002_platform_gate((param_1 != 0) + '\x11',1);
  uVar1 = gx8002_clock_frequency(0x10);
  uVar3 = uVar1 % 1000000;
  if (100 < uVar3) {
    if (100 < (int)(1000000 - uVar3)) goto LAB_10004552;
    uVar1 = uVar1 + 1000000;
  }
  uVar1 = uVar1 - uVar3;
LAB_10004552:
  iVar4 = param_1 * 0x80 + DAT_10004580;
  *(uint *)(iVar4 + 0xc) = uVar1;
  *(undefined4 *)(iVar4 + 0x10) = param_2;
  uVar2 = FUN_100043a4(iVar4);
  return uVar2;
}

