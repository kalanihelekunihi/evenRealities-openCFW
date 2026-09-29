
undefined4 gx8002_kws_initialize(undefined4 param_1,uint param_2)

{
  if (param_2 < 2) {
    gx8002_kws_flash_load();
  }
  gx8002_snpu_initialize();
  *DAT_10206da8 = param_1;
  return 0;
}

