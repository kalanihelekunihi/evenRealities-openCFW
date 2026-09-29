
void at_core_output(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  undefined4 uStack_c;
  undefined4 uStack_8;
  undefined4 uStack_4;
  
  iVar2 = DAT_00541580;
  iVar4 = DAT_00541580 + 0x24;
  uStack_c = param_2;
  uStack_8 = param_3;
  uStack_4 = param_4;
  iVar3 = FUN_0044b76c(iVar4,0x100,param_1,&uStack_c);
  if (0 < iVar3) {
    bVar1 = *(byte *)(iVar2 + 0x14);
    if (bVar1 == 0) {
      for (uVar5 = 1; uVar5 < 3; uVar5 = uVar5 + 1) {
        if (((int)((*(uint *)(iVar2 + 0x10) >> (uVar5 & 0xff)) << 0x1f) < 0) &&
           (*(int *)(iVar2 + uVar5 * 4 + 0x18) != 0)) {
          (**(code **)(iVar2 + uVar5 * 4 + 0x18))(iVar4,iVar3);
        }
      }
    }
    else if (bVar1 == 2) {
      if (((int)((uint)*(byte *)(iVar2 + 0x10) << 0x1d) < 0) && (*(int *)(iVar2 + 0x20) != 0)) {
        (**(code **)(iVar2 + 0x20))(iVar4,iVar3);
      }
    }
    else if (((bVar1 < 2) && ((int)((uint)*(byte *)(iVar2 + 0x10) << 0x1e) < 0)) &&
            (*(int *)(iVar2 + 0x1c) != 0)) {
      (**(code **)(iVar2 + 0x1c))(iVar4,iVar3);
    }
  }
  return;
}

