一、文件说明：

  1. 64位linux平台csky裸程序编译连接工具套件安装文件：
     csky-abiv2-elf-tools-x86_64-*.tar.gz
  ------
  2. 32位linux平台csky裸程序编译连接工具套件安装文件：
     csky-abiv2-elf-tools-i386-*.tar.gz
  ------
  3. Windows Cygwin平台csky裸程序编译连接工具套件安装文件：
     csky-abiv2-elf-tools-cygwin-*.tar.gz
  ------
  4. Windows Mingw平台csky裸程序编译连接工具套件安装文件：
     csky-abiv2-elf-tools-mingw-*.tar.gz



二、安装说明：

      1. 工具套件安装方法：

         把 csky-xx-tools-xx.tar.gz 压缩文件拷贝到安装目录下，
         通过 tar -zxf csky-xx-tools-xx.tar.gz 命令解压即可

        通过上面方法安装好工具套件后，设置安装目录下的bin目录到
        环境变量PATH中，即完成了工具套件安装。每个平台安装方法相同，上面提
        到的文件名中，“xx”代表每个平台对应文件名。

     2. 安装调试代理服务程序
        windows平台提供的是安装包形式，先解压压缩包CSKY_DebugServer_Driver*.zip，双击setup.exe安装；
	linux平台提供的是sh脚本安装包，拷贝DebugServerConsole-linux-*.sh 到主机，
        通过命令chmod +x 增加脚本执行权限，执行 ./DebugServerConsole-linux-*.sh -i 即可安装。

三、使用说明：

    1. csky-abiv2-elf-xxx套件提供给用户编译汇编链接和调试csky CPU平台上运行的裸程
       序的功能。

    2. Host机器的C库版本要求在2.5以上

    3. 支持CPU类型：CK801、CK802、CK803、CK804、CK805、CK807、CK810、CK860；

    4. Windows 平台必须预装cygwin；

    5. 建议配合CSkyDebugServer-V5.6.00版本调试代理服务程序使用；

四、MD5：
e924e3e23ee004e81388c91a3e521de5  csky-elfabiv2-tools-i386-minilibc-20190930.tar.gz
d50f2469b58cec3807160004db89e9ec  csky-elfabiv2-tools-mingw-minilibc-20190929.tar.gz
14c5da904fdce5f5b943ae8218730e4e  csky-elfabiv2-tools-x86_64-minilibc-20190929.tar.gz
