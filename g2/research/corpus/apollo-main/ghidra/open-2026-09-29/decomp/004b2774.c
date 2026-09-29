
undefined8 FUN_004b2774(int param_1,undefined1 *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  ushort uVar5;
  undefined1 *local_20;
  undefined2 local_1c;
  undefined2 local_1a;
  undefined4 uStack_18;
  
  local_20 = param_2;
  if (param_2 == (undefined1 *)0x0) {
    iVar1 = 0;
  }
  else {
    iVar4 = *(int *)(param_1 + 0x18);
    for (uVar5 = 0; uVar5 < (*(ushort *)(iVar4 + 0x12) & 0x1ff); uVar5 = uVar5 + 1) {
      uVar3 = (int)param_2 - *(int *)(*(int *)(iVar4 + 8) + (uint)uVar5 * 0x14);
      if (uVar3 < *(ushort *)(*(int *)(iVar4 + 8) + (uint)uVar5 * 0x14 + 4)) {
        iVar1 = 0;
        if (*(char *)(*(int *)(iVar4 + 8) + (uint)uVar5 * 0x14 + 0x12) == '\x02') {
          iVar1 = uVar3 + *(ushort *)(*(int *)(iVar4 + 8) + (uint)uVar5 * 0x14 + 6);
          goto LAB_004b28ec;
        }
        if (*(char *)(*(int *)(iVar4 + 8) + (uint)uVar5 * 0x14 + 0x12) != '\0') {
          uStack_18 = param_4;
          if (*(char *)(*(int *)(iVar4 + 8) + (uint)uVar5 * 0x14 + 0x12) == '\x03') {
            _local_1c = CONCAT22((short)uVar3,(short)param_3);
            local_20 = &LAB_004b29d0_1;
            iVar2 = FUN_0052a284(&local_1a,
                                 *(undefined4 *)(*(int *)(iVar4 + 8) + (uint)uVar5 * 0x14 + 8),
                                 *(undefined2 *)(*(int *)(iVar4 + 8) + (uint)uVar5 * 0x14 + 0x10),2)
            ;
            if (iVar2 != 0) {
              iVar1 = (iVar2 - *(int *)(*(int *)(iVar4 + 8) + (uint)uVar5 * 0x14 + 8) >> 1) +
                      (uint)*(ushort *)(*(int *)(iVar4 + 8) + (uint)uVar5 * 0x14 + 6);
            }
          }
          else if (*(char *)(*(int *)(iVar4 + 8) + (uint)uVar5 * 0x14 + 0x12) == '\x01') {
            _local_1c = CONCAT22((short)((uint)param_3 >> 0x10),(short)uVar3);
            local_20 = &LAB_004b29d0_1;
            iVar2 = FUN_0052a284(&local_1c,
                                 *(undefined4 *)(*(int *)(iVar4 + 8) + (uint)uVar5 * 0x14 + 8),
                                 *(undefined2 *)(*(int *)(iVar4 + 8) + (uint)uVar5 * 0x14 + 0x10),2)
            ;
            if (iVar2 != 0) {
              iVar1 = (uint)*(ushort *)
                             (*(int *)(*(int *)(iVar4 + 8) + (uint)uVar5 * 0x14 + 0xc) +
                             (iVar2 - *(int *)(*(int *)(iVar4 + 8) + (uint)uVar5 * 0x14 + 8) >> 1) *
                             2) + (uint)*(ushort *)(*(int *)(iVar4 + 8) + (uint)uVar5 * 0x14 + 6);
            }
          }
          goto LAB_004b28ec;
        }
        iVar1 = *(int *)(*(int *)(iVar4 + 8) + (uint)uVar5 * 0x14 + 0xc);
        if ((*(char *)(iVar1 + uVar3) != '\0') ||
           (param_2 == *(undefined1 **)(*(int *)(iVar4 + 8) + (uint)uVar5 * 0x14))) {
          iVar1 = (uint)*(byte *)(iVar1 + uVar3) +
                  (uint)*(ushort *)(*(int *)(iVar4 + 8) + (uint)uVar5 * 0x14 + 6);
          goto LAB_004b28ec;
        }
      }
    }
    iVar1 = 0;
  }
LAB_004b28ec:
  return CONCAT44(local_20,iVar1);
}

