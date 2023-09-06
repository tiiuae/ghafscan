# SPDX-FileCopyrightText: 2023 Technology Innovation Institute (TII)
#
# SPDX-License-Identifier: Apache-2.0
{
  pkgs ? import <nixpkgs> {},
  pythonPackages ? pkgs.python3Packages,
}:
pkgs.mkShell rec {
  name = "ghafscan-dev-shell";
  sbomnix = import ./sbomnix.nix;
  vulnxscan = import "${sbomnix}/scripts/vulnxscan/vulnxscan.nix" {pkgs = pkgs;};
  csvdiff_nix = import ./csvdiff.nix;
  csvdiff = import "${csvdiff_nix}/csvdiff/default.nix" {pkgs = pkgs;};
  buildInputs = [
    pkgs.nix
    pkgs.reuse
    vulnxscan
    csvdiff
    pythonPackages.black
    pythonPackages.colorlog
    pythonPackages.gitpython
    pythonPackages.pandas
    pythonPackages.pycodestyle
    pythonPackages.pylint
    pythonPackages.pytest
    pythonPackages.tabulate
    pythonPackages.venvShellHook
  ];
  venvDir = "venv";
  postShellHook = ''
    export PYTHONPATH="$PWD/src:$PYTHONPATH"

    # https://github.com/NixOS/nix/issues/1009:
    export TMPDIR="/tmp"

    # Enter python development environment
    make install-dev
  '';
}
