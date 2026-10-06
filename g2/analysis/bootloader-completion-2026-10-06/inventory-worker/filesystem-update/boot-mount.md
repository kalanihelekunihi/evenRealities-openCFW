# Boot filesystem initializer provider

The provider is `g2/components/bootloader/filesystem/boot_mount.c`, ABI
`uint32_t opencfw_provider_421210(void)` in `boot_mount.h`. It uses the source
littlefs v2.10.1 config/callbacks and stock addresses: filesystem object
`0x20026878`, config `0x00431070`, ready flag `0x2002711c`, static boot-count
`lfs_file_t` at `0x20026c0c`. The locked input is
`g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin`, SHA-256
`f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`, loaded at
`0x00410000`.

Stock function identities from the locked image:

| Entry | Interval | Bytes | SHA-256 |
| --- | --- | ---: | --- |
| directory ensure `0x4210c8` | `[0x4210c8,0x421210)` | 328 | `33bfb1eca1b24cb152f5f2bd422c0761b8df54e6f0ecfa887bd77ca1eac104cb` |
| directory recovery `0x4211b0` | `[0x4211b0,0x421210)` | 96 | `9c3d0c94a411e7e0a666d918d23a0c8f4eefecd2d5a32761767786bf1f47bc08` |
| initializer `0x421210` | `[0x421210,0x4212d8)` | 200 | `07d8267cfa9725c9ac0ee613334d09968b780b890c4680f612546239bff1adf8` |

The directory loop calls `lfs_dir_open(fs, dir, path)` for `/firmware`, `/ota`,
`/user`, `/log`; it does not call `lfs_stat`. If open succeeds, it calls
`lfs_dir_close` and continues. If open returns `LFS_ERR_NOENT`, it calls
`lfs_mkdir`; every mkdir result is logged and the loop continues, including
errors other than `LFS_ERR_EXIST`. Any other directory-open result logs and
returns `-1`. This maps the stock `0x415288` directory-open wrapper, `0x41531c`
directory-close wrapper, and `0x41527e` mkdir wrapper. The close wrapper
reaches `0x410da8`, which removes the directory from littlefs's open mlist;
the source littlefs `lfs_dir_close` path performs that cleanup.

Initializer flow: mount; if it fails, format and retry mount; a second mount
failure logs and returns 9. It then runs the directory loop; a non-ENOENT
directory-open error logs and invokes `0x4211b0`, but ignores that recovery
return. Recovery unmounts, formats, mounts, and re-runs directory creation;
mount or directory-recovery failure returns 9. The initializer then sets the
ready flag, uses the fixed object `0x20026c0c` and path string `boot_count`
(literal `0x433fc8`), and directly calls littlefs wrappers with no allocator
or filesystem mutex: open flags `0x103`, read four bytes, increment, seek to
offset zero, write four bytes, close. It logs and returns zero. The count local
starts at zero and the read/write results are ignored, matching the original
flow.

Validation is recorded in `boot-mount-differential.json`. The fixture compiles
the candidate provider and source littlefs for Cortex-M4, executes original
stock instructions and candidate ARM instructions on separate identical
synthetic NOR images, and asserts equal final NOR bytes, return status, and
ready state in four cases:

- blank media format/mount, directory creation, and boot count 1 then 2 on a
  second initializer call;
- an existing regular file named `firmware`, forcing a non-ENOENT directory
  open error and real stock `0x4211b0` unmount/format/remount recovery;
- one injected NOR program failure on the first mkdir, exercising the rule
  that mkdir errors log and continue rather than aborting directory setup.

The focused host target is `make -C g2/components/bootloader/filesystem
host-boot-mount-test`; it writes only to `/tmp/opencfw-boot-mount-test`. It
passed with ASAN/UBSAN and confirms no mutex/allocator calls from the new
initializer path.

Limits: NOR, lower read/program/erase, and log sinks are synthetic. The
original and source runs produce equal storage bytes for these cases; logger
format/variadic ABI and payloads are intercepted, not differentially compared.
The one injected mkdir failure results in identical final NOR and state, while
the source logger adapter records one extra event because the component NOR
callback also reports its I/O error. This is not a physical filesystem image,
hardware test, IAR object match, or bootability claim. The provider is not yet
wired into the shared component/root combined linker.
