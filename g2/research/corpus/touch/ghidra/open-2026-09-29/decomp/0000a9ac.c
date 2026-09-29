
void exit_wrapper(undefined4 param_1,undefined4 param_2)

{
  undefined1 extraout_r1;
  undefined1 *extraout_r2;
  undefined1 *puVar1;
  
  if (iRam0000a9cc != 0) {
    param_2 = 0;
  }
  if ((code *)*puRam0000a9d0 != (code *)0x0) {
    (*(code *)*puRam0000a9d0)(param_1,param_2);
  }
  _exit_halt(param_1);
  for (puVar1 = (undefined1 *)0x0; puVar1 != extraout_r2; puVar1 = puVar1 + 1) {
    *puVar1 = extraout_r1;
  }
  return;
}

