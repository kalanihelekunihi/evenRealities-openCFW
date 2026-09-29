
void FUN_00523c88(void)

{
  int *piVar1;
  int iVar2;
  undefined4 *puVar3;
  
  piVar1 = DAT_0052404c;
  iVar2 = *DAT_0052404c;
  *(undefined4 *)(iVar2 + 0x10) = 0;
  *(undefined4 *)(iVar2 + 0x14) = 0;
  puVar3 = (undefined4 *)(piVar1[1] + piVar1[3] * 4);
  *puVar3 = DAT_00524050;
  iVar2 = piVar1[2];
  puVar3[2] = DAT_00524054;
  puVar3[1] = iVar2;
  puVar3[3] = piVar1[4];
  FUN_005140ea();
  FUN_00514046(0x148,0);
  FUN_00514046(0xec,piVar1[2] | 6);
  FUN_00514046(0xf0,piVar1[2]);
  FUN_00514046(0xf4,piVar1[4]);
  return;
}

