# SPDX-FileCopyrightText: 2023 Technology Innovation Institute (TII)
#
# SPDX-License-Identifier: Apache-2.0
{
  pkgs ? import <nixpkgs> {},
  pythonPackages ? pkgs.python3Packages,
}:
pythonPackages.buildPythonPackage rec {
  pname = "ghafscan";
  version = pkgs.lib.removeSuffix "\n" (builtins.readFile ./VERSION);
  format = "setuptools";

  src = ./.;

  sbomnix = import ./sbomnix.nix;
  vulnxscan = import "${sbomnix}/scripts/vulnxscan/vulnxscan.nix" {pkgs = pkgs;};
  csvdiff_nix = import ./csvdiff.nix;
  csvdiff = import "${csvdiff_nix}/csvdiff/default.nix" {pkgs = pkgs;};

  propagatedBuildInputs = [
    pkgs.nix
    pkgs.reuse
    vulnxscan
    csvdiff
    pythonPackages.colorlog
    pythonPackages.gitpython
    pythonPackages.pandas
    pythonPackages.tabulate
  ];
}
