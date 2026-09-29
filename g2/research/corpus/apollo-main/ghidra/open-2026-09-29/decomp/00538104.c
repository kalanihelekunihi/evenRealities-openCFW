
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 SmprScInit(void)

{
  undefined4 unaff_r7;
  
  *(undefined4 *)(_DAT_0053823c + 0xe4) = _DAT_00538238;
  SmpScInit();
  return unaff_r7;
}

