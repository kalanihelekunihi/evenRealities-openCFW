
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void SmpiInit(void)

{
  int iVar1;
  
  iVar1 = _DAT_00537f04;
  *(undefined **)(_DAT_00537f04 + 0xe8) = PTR_PTR_00537f08;
  *(undefined **)(iVar1 + 0xf0) = PTR_smpProcPairing_1_00537f0c;
  *(undefined **)(iVar1 + 0xf4) = PTR_smpAuthReq_1_00537f10;
  return;
}

