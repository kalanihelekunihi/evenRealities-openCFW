
undefined4 dmDevHciEvtHwError(int param_1)

{
  undefined4 unaff_r7;
  
  *(undefined1 *)(param_1 + 2) = 0x79;
  (**(code **)(DAT_004b306c + 8))();
  return unaff_r7;
}

