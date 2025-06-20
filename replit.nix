{ pkgs }: {
  deps = [
    pkgs.chromium
    pkgs.at-spi2-core
    pkgs.libdrm
    pkgs.at-spi2-atk
    pkgs.gobject-introspection
    pkgs.alsa-lib
    pkgs.cairo
    pkgs.pango
    pkgs.mesa
    pkgs.xorg.libXrandr
    pkgs.xorg.libXfixes
    pkgs.xorg.libXext
    pkgs.xorg.libXdamage
    pkgs.xorg.libXcomposite
    pkgs.xorg.libX11
    pkgs.libxkbcommon
    pkgs.xorg.libxcb
    pkgs.expat
    pkgs.cups
    pkgs.atk
    pkgs.dbus
    pkgs.nspr
    pkgs.nss
    pkgs.glib
    pkgs.python311
    pkgs.python311Packages.pip
    pkgs.playwright
  ];

  postInstall = ''
    python3 -m pip install --upgrade pip
    python3 -m pip install -r requirements.txt
    python3 -m playwright install chromium
  '';
}