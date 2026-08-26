import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "third_party/invensense-icm45608"
IMU_SOURCES = (
    "inv_imu_transport.c",
    "inv_imu_driver.c",
    "inv_imu_driver_advanced.c",
    "inv_imu_edmp.c",
    "inv_imu_edmp_extended_features.c",
    "inv_imu_edmp_mrm.c",
    "inv_imu_i2cm.c",
    "sif_classifier_ir.c",
    "sif_feature_extract_ir.c",
)


class InvensenseIcm45608SnapshotTests(unittest.TestCase):
    def test_offline_snapshot_verifier(self):
        subprocess.run(
            ["python3", str(SNAPSHOT / "verify_snapshot.py")],
            cwd=ROOT,
            check=True,
        )

    def test_complete_advanced_surface_compiles_for_cortex_m55(self):
        common = [
            "/usr/bin/clang",
            "--target=arm-none-eabi",
            "-mcpu=cortex-m55",
            "-mthumb",
            "-mfloat-abi=hard",
            "-mfpu=fpv5-d16",
            "-ffreestanding",
            "-fno-builtin",
            "-fno-stack-protector",
            "-Oz",
            "-std=c11",
            "-Wall",
            "-Wextra",
            "-Werror",
            "-Wno-unused-parameter",
            "-Wno-misleading-indentation",
            "-I",
            str(SNAPSHOT / "g2-compat"),
            "-I",
            str(ROOT / "third_party/cJSON/g2-compat"),
            "-I",
            str(SNAPSHOT / "src"),
        ]
        sources = [SNAPSHOT / "src/imu" / name for name in IMU_SOURCES]
        sources.extend((
            SNAPSHOT / "src/invn_mag.c",
            SNAPSHOT / "src/Ict1531x/Ict1531x.c",
        ))
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            for index, source in enumerate(sources):
                destination = output / f"icm45608-{index}.o"
                subprocess.run([*common, "-c", str(source), "-o", str(destination)],
                               cwd=ROOT, check=True)
                self.assertGreater(destination.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
