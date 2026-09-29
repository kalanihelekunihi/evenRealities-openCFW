
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 hub_als_timer_callback(void)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  undefined2 uStack_10;
  undefined2 uStack_e;
  
  uVar3 = *(undefined4 *)(PTR_DAT_004a7388 + 4);
  uStack_10 = (undefined2)*(undefined4 *)PTR_DAT_004a7388;
  uStack_e = (undefined2)((uint)*(undefined4 *)PTR_DAT_004a7388 >> 0x10);
  if ((*_DAT_004a738c != 0) && (iVar1 = semantic_OtaTransferActive(), iVar1 == 0)) {
    uVar2 = osKernelGetTickCount();
    *_DAT_004a7360 = uVar2;
    uStack_10 = 2;
    HUB_SendMessage(&uStack_10);
  }
  return CONCAT44(uVar3,CONCAT22(uStack_e,uStack_10));
}

