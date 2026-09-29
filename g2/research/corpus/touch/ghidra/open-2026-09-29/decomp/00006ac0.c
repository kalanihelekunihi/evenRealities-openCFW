
int event_dispatcher(uint param_1,int param_2)

{
  uint uVar1;
  int iVar2;
  
  uVar1 = (uint)*(byte *)(*(int *)(param_2 + 8) + 0x55);
  if (uVar1 == param_1) {
    iVar2 = 0;
  }
  else {
    if (uVar1 < 3) {
      iVar2 = 0;
    }
    else if ((uVar1 - 5 & 0xff) < 3) {
      iVar2 = 0;
    }
    else {
      iVar2 = 1;
    }
    *(undefined1 *)(*(int *)(param_2 + 8) + 0x73) = 0;
    if (iVar2 == 0) {
      if (param_1 < 8) {
                    /* WARNING: Could not recover jumptable at 0x00006b04. Too many branches */
                    /* WARNING: Treating indirect jump as call */
        iVar2 = (**(code **)(DAT_00006bcc + param_1 * 4))();
        return iVar2;
      }
      iVar2 = 1;
    }
  }
  return iVar2;
}

