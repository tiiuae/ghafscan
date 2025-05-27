# SPDX-FileCopyrightText: 2023 Technology Innovation Institute (TII)
#
# SPDX-License-Identifier: Apache-2.0
_: {
  perSystem = {
    inputs',
    pkgs,
    lib,
    ...
  }: let
    pp = pkgs.python3Packages;
  in {
    packages = rec {
      default = ghafscan;

      ghafscan = pp.buildPythonPackage {
        pname = "ghafscan";
        version = pkgs.lib.removeSuffix "\n" (builtins.readFile ../VERSION);
        format = "setuptools";

        src = lib.cleanSource ../.;

        pythonImportsCheck = ["ghafscan"];

        propagatedBuildInputs = with pp; [
          colorlog
          gitpython
          pandas
          tabulate
        ];

        postInstall = ''
          wrapProgram $out/bin/ghafscan \
              --prefix PATH : ${lib.makeBinPath [pkgs.sbomnix inputs'.csvdiff.packages.default]}
        '';
      };
    };
  };
}
