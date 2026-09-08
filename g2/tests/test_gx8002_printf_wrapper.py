# SPDX-License-Identifier: MIT
from pathlib import Path
import subprocess
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]

class PrintfWrapperTests(unittest.TestCase):
    def test_variadic_forwarding_and_formatter_result(self):
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory);fixture=p/'fixture.c'
            fixture.write_text('''#include <stdarg.h>
#include <string.h>
extern int open_cfw_gx8002_printf(const char *, ...);
int open_cfw_gx8002_tfp_format(void *output,const char *format,va_list args) {
 if(output || strcmp(format,"fixture")) return -1;
 for(int i=1;i<=8;++i) if(va_arg(args,int)!=i) return -2;
 if(strcmp(va_arg(args,const char*),"tail")) return -3;
 return 57;
}
int main(void) { return open_cfw_gx8002_printf("fixture",1,2,3,4,5,6,7,8,"tail")==57 ? 0:1; }
''')
            binary=p/'test'
            subprocess.run(['cc','-O2','-Wall','-Wextra','-Werror',str(fixture),
                            str(ROOT/'components/shared/gx8002/runtime_gx8002_printf.c'),'-o',str(binary)],check=True)
            subprocess.run([str(binary)],check=True)
if __name__=='__main__':unittest.main()
