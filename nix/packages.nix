# SPDX-FileCopyrightText: 2023 Technology Innovation Institute (TII)
#
# SPDX-License-Identifier: Apache-2.0
{inputs, ...}: {
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

      csvdiff = (import "${inputs.ci-public}/csvdiff") {inherit pkgs;};

      ghafscan = pp.buildPythonPackage {
        pname = "ghafscan";
        version = pkgs.lib.removeSuffix "\n" (builtins.readFile ../VERSION);
        format = "setuptools";

        src = lib.cleanSource ../.;

        pythonImportsCheck = ["ghafscan"];

        propagatedBuildInputs =
          [
            pkgs.reuse
            csvdiff
            # we need vulnxscan from sbombnix
            inputs'.sbomnix.packages.default
          ]
          ++ (with pp; [
            colorlog
            gitpython
            pandas
            tabulate
          ]);
      };
    };
  };
}
