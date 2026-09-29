
undefined8 smpiScActOobCalcCb(int param_1,undefined4 param_2,int param_3,undefined4 param_4)

{
  ushort uStack_18;
  undefined1 uStack_16;
  undefined1 uStack_15;
  int iStack_14;
  undefined4 uStack_10;
  
  uStack_18 = (ushort)param_2;
  uStack_16 = (undefined1)((uint)param_2 >> 0x10);
  uStack_15 = (undefined1)((uint)param_2 >> 0x18);
  iStack_14 = param_3;
  uStack_10 = param_4;
  if (*(char *)(param_1 + 0x29) != '\x01') {
    FUN_00542a44(*(int *)(*(int *)(param_1 + 0x48) + 0x14) + 0x20,PTR_DAT_005e38b0);
  }
  if (*(char *)(param_1 + 0x22) == '\x01') {
    iStack_14 = *(int *)(*(int *)(param_1 + 0x48) + 0x14) + 0x30;
    uStack_18 = 0;
    uStack_16 = 0;
    uStack_15 = 0;
    SmpScCalcF4(param_1,param_2,*(undefined4 *)(*(int *)(param_1 + 0x48) + 8),
                *(undefined4 *)(*(int *)(param_1 + 0x48) + 8));
  }
  else {
    FUN_00542a44(*(int *)(*(int *)(param_1 + 0x48) + 0x14) + 0x30,PTR_DAT_005e38b0);
    uStack_18 = (ushort)*(byte *)(param_1 + 0x3d);
    uStack_16 = 0x1c;
    uStack_10 = 0;
    smpSmExecute(param_1,&uStack_18);
  }
  return CONCAT44(iStack_14,CONCAT13(uStack_15,CONCAT12(uStack_16,uStack_18)));
}

