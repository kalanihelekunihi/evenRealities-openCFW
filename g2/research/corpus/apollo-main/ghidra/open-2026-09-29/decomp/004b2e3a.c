
undefined4 dmDevHciEvtVendorSpecCmdCmpl(int param_1)

{
  undefined4 unaff_r7;
  
  *(undefined1 *)(param_1 + 2) = 0x7b;
  (**(code **)(DAT_004b306c + 8))();
  return unaff_r7;
}

