
undefined8 FUN_0058c138(int param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  uint uVar1;
  uint uVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  undefined1 local_28;
  undefined1 uStack_27;
  undefined1 uStack_26;
  undefined1 uStack_25;
  undefined1 local_24;
  undefined1 uStack_23;
  undefined1 uStack_22;
  undefined1 uStack_21;
  
  local_24 = (undefined1)param_4;
  uStack_23 = (byte)((uint)param_4 >> 8);
  uStack_22 = (byte)((uint)param_4 >> 0x10);
  uStack_21 = (undefined1)((uint)param_4 >> 0x18);
  local_28 = (undefined1)param_3;
  uStack_27 = (byte)((uint)param_3 >> 8);
  uStack_26 = (byte)((uint)param_3 >> 0x10);
  uStack_25 = (undefined1)((uint)param_3 >> 0x18);
  if (param_1 != 0) {
    FUN_0044130c(param_1,param_2 & 0xff,0);
    uVar1 = FUN_0044104c(DAT_0058c72c);
    local_28 = (undefined1)uVar1;
    uStack_27 = (byte)(uVar1 >> 8);
    uStack_26 = (byte)(uVar1 >> 0x10);
    uStack_25 = (undefined1)(uVar1 >> 0x18);
    uVar2 = FUN_0044104c(0xffffff);
    local_24 = (undefined1)uVar2;
    uStack_23 = (byte)(uVar2 >> 8);
    uStack_22 = (byte)(uVar2 >> 0x10);
    uStack_21 = (undefined1)(uVar2 >> 0x18);
    uVar3 = FUN_00441068((int)(param_2 * ((uint)uStack_22 - (uint)uStack_26)) / 0xff +
                         (uint)uStack_26 & 0xff,
                         (int)(param_2 * ((uint)uStack_23 - (uint)uStack_27)) / 0xff +
                         (uint)uStack_27 & 0xff,
                         (int)(param_2 * ((uVar2 & 0xff) - (uVar1 & 0xff))) / 0xff + (uVar1 & 0xff)
                         & 0xff);
    uVar1 = FUN_0044ddea(param_1);
    for (uVar2 = 0; uVar2 < uVar1; uVar2 = uVar2 + 1) {
      iVar4 = FUN_0044dce2(param_1,uVar2);
      if (iVar4 != 0) {
        iVar5 = FUN_0043e2d4(iVar4,DAT_0058c734);
        if (iVar5 == 0) {
          iVar5 = FUN_0043e2d4(iVar4,DAT_0058c730);
          if (iVar5 == 0) {
            FUN_0058c138(iVar4,param_2);
          }
          else {
            FUN_0044140e(iVar4,uVar3,0);
          }
        }
        else {
          FUN_004413ce(iVar4,(int)(param_2 * 0xcc) / 0xff + 0x33U & 0xff,0);
        }
      }
    }
  }
  return CONCAT17(uStack_21,
                  CONCAT16(uStack_22,
                           CONCAT15(uStack_23,
                                    CONCAT14(local_24,CONCAT13(uStack_25,
                                                               CONCAT12(uStack_26,
                                                                        CONCAT11(uStack_27,local_28)
                                                                       ))))));
}

