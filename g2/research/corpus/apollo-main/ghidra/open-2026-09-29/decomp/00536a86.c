
undefined4 dmConnSmActOpen(undefined4 param_1,int param_2)

{
  undefined4 unaff_r7;
  
  dmConnOpen(*(undefined1 *)(param_2 + 4),*(undefined1 *)(param_2 + 0x11),param_2 + 0xb);
  return unaff_r7;
}

