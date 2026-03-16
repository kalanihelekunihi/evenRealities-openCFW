#!/usr/bin/env bash
#
# install-build-dependencies — Download all SDKs required to build openCFW.
#
# Usage:
#   ./openCFW/tools/install-build-dependencies [--dry-run] [--sdk NAME]
#
# Options:
#   --dry-run   Print what would be downloaded without doing it
#   --sdk NAME  Install only the named SDK (e.g. --sdk lvgl_v9.3)
#
# Supports macOS, Linux, and Windows (Git Bash / MSYS2 / WSL).

set -euo pipefail

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SDKS_DIR="$(cd "$SCRIPT_DIR/../sdks" && pwd)"

DRY_RUN=0
ONLY_SDK=""
FAILED=()
SKIPPED=()
INSTALLED=()

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run)  DRY_RUN=1; shift ;;
        --sdk)      ONLY_SDK="$2"; shift 2 ;;
        -h|--help)
            sed -n '2,/^$/s/^# \{0,1\}//p' "$0"
            exit 0
            ;;
        *) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
done

# ---------------------------------------------------------------------------
# OS detection
# ---------------------------------------------------------------------------

detect_os() {
    case "$(uname -s)" in
        Darwin*)  echo "macos" ;;
        Linux*)   echo "linux" ;;
        CYGWIN*|MINGW*|MSYS*) echo "windows" ;;
        *)        echo "unknown" ;;
    esac
}

OS="$(detect_os)"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

log()  { printf "\033[1;34m==>\033[0m %s\n" "$*"; }
ok()   { printf "\033[1;32m ✓ \033[0m %s\n" "$*"; }
warn() { printf "\033[1;33m ⚠ \033[0m %s\n" "$*"; }
err()  { printf "\033[1;31m ✗ \033[0m %s\n" "$*"; }

command_exists() { command -v "$1" &>/dev/null; }

require_cmd() {
    local cmd="$1"
    if ! command_exists "$cmd"; then
        err "Required command '$cmd' not found."
        case "$OS" in
            macos)   echo "  Install with: brew install $cmd" ;;
            linux)   echo "  Install with: sudo apt install $cmd  (or your distro's equivalent)" ;;
            windows) echo "  Install with: choco install $cmd  (or winget/scoop)" ;;
        esac
        exit 1
    fi
}

# Clone a git repo at a specific ref into the target directory.
# Usage: git_clone URL TARGET_DIR [REF]
#   REF can be a tag, branch, or commit hash. Omit for default branch.
git_clone() {
    local url="$1" target="$2" ref="${3:-}"
    local name
    name="$(basename "$target")"

    if [[ -d "$target" ]]; then
        ok "$name already exists — skipping"
        SKIPPED+=("$name")
        return 0
    fi

    if [[ "$DRY_RUN" -eq 1 ]]; then
        log "[dry-run] git clone $url → $target ${ref:+(ref: $ref)}"
        return 0
    fi

    log "Cloning $name …"
    if [[ -n "$ref" ]]; then
        # Try shallow clone at tag/branch first; fall back to full clone + checkout for commits
        if git clone --depth 1 --branch "$ref" "$url" "$target" 2>/dev/null; then
            ok "$name ($ref)"
        else
            git clone "$url" "$target"
            git -C "$target" checkout "$ref"
            ok "$name ($ref)"
        fi
    else
        git clone --depth 1 "$url" "$target"
        ok "$name (default branch)"
    fi
    INSTALLED+=("$name")
}

# Download and extract an archive.
# Usage: archive_download URL TARGET_DIR [STRIP_COMPONENTS]
#   STRIP_COMPONENTS: number of leading path components to strip (default 1)
archive_download() {
    local url="$1" target="$2" strip="${3:-1}"
    local name
    name="$(basename "$target")"
    local tmpfile

    if [[ -d "$target" ]]; then
        ok "$name already exists — skipping"
        SKIPPED+=("$name")
        return 0
    fi

    if [[ "$DRY_RUN" -eq 1 ]]; then
        log "[dry-run] download $url → $target"
        return 0
    fi

    log "Downloading $name …"
    tmpfile="$(mktemp)"

    if command_exists curl; then
        curl -fSL --retry 3 -o "$tmpfile" "$url"
    elif command_exists wget; then
        wget -q -O "$tmpfile" "$url"
    else
        err "Neither curl nor wget found"
        exit 1
    fi

    mkdir -p "$target"

    case "$url" in
        *.tar.gz|*.tgz)
            tar xzf "$tmpfile" -C "$target" --strip-components="$strip"
            ;;
        *.zip)
            # Extract to temp dir, then move contents (handles strip-components)
            local tmpdir
            tmpdir="$(mktemp -d)"
            unzip -q "$tmpfile" -d "$tmpdir"
            if [[ "$strip" -eq 1 ]]; then
                # Move the single top-level directory's contents
                local inner
                inner="$(find "$tmpdir" -mindepth 1 -maxdepth 1 -type d | head -1)"
                if [[ -n "$inner" ]]; then
                    mv "$inner"/* "$inner"/.[!.]* "$target"/ 2>/dev/null || mv "$inner"/* "$target"/
                else
                    mv "$tmpdir"/* "$target"/
                fi
            else
                mv "$tmpdir"/* "$target"/
            fi
            rm -rf "$tmpdir"
            ;;
        *)
            err "Unknown archive format: $url"
            rm -f "$tmpfile"
            FAILED+=("$name")
            return 1
            ;;
    esac

    rm -f "$tmpfile"
    ok "$name"
    INSTALLED+=("$name")
}

# Record an SDK that requires manual download.
manual_download() {
    local name="$1" reason="$2"
    if [[ -d "$SDKS_DIR/$name" ]]; then
        ok "$name already exists — skipping"
        SKIPPED+=("$name")
        return 0
    fi
    warn "$name — manual download required: $reason"
    FAILED+=("$name (manual)")
}

# Gate: skip if --sdk was specified and this isn't the one
should_install() {
    [[ -z "$ONLY_SDK" || "$ONLY_SDK" == "$1" ]]
}

# ---------------------------------------------------------------------------
# Prerequisites
# ---------------------------------------------------------------------------

log "Detected OS: $OS"

require_cmd git
if ! command_exists curl && ! command_exists wget; then
    err "Either curl or wget is required"
    exit 1
fi
if ! command_exists unzip; then
    warn "unzip not found — .zip downloads will fail"
fi

# ---------------------------------------------------------------------------
# SDK definitions
# ---------------------------------------------------------------------------

#-- 1. LVGL v9.3 (GUI framework) ------------------------------------------
should_install "lvgl_v9.3" && \
    git_clone "https://github.com/lvgl/lvgl.git" \
              "$SDKS_DIR/lvgl_v9.3" "v9.3.0"

#-- 2. lv_freetype (LVGL FreeType integration, legacy standalone) ----------
should_install "lv_freetype" && \
    git_clone "https://github.com/lvgl/lv_lib_freetype.git" \
              "$SDKS_DIR/lv_freetype" "master"

#-- 3. FreeType 2.13.2 (font rendering) -----------------------------------
should_install "freetype" && \
    archive_download "https://download.savannah.gnu.org/releases/freetype/freetype-2.13.2.tar.gz" \
                     "$SDKS_DIR/freetype"

#-- 4. AmbiqSuite v5 (Apollo510 HAL, Zephyr module) -----------------------
should_install "AmbiqSuite_v5" && \
    git_clone "https://github.com/AmbiqMicro/ambiqhal_ambiq.git" \
              "$SDKS_DIR/AmbiqSuite_v5" "apollo510-dev"

#-- 5. neuralSPOT v1.3.0 (Ambiq ML/AI framework) --------------------------
should_install "neuralSPOT" && \
    git_clone "https://github.com/AmbiqAI/neuralSPOT.git" \
              "$SDKS_DIR/neuralSPOT" "v1.3.0"

#-- 6. nRF Connect SDK v2.7.0 (Nordic Zephyr NCS) -------------------------
should_install "nRF_Connect_v2.7.0" && \
    git_clone "https://github.com/nrfconnect/sdk-nrf.git" \
              "$SDKS_DIR/nRF_Connect_v2.7.0" "v2.7.0"

#-- 7. nRF5 SDK 17.1.0 (Nordic classic SDK) -------------------------------
should_install "nRF5_SDK_17.1.0_ddde560" && \
    archive_download "https://nsscprodmedia.blob.core.windows.net/prod/software-and-other-downloads/sdks/nrf5/binaries/nRF5_SDK_17.1.0_ddde560.zip" \
                     "$SDKS_DIR/nRF5_SDK_17.1.0_ddde560"

#-- 8. npmx v1.3.1 (Nordic nPM PMIC drivers) ------------------------------
should_install "npmx" && \
    git_clone "https://github.com/NordicSemiconductor/npmx.git" \
              "$SDKS_DIR/npmx" "v1.3.1"

#-- 9. nPM1300 EK Hardware (Nordic PMIC eval kit schematics) ---------------
should_install "nPM1300_EK_Hardware" && \
    git_clone "https://github.com/NordicSemiconductor/nPM1300-EK-Hardware.git" \
              "$SDKS_DIR/nPM1300_EK_Hardware" "main"

#-- 10. STM32CubeF0 (STM32F0 HAL) -----------------------------------------
should_install "STM32CubeF0" && \
    git_clone "https://github.com/STMicroelectronics/STM32CubeF0.git" \
              "$SDKS_DIR/STM32CubeF0" "master"

#-- 11. STM32CubeL0 v1.12.4 (STM32L0 HAL) ---------------------------------
should_install "STM32CubeL0" && \
    git_clone "https://github.com/STMicroelectronics/STM32CubeL0.git" \
              "$SDKS_DIR/STM32CubeL0" "v1.12.4"

#-- 12. STM32CubeL1 v1.10.6 (STM32L1 HAL) ---------------------------------
should_install "STM32CubeL1" && \
    git_clone "https://github.com/STMicroelectronics/STM32CubeL1.git" \
              "$SDKS_DIR/STM32CubeL1" "v1.10.6"

#-- 13. LC3 codec v1.1.3 (Google/Intel, Bluetooth LE Audio) ----------------
should_install "lc3" && \
    git_clone "https://github.com/google/liblc3.git" \
              "$SDKS_DIR/lc3" "v1.1.3"

#-- 14. BQ25180 (TI charger IC driver) ------------------------------------
should_install "bq25180" && \
    git_clone "https://github.com/libmcu/bq25180.git" \
              "$SDKS_DIR/bq25180" "main"

#-- 15. BQ27427 v1.0.4 (TI fuel gauge, Arduino library) -------------------
should_install "bq27427" && \
    git_clone "https://github.com/edreanernst/BQ27427_Arduino_Library.git" \
              "$SDKS_DIR/bq27427" "main"

#-- 16. OPT300x (TI light sensor driver, LibDriver) -----------------------
should_install "opt3007" && \
    git_clone "https://github.com/libdriver/opt300x.git" \
              "$SDKS_DIR/opt3007" "master"

#-- 17. MX25 series flash driver (Macronix MX25U25643G) -------------------
should_install "mx25u25643g" && \
    git_clone "https://github.com/jcu-eresearch/c-MX25-Series.git" \
              "$SDKS_DIR/mx25u25643g" "master"

#-- 18. ICM45608 Arduino driver (TDK/InvenSense IMU) ----------------------
should_install "ICM45608" && {
    if [[ -d "$SDKS_DIR/ICM45608" ]]; then
        ok "ICM45608 already exists — skipping"
        SKIPPED+=("ICM45608")
    elif [[ "$DRY_RUN" -eq 1 ]]; then
        log "[dry-run] clone ICM45608 (arduino + c_driver) → $SDKS_DIR/ICM45608"
    else
        log "Cloning ICM45608 …"
        mkdir -p "$SDKS_DIR/ICM45608"
        git clone --depth 1 "https://github.com/tdk-invn-oss/motion.arduino.ICM45608.git" \
            "$SDKS_DIR/ICM45608/arduino"
        git clone --depth 1 "https://github.com/tdk-invn-oss/motion.mcu.icm45608.driver.git" \
            "$SDKS_DIR/ICM45608/c_driver"
        ok "ICM45608 (arduino + c_driver)"
        INSTALLED+=("ICM45608")
    fi
}

#-- 19. EM9305 BLE headers (extracted from AmbiqSuite) ---------------------
should_install "em9305" && {
    if [[ -d "$SDKS_DIR/em9305" ]]; then
        ok "em9305 already exists — skipping"
        SKIPPED+=("em9305")
    elif [[ -d "$SDKS_DIR/AmbiqSuite_v5" ]]; then
        if [[ "$DRY_RUN" -eq 1 ]]; then
            log "[dry-run] extract em9305 headers from AmbiqSuite_v5"
        else
            log "Extracting em9305 headers from AmbiqSuite_v5 …"
            mkdir -p "$SDKS_DIR/em9305/include" "$SDKS_DIR/em9305/src"
            # Copy EM9305 BLE driver files from AmbiqSuite
            find "$SDKS_DIR/AmbiqSuite_v5" -name "*em9305*" -type f | while read -r f; do
                case "$f" in
                    *.h) cp "$f" "$SDKS_DIR/em9305/include/" ;;
                    *.c) cp "$f" "$SDKS_DIR/em9305/src/" ;;
                esac
            done
            ok "em9305 (extracted from AmbiqSuite_v5)"
            INSTALLED+=("em9305")
        fi
    else
        warn "em9305 — install AmbiqSuite_v5 first (EM9305 headers are extracted from it)"
        FAILED+=("em9305")
    fi
}

#-- 20. Apollo510-EVB (Embedded Wizard — requires license) -----------------
should_install "Apollo510-EVB" && \
    manual_download "Apollo510-EVB" \
        "Embedded Wizard Build Environment — download from https://www.embedded-wizard.de/ (requires license)"

#-- 21. LC3 Conformance (Bluetooth SIG — requires login) -------------------
should_install "lc3_conformance" && \
    manual_download "lc3_conformance" \
        "Bluetooth SIG conformance suite — download from https://www.bluetooth.com/specifications/specs/ (requires SIG login)"

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

echo ""
log "──────────────────────────────────────"
log "Summary"
log "──────────────────────────────────────"
[[ ${#INSTALLED[@]} -gt 0 ]] && ok "Installed: ${INSTALLED[*]}"
[[ ${#SKIPPED[@]}  -gt 0 ]] && ok "Already present: ${SKIPPED[*]}"
[[ ${#FAILED[@]}   -gt 0 ]] && warn "Needs attention: ${FAILED[*]}"
[[ ${#INSTALLED[@]} -eq 0 && ${#SKIPPED[@]} -gt 0 && ${#FAILED[@]} -eq 0 ]] && \
    log "All SDKs already installed."
echo ""
