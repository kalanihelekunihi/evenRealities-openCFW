
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void device_mgr_fn_004c67dc(void)

{
  if (*_DAT_004c6c80 != '\0') {
    *_DAT_004c6c7c = *_DAT_004c6c7c + 1;
    *_DAT_004c6c88 = *_DAT_004c6c88 + 1;
  }
  if (*_DAT_004c6c90 != '\0') {
    *_DAT_004c6c8c = *_DAT_004c6c8c + 1;
  }
  return;
}

