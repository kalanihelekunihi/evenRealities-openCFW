
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 SmpiScInit(void)

{
  undefined4 unaff_r7;
  
  *(undefined4 *)(_DAT_0053803c + 0xe8) = _DAT_00538038;
  SmpScInit();
  return unaff_r7;
}

