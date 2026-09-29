
void FUN_005cb252(int param_1,uint param_2,char param_3,undefined4 param_4,undefined4 param_5)

{
  bool bVar1;
  
  bVar1 = (*(uint *)(param_1 + 0x48) & 0x7fff) != param_2;
  if (param_3 == '\0') {
    param_4 = param_5;
  }
  if (((param_2 == 0 || !bVar1) && (*(char *)(param_1 + 0x3c) != '\b')) &&
     (*(char *)(param_1 + 0x3c) != '\x10')) {
    if (bVar1) {
      if ((*(char *)(param_1 + 0x3c) == '\x02') || (*(char *)(param_1 + 0x3c) == '\x04')) {
        *(undefined4 *)(param_1 + 0x60) = param_4;
      }
      else {
        *(undefined4 *)(param_1 + 0x5c) = param_4;
      }
    }
    else if ((*(char *)(param_1 + 0x3c) == '\x02') || (*(char *)(param_1 + 0x3c) == '\x04')) {
      *(undefined4 *)(param_1 + 0x5c) = param_4;
    }
    else {
      *(undefined4 *)(param_1 + 0x60) = param_4;
    }
  }
  return;
}

