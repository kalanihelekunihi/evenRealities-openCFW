
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void SmprInit(void)

{
  int iVar1;
  
  iVar1 = _DAT_005380f4;
  *(undefined **)(_DAT_005380f4 + 0xe4) = PTR_PTR_005380f8;
  *(undefined **)(iVar1 + 0xf0) = PTR_smpProcPairing_1_005380fc;
  *(undefined **)(iVar1 + 0xf4) = PTR_smpAuthReq_1_00538100;
  return;
}

