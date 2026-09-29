
undefined4 semantic_whitelist_get_cached_crc32(undefined4 *param_1)

{
  undefined4 uVar1;
  
  if (param_1 == (undefined4 *)0x0) {
    uVar1 = 0;
  }
  else if (*DAT_004d6b00 == '\0') {
    uVar1 = 0;
  }
  else {
    *param_1 = *DAT_004d6b3c;
    uVar1 = 1;
  }
  return uVar1;
}

