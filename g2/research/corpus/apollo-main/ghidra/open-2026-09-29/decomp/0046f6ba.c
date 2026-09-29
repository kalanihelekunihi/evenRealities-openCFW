
undefined4 FUN_0046f6ba(char param_1)

{
  undefined4 unaff_r7;
  
  if (param_1 == '\x01') {
    *(undefined1 *)(DAT_00470218 + 5) = 8;
  }
  else {
    *(undefined1 *)(DAT_00470218 + 5) = 0;
  }
  FUN_004c0f78(*DAT_00470014,0x10,DAT_00470218);
  return unaff_r7;
}

