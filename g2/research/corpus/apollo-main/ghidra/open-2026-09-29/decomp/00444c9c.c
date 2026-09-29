
undefined8 semantic_OtaBufferedFlashWrite(uint param_1,int param_2,uint param_3,uint param_4)

{
  int *piVar1;
  int *piVar2;
  ushort uVar3;
  uint uVar4;
  int iVar5;
  byte bVar6;
  byte bVar7;
  int iVar8;
  
  piVar2 = DAT_0044559c;
  piVar1 = DAT_0044542c;
  bVar6 = 0;
  if (param_3 < *(ushort *)(DAT_0044559c + 1)) {
    uVar4 = 0;
  }
  else {
    param_3 = param_3 - *(ushort *)(DAT_0044559c + 1);
    if (((param_3 < *(uint *)(DAT_00445430 + 0x38)) ||
        (((*(int *)*DAT_0044542c + *(int *)(DAT_00445430 + 0xc)) - 1U &
         ~(*(int *)*DAT_0044542c - 1U)) + *(uint *)(DAT_00445430 + 0x38) <= param_3)) ||
       ((param_3 & *(int *)*DAT_0044542c - 1U) != 0)) {
      uVar4 = 0;
    }
    else {
      if (*(int *)(*DAT_0044542c + 0x10) != 0) {
        (**(code **)(*DAT_0044542c + 0x10))();
      }
      while (bVar7 = 1, (param_1 & 0xffff) != 0) {
        uVar4 = *(int *)*piVar1 - (uint)*(ushort *)(piVar2 + 1);
        if ((param_1 & 0xffff) < (*(int *)*piVar1 - (uint)*(ushort *)(piVar2 + 1) & 0xffff)) {
          uVar4 = param_1;
        }
        for (uVar3 = 0; (uint)uVar3 < (uVar4 & 0xffff); uVar3 = uVar3 + 1) {
          *(undefined1 *)(*piVar2 + (uint)*(ushort *)(piVar2 + 1)) =
               *(undefined1 *)(param_2 + (uint)uVar3);
          *(short *)(piVar2 + 1) = (short)piVar2[1] + 1;
        }
        param_1 = param_1 - uVar4;
        param_2 = param_2 + (uVar4 & 0xffff);
        if (((param_4 & 0xff) != 0) || ((uint)*(ushort *)(piVar2 + 1) == *(uint *)*piVar1)) {
          iVar8 = *(int *)*piVar1 * (uint)bVar6 + param_3;
          iVar5 = (**(code **)(*piVar1 + 0x1c))(iVar8,*piVar2,*(undefined4 *)*piVar1);
          if ((iVar5 != 0) ||
             (iVar5 = _verifyFlashContent(iVar8,*piVar2,(short)piVar2[1],*piVar1), iVar5 != 0)) {
            bVar7 = 0;
            break;
          }
          bVar6 = bVar6 + 1;
          *(undefined2 *)(piVar2 + 1) = 0;
        }
      }
      if (*(int *)(*piVar1 + 0x14) != 0) {
        (**(code **)(*piVar1 + 0x14))();
      }
      uVar4 = (uint)bVar7;
    }
  }
  return CONCAT44(param_4,uVar4);
}

