
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 AttRegister(undefined4 param_1)

{
  ushort uVar1;
  undefined4 unaff_r7;
  
  *(undefined4 *)(DAT_004b51d0 + 0x58) = param_1;
  uVar1 = HciGetMaxRxAclLen();
  if ((int)(uVar1 - 4) < (int)(uint)*(ushort *)(*_DAT_004b5200 + 4)) {
    unaff_r7 = 0;
    attExecCallback(0,0x78,0,2);
  }
  return unaff_r7;
}

