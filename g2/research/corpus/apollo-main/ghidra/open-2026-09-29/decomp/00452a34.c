
undefined4 FUN_00452a34(int param_1,int param_2,int *param_3,undefined4 param_4)

{
  undefined1 uVar1;
  undefined1 uVar2;
  byte bVar3;
  int iVar4;
  undefined4 uVar5;
  uint uVar6;
  undefined4 local_18;
  
  *param_3 = param_1;
  param_3[1] = param_2;
  local_18 = param_4;
  uVar2 = FUN_004524a4(param_1,param_2);
  *(undefined1 *)(param_3 + 0x14) = uVar2;
  if (2 < *(byte *)(param_3 + 0x14)) {
    bVar3 = FUN_00452df0(param_1,param_2,param_3);
    if (bVar3 < 0xfd) {
      *(char *)(param_3 + 0x14) = (char)((uint)bVar3 * (uint)*(byte *)(param_3 + 0x14) >> 8);
    }
    if (2 < *(byte *)(param_3 + 0x14)) {
      param_3[0xc] = 0;
      param_3[0xd] = 0x100;
      param_3[0xe] = 0x100;
      iVar4 = FUN_00451598(param_1 + 0x14);
      param_3[0x11] = iVar4 / 2;
      iVar4 = FUN_004515a4(param_1 + 0x14);
      param_3[0x12] = iVar4 / 2;
      uVar5 = FUN_004524b0(param_1,param_2);
      bVar3 = FUN_004524d0(param_1,param_2);
      local_18 = (uint)bVar3;
      uVar6 = FUN_00452e68(param_1,param_2,param_3,uVar5);
      local_18._3_1_ = (undefined1)(uVar6 >> 0x18);
      *(undefined1 *)((int)param_3 + 0x4f) = local_18._3_1_;
      local_18._1_1_ = (undefined1)(uVar6 >> 8);
      uVar2 = local_18._1_1_;
      local_18._2_1_ = (undefined1)(uVar6 >> 0x10);
      uVar1 = local_18._2_1_;
      local_18 = uVar6;
      local_18 = FUN_00441068(uVar1,uVar2,uVar6 & 0xff);
      FUN_00439be4(param_3 + 0x13,&local_18,3);
      if (param_2 != 0) {
        bVar3 = FUN_0045260a(param_1,param_2);
        *(byte *)((int)param_3 + 0x51) = *(byte *)((int)param_3 + 0x51) & 0xf8 | bVar3 & 7;
      }
    }
  }
  return local_18;
}

