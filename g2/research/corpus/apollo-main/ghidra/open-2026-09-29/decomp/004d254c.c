
void dmPrivActResolveAddr
               (undefined2 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined1 auStack_24 [3];
  undefined1 auStack_21 [13];
  undefined4 uStack_14;
  
  iVar1 = DAT_004d2920;
  uStack_14 = param_4;
  if ((int)((uint)*(byte *)(DAT_004d2920 + 3) << 0x1f) < 0) {
    *(undefined1 *)((int)param_1 + 3) = 7;
    *(undefined1 *)(param_1 + 1) = 0x37;
    (**(code **)(DAT_004d2924 + 8))(param_1);
  }
  else {
    FUN_00439be4(DAT_004d2920,param_1 + 10,3);
    FUN_00439be4(auStack_24,(int)param_1 + 0x17,3);
    FUN_0043c0e4(auStack_21,0xd,0);
    *(byte *)(iVar1 + 3) = *(byte *)(iVar1 + 3) | 1;
    FUN_00536426(param_1 + 2,auStack_24,*(undefined1 *)(DAT_004d2924 + 0xc),*param_1,0x78);
  }
  return;
}

