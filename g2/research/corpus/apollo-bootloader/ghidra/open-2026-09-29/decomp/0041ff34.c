
undefined4 FUN_0041ff34(char param_1)

{
  undefined4 unaff_r7;
  
  if (param_1 == '\x01') {
    *(undefined1 *)(DAT_00420a04 + 5) = 8;
  }
  else {
    *(undefined1 *)(DAT_00420a04 + 5) = 0;
  }
  am_hal_mspi_control(*DAT_00420874,0x10,DAT_00420a04);
  return unaff_r7;
}

