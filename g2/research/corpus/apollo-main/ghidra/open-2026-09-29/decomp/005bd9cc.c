
void FUN_005bd9cc(undefined1 param_1,undefined1 param_2,undefined4 param_3,undefined4 param_4,
                 int param_5)

{
  undefined1 *puVar1;
  
  puVar1 = (undefined1 *)
           (**(code **)(param_5 + 0x20))
                     (*(undefined4 *)(param_5 + 0x28),1,0x1c,*(code **)(param_5 + 0x20),param_4);
  if (puVar1 != (undefined1 *)0x0) {
    *puVar1 = 0;
    puVar1[0x10] = param_1;
    puVar1[0x11] = param_2;
    *(undefined4 *)(puVar1 + 0x14) = param_3;
    *(undefined4 *)(puVar1 + 0x18) = param_4;
  }
  return;
}

