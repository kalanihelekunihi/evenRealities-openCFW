
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_004d306c(undefined1 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  uint uVar1;
  undefined4 uVar2;
  undefined4 uStack_10;
  
  uStack_10 = param_4;
  uVar1 = osKernelGetTickCount();
  if (*_DAT_004d3480 == 0) {
    *_DAT_004d3480 = uVar1;
  }
  else if (*_DAT_004d3480 < uVar1) {
    if (uVar1 - *_DAT_004d3480 < 10000) {
      uVar2 = 0;
      goto LAB_004d30b8;
    }
    *_DAT_004d3480 = uVar1;
  }
  FUN_0043c0e4(&uStack_10,1,0);
  uStack_10 = CONCAT31(uStack_10._1_3_,param_1);
  uVar2 = FUN_00464d1c(0x21,&uStack_10,1,0);
LAB_004d30b8:
  return CONCAT44(uStack_10,uVar2);
}

