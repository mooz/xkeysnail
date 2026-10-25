#!/bin/bash
# Build an Ubuntu arm64 .deb of xkeysnail.
# The package is pure Python and is stamped Architecture: arm64 so it
# installs on Ubuntu arm64 (including Parallels ARM VMs). python-evdev,
# python-xlib, and appdirs come from apt. inotify_simple is bundled
# because Ubuntu does not ship that module.
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
cd "$ROOT"

VERSION=$(python3 -c "exec(open('xkeysnail/info.py').read()); print(__version__)")
DEB_VERSION="${VERSION}-1"
ARCH=arm64
OUT_DIR=${OUT_DIR:-"$ROOT/dist"}
OUT="$OUT_DIR/xkeysnail_${DEB_VERSION}_${ARCH}.deb"
STAGE=$(mktemp -d)
VENDOR=$(mktemp -d)
cleanup() {
    rm -rf "$STAGE" "$VENDOR"
}
trap cleanup EXIT

python3 setup.py install \
    --root="$STAGE" \
    --prefix=/usr \
    --install-layout=deb

BIN="$STAGE/usr/bin/xkeysnail"
if [[ ! -f "$BIN" ]]; then
    echo "setup.py install did not produce $BIN" >&2
    find "$STAGE" -type f >&2
    exit 1
fi
# Ubuntu images do not always provide /usr/bin/python.
sed -i '1s|^#!.*python.*|#!/usr/bin/python3|' "$BIN"
chmod 755 "$BIN"

python3 -m pip download --no-deps -d "$VENDOR" 'inotify_simple==2.0.1'
WHEEL=$(echo "$VENDOR"/inotify_simple-*.whl)
python3 -m zipfile -e "$WHEEL" "$VENDOR/unpacked"
PY_DIR=$(find "$STAGE/usr/lib" -type d -name xkeysnail -printf '%h\n' | head -1)
if [[ -z "$PY_DIR" ]]; then
    echo "could not find installed xkeysnail package directory" >&2
    find "$STAGE" -type d >&2
    exit 1
fi
cp "$VENDOR/unpacked/inotify_simple.py" "$PY_DIR/inotify_simple.py"
chmod 644 "$PY_DIR/inotify_simple.py"

DOC="$STAGE/usr/share/doc/xkeysnail"
mkdir -p "$DOC/examples"
cp "$ROOT/README.md" "$DOC/README.md"
cp "$ROOT/example/config.py" "$DOC/examples/config.py"
cp "$VENDOR/unpacked/inotify_simple-2.0.1.dist-info/licenses/LICENSE" \
    "$DOC/inotify_simple.LICENSE"
chmod 644 "$DOC/README.md" "$DOC/examples/config.py" "$DOC/inotify_simple.LICENSE"

INSTALLED_SIZE=$(du -sk "$STAGE/usr" | cut -f1)
mkdir -p "$STAGE/DEBIAN"
cat > "$STAGE/DEBIAN/control" <<EOF
Package: xkeysnail
Version: ${DEB_VERSION}
Section: utils
Priority: optional
Architecture: ${ARCH}
Maintainer: Masafumi Oyamada <stillpedant@gmail.com>
Depends: python3 (>= 3.8), python3-evdev (>= 1.3.0), python3-xlib, python3-appdirs
Homepage: https://github.com/mooz/xkeysnail
Installed-Size: ${INSTALLED_SIZE}
Description: keyboard remapping tool for the X environment
 xkeysnail remaps keyboard events with evdev and uinput, including
 per-application and multi-stroke bindings.
 .
 Device nodes are read from InputDevice.path so the tool runs on
 python-evdev 1.9 and later, where InputDevice.fn was removed.
EOF

cat > "$DOC/copyright" <<'EOF'
Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: xkeysnail
Upstream-Contact: Masafumi Oyamada <stillpedant@gmail.com>
Source: https://github.com/mooz/xkeysnail

Files: *
Copyright: Masafumi Oyamada
License: GPL

Files: usr/lib/python3/dist-packages/inotify_simple.py
Copyright: 2016, Chris Billington
License: BSD-2-Clause
 The full license text is installed as
 /usr/share/doc/xkeysnail/inotify_simple.LICENSE
EOF

mkdir -p "$OUT_DIR"
rm -f "$OUT"
dpkg-deb --root-owner-group --build "$STAGE" "$OUT"
echo "Built $OUT"
dpkg-deb --info "$OUT"
