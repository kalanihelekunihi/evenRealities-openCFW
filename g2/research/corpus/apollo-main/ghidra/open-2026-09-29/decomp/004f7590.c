
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_004f7590(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  uint *puVar2;
  int iVar3;
  uint uVar4;
  undefined4 uStack_10;
  undefined4 uStack_c;
  
  piVar1 = DAT_004f7ae0;
  uStack_10 = param_3;
  uStack_c = param_4;
  if ((((*DAT_004f7ae0 != 0) && (*DAT_004f7c08 != '\0')) &&
      (iVar3 = FUN_0043e2ea(*DAT_004f7ae0), iVar3 != 0)) &&
     (iVar3 = FUN_0043e0e0(*piVar1,1), iVar3 == 0)) {
    uVar4 = osKernelGetTickCount();
    puVar2 = DAT_004f7c04;
    if ((DAT_004f7c04[1] + (uint)(0xfffff82f < *DAT_004f7c04) == 0) &&
       (*DAT_004f7c04 + 2000 < uVar4)) {
      uVar4 = osKernelGetTickCount();
      *puVar2 = uVar4;
      puVar2[1] = 0;
      iVar3 = FUN_0045a568();
      if ((iVar3 == 1) &&
         ((iVar3 = FUN_00443484(), iVar3 == 1 && (iVar3 = FUN_004434d0(1), iVar3 == 1)))) {
        uStack_10 = *_DAT_004f8294;
        uStack_c = _DAT_004f8294[1];
        FUN_00464bb2(1,&uStack_10,6,0);
      }
    }
  }
  return CONCAT44(uStack_c,uStack_10);
}

