
undefined4 dmDevHciEvtReset(int param_1)

{
  int iVar1;
  undefined4 unaff_r7;
  
  iVar1 = DAT_004b306c;
  *(undefined1 *)(DAT_004b306c + 0x10) = 0;
  *(undefined1 *)(param_1 + 2) = 0x20;
  (**(code **)(iVar1 + 8))();
  return unaff_r7;
}

