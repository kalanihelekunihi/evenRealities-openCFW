
undefined4 dmConnSmActAccept(undefined4 param_1,int param_2)

{
  undefined4 unaff_r7;
  
  dmAdvStartDirected(*(undefined1 *)(param_2 + 6),*(undefined2 *)(param_2 + 8),
                     *(undefined1 *)(param_2 + 0x11),param_2 + 0xb);
  return unaff_r7;
}

