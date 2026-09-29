
undefined8 FUN_005be024(int param_1,undefined4 param_2,int param_3,undefined4 param_4)

{
  undefined1 *puVar1;
  undefined4 uVar2;
  
  puVar1 = (undefined1 *)(**(code **)(param_1 + 0x20))(*(undefined4 *)(param_1 + 0x28),1,0x40);
  if (puVar1 != (undefined1 *)0x0) {
    uVar2 = (**(code **)(param_1 + 0x20))(*(undefined4 *)(param_1 + 0x28),8,0x5a0);
    *(undefined4 *)(puVar1 + 0x24) = uVar2;
    if (*(int *)(puVar1 + 0x24) == 0) {
      (**(code **)(param_1 + 0x24))(*(undefined4 *)(param_1 + 0x28),puVar1);
      puVar1 = (undefined1 *)0x0;
    }
    else {
      uVar2 = (**(code **)(param_1 + 0x20))(*(undefined4 *)(param_1 + 0x28),1,param_3);
      *(undefined4 *)(puVar1 + 0x28) = uVar2;
      if (*(int *)(puVar1 + 0x28) == 0) {
        (**(code **)(param_1 + 0x24))
                  (*(undefined4 *)(param_1 + 0x28),*(undefined4 *)(puVar1 + 0x24));
        (**(code **)(param_1 + 0x24))(*(undefined4 *)(param_1 + 0x28),puVar1);
        puVar1 = (undefined1 *)0x0;
      }
      else {
        *(int *)(puVar1 + 0x2c) = *(int *)(puVar1 + 0x28) + param_3;
        *(undefined4 *)(puVar1 + 0x38) = param_2;
        *puVar1 = 0;
        FUN_005bdfca(puVar1,param_1,0);
      }
    }
  }
  return CONCAT44(param_4,puVar1);
}

