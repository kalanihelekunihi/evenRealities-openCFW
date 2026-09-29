
undefined4 dmConnSmActHciUpdated(undefined4 param_1,int param_2)

{
  undefined4 unaff_r7;
  
  *(undefined1 *)(param_2 + 2) = 0x29;
  (**(code **)(DAT_004b6520 + 0x9c))();
  return unaff_r7;
}

