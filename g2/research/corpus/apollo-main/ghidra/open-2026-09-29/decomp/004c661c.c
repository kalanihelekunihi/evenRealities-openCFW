
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 device_mgr_fn_004c661c(void)

{
  undefined4 uVar1;
  undefined2 uStack_10;
  undefined2 uStack_e;
  
  uVar1 = _DAT_004c6c74[1];
  uStack_e = (undefined2)((uint)*_DAT_004c6c74 >> 0x10);
  uStack_10 = 2;
  device_mgr_fn_004c659a(&uStack_10);
  return CONCAT44(uVar1,CONCAT22(uStack_e,uStack_10));
}

