
void FUN_0045f58c(int *param_1,int param_2)

{
  undefined4 *puVar1;
  
  if ((((param_1 != (int *)0x0) && (param_2 != 0)) &&
      (puVar1 = (undefined4 *)FUN_0045f840(param_1), puVar1 != (undefined4 *)0x0)) &&
     (*(char *)(puVar1 + 7) != '\x01')) {
    if (*(char *)((int)puVar1 + 0xb) == '\0') {
      if (*param_1 == 0) {
        FUN_0045f8a4(puVar1);
        param_1[1] = (int)puVar1;
      }
      else {
        FUN_0045f8a4(puVar1);
      }
    }
    else {
      if ((param_1[1] != 0) && (*(int *)(param_1[1] + 0x18) != 0)) {
        (**(code **)(param_1[1] + 0x18))(param_1[1],param_1,0x42,puVar1);
      }
      if (param_1[1] != 0) {
        param_1[1] = 0;
      }
      FUN_0044228a(*puVar1,3,0,0);
      *(undefined1 *)(puVar1 + 7) = 2;
      FUN_0045ef24(puVar1,1);
      *param_1 = (int)puVar1;
    }
  }
  return;
}

