
undefined4 event_bit_set_42e444(uint param_1)

{
  undefined4 unaff_r7;
  
  bl_runtime_flags_set(*(undefined4 *)(DAT_0042e46c + 0x1c),1 << (param_1 & 0xff));
  return unaff_r7;
}

