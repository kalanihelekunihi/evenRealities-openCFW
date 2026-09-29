
void FUN_0044df80(int param_1)

{
  char cVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  undefined4 uVar6;
  
  if ((*(ushort *)(param_1 + 0x2a) & 0x1fff) >> 0xc == 0) {
    *(ushort *)(param_1 + 0x2a) = *(ushort *)(param_1 + 0x2a) | 0x1000;
    cVar1 = FUN_00451670(param_1,0x29,0);
    if (cVar1 == '\0') {
      *(ushort *)(param_1 + 0x2a) = *(ushort *)(param_1 + 0x2a) & 0xefff;
    }
    else {
      if (*(int *)(param_1 + 8) != 0) {
        FUN_00450228(*(int *)(param_1 + 8) + 8);
      }
      iVar2 = FUN_0044dce2(param_1,0);
      while (iVar2 != 0) {
        FUN_0044df80();
        iVar2 = FUN_0044dce2(param_1,0);
      }
      iVar2 = FUN_0043e1be(param_1);
      for (iVar3 = FUN_00452edc(0); iVar3 != 0; iVar3 = FUN_00452edc(iVar3)) {
        cVar1 = FUN_00452f00(iVar3);
        if ((cVar1 == '\x01') || (cVar1 == '\x03')) {
          if ((*(int *)(iVar3 + 0x68) == param_1) ||
             ((*(int *)(iVar3 + 0x6c) == param_1 || (*(int *)(iVar3 + 0x70) == param_1)))) {
            FUN_0044df60(iVar3,param_1);
          }
          if (*(int *)(iVar3 + 0x74) == param_1) {
            *(undefined4 *)(iVar3 + 0x74) = 0;
          }
          if (*(int *)(iVar3 + 0x78) == param_1) {
            *(undefined4 *)(iVar3 + 0x78) = 0;
          }
        }
        if ((*(int *)(iVar3 + 0xb8) == iVar2) && (iVar4 = FUN_00452ffa(), param_1 == iVar4)) {
          FUN_0044df60(iVar3,param_1);
        }
      }
      cVar1 = '\x01';
      while (cVar1 == '\x01') {
        cVar1 = FUN_00484052(DAT_0044e208,param_1);
      }
      FUN_0044d16e(param_1);
      if (*(int *)(param_1 + 4) == 0) {
        iVar2 = FUN_0044dc0a(param_1);
        for (uVar5 = 0;
            (uVar5 < *(uint *)(iVar2 + 0x2d4) &&
            (*(int *)(*(int *)(iVar2 + 0x2b8) + uVar5 * 4) != param_1)); uVar5 = uVar5 + 1) {
        }
        for (; uVar5 < *(int *)(iVar2 + 0x2d4) - 1U; uVar5 = uVar5 + 1) {
          *(undefined4 *)(*(int *)(iVar2 + 0x2b8) + uVar5 * 4) =
               *(undefined4 *)(*(int *)(iVar2 + 0x2b8) + uVar5 * 4 + 4);
        }
        *(int *)(iVar2 + 0x2d4) = *(int *)(iVar2 + 0x2d4) + -1;
        uVar6 = FUN_0044f76a(*(undefined4 *)(iVar2 + 0x2b8),*(int *)(iVar2 + 0x2d4) << 2);
        *(undefined4 *)(iVar2 + 0x2b8) = uVar6;
      }
      else {
        for (uVar5 = FUN_0044de92(param_1);
            (int)(uVar5 & 0xffff) <
            (int)(*(ushort *)(*(int *)(*(int *)(param_1 + 4) + 8) + 0x30) - 1); uVar5 = uVar5 + 1) {
          *(undefined4 *)(**(int **)(*(int *)(param_1 + 4) + 8) + (uVar5 & 0xffff) * 4) =
               *(undefined4 *)(**(int **)(*(int *)(param_1 + 4) + 8) + (uVar5 & 0xffff) * 4 + 4);
        }
        *(short *)(*(int *)(*(int *)(param_1 + 4) + 8) + 0x30) =
             *(short *)(*(int *)(*(int *)(param_1 + 4) + 8) + 0x30) + -1;
        uVar6 = FUN_0044f76a(**(undefined4 **)(*(int *)(param_1 + 4) + 8),
                             (uint)*(ushort *)(*(int *)(*(int *)(param_1 + 4) + 8) + 0x30) << 2);
        **(undefined4 **)(*(int *)(param_1 + 4) + 8) = uVar6;
      }
      FUN_0044f758(param_1);
    }
  }
  return;
}

