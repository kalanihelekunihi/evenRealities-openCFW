
void als_function_31(void)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  
  *DAT_004ae99c = 3;
  hub_timer_start(1000);
  iVar2 = als_function_27();
  *DAT_004ae734 = iVar2;
  if (iVar2 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(2,DAT_004ae4dc,DAT_004ae4d8,DAT_004ae9b0,0x1fb,DAT_004ae9ac);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_004ae9b4,DAT_004ae9b4);
    }
  }
  else {
    als_function_04(iVar2);
    als_function_05(iVar2);
    piVar1 = DAT_004ae738;
    *DAT_004ae738 = iVar2;
    als_function_11(*piVar1);
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(3,DAT_004ae4dc,DAT_004ae4d8,DAT_004ae9b0,0x205,DAT_004ae9b8,iVar2,*DAT_004ae954,
                   *DAT_004ae810);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0xcc00000,DAT_004ae9bc,DAT_004ae9bc,iVar2,*DAT_004ae954,*DAT_004ae810);
    }
    iVar2 = settings_get_config();
    if (*(int *)(iVar2 + 4) == 0) {
      als_function_23(*DAT_004ae954,1);
    }
  }
  return;
}

