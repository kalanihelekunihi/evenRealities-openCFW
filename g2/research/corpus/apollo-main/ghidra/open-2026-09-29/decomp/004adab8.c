
undefined4 als_function_08(undefined4 param_1)

{
  int iVar1;
  float fVar2;
  
  fVar2 = (float)semantic_get_heading_float();
  if ((int)((uint)(fVar2 < -30.0) << 0x1f) < 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(3,DAT_004ae4dc,DAT_004ae4d8,DAT_004ae4d4,0xad,DAT_004ae4d0,(double)fVar2,param_1,
                   *DAT_004ae734);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0xcc00000,DAT_004ae4e0,DAT_004ae4e0);
    }
    param_1 = *DAT_004ae734;
  }
  return param_1;
}

