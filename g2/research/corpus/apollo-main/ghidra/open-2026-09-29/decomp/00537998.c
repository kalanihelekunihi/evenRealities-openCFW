
void smpCalcS1(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 uVar1;
  undefined4 local_28;
  undefined1 auStack_24 [8];
  undefined1 auStack_1c [8];
  undefined4 uStack_14;
  
  uStack_14 = param_4;
  FUN_00542a52(auStack_24,param_4);
  FUN_00542a52(auStack_1c,param_3);
  local_28 = 0xb;
  uVar1 = FUN_00536426(param_2,auStack_24,*(undefined1 *)(DAT_00537ebc + 0xec),
                       *(undefined1 *)(param_1 + 0x3d));
  *(undefined1 *)(param_1 + 0x41) = uVar1;
  if (*(char *)(param_1 + 0x41) == -1) {
    local_28 = CONCAT13(8,CONCAT12(3,(undefined2)local_28));
    smpSmExecute(param_1,&local_28);
  }
  return;
}

