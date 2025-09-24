#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2023 Technology Innovation Institute (TII)
#
# SPDX-License-Identifier: Apache-2.0

# pylint: disable=too-many-instance-attributes
# pylint: disable=too-many-statements, too-many-locals

"""Run and summarize vulnerability scans for flake targets"""

import os
import sys
import re
import argparse
import logging
import subprocess
import tempfile
import shutil
import difflib
import csv
from pathlib import Path

import git
import pandas as pd
from colorlog import ColoredFormatter, default_log_colors
from tabulate import tabulate


################################################################################

LOG_SPAM = logging.DEBUG - 1
LOG = logging.getLogger(os.path.abspath(__file__))

################################################################################


def _getargs():
    """Parse command line arguments"""
    desc = "Run and summarize vulnerability scans for Ghaf flake targets."
    epil = (
        "Example: ghafscan --flakeref=github:tiiuae/ghaf?ref=main "
        "--target=packages.x86_64-linux.lenovo-x1-carbon-gen11-release"
    )
    parser = argparse.ArgumentParser(description=desc, epilog=epil)
    helps = (
        "Flake reference to specify the location of the flake target. "
        "For more details, see: "
        "https://nixos.org/manual/nix/stable/command-ref/new-cli/nix3-flake"
        "#flake-references."
    )
    parser.add_argument("-f", "--flakeref", required=True, help=helps)
    helps = "Target flake output, repeat to scan many outputs."
    parser.add_argument(
        "-t", "--target", required=True, action="append", help=helps, nargs="+"
    )
    helps = "Path to output directory (default=./result)."
    parser.add_argument("-o", "--outdir", help=helps, default="./result", type=Path)
    helps = (
        "Path to whitelist file. Vulnerabilities that match any whitelisted "
        "entries will not be included to the console output and are annotated "
        "accordingly in the output csv. See more details in the vulnxscan "
        "README.md."
    )
    parser.add_argument("-w", "--whitelist", help=helps, type=Path)
    helps = "Set the debug verbosity level between 0-3 (default: --verbose=1)"
    parser.add_argument("--verbose", help=helps, type=int, default=1)
    return parser.parse_args()


################################################################################


# Utils


def _set_log_verbosity(verbosity=1):
    """Set logging verbosity"""
    log_levels = [logging.NOTSET, logging.INFO, logging.DEBUG, LOG_SPAM]
    verbosity = min(len(log_levels) - 1, max(verbosity, 0))
    _init_logging(verbosity)


def _init_logging(verbosity=1):
    """Initialize logging"""
    if verbosity == 0:
        level = logging.NOTSET
    elif verbosity == 1:
        level = logging.INFO
    elif verbosity == 2:
        level = logging.DEBUG
    else:
        level = LOG_SPAM
    if level <= logging.DEBUG:
        logformat = (
            "%(log_color)s%(levelname)-8s%(reset)s "
            "%(filename)s:%(funcName)s():%(lineno)d "
            "%(message)s"
        )
    else:
        logformat = "%(log_color)s%(levelname)-8s%(reset)s %(message)s"
    logging.addLevelName(LOG_SPAM, "SPAM")
    default_log_colors["INFO"] = "fg_bold_white"
    default_log_colors["DEBUG"] = "fg_bold_white"
    default_log_colors["SPAM"] = "fg_bold_white"
    formatter = ColoredFormatter(logformat, log_colors=default_log_colors)
    if LOG.hasHandlers() and len(LOG.handlers) > 0:
        stream = LOG.handlers[0]
    else:
        stream = logging.StreamHandler()
    stream.setFormatter(formatter)
    if not LOG.hasHandlers():
        LOG.addHandler(stream)
    LOG.setLevel(level)


def exit_unless_command_exists(name):
    """Check if `name` is an executable in PATH"""
    name_is_in_path = shutil.which(name) is not None
    if not name_is_in_path:
        LOG.fatal("command '%s' is not in PATH", name)
        sys.exit(1)


def exec_cmd(
    cmd, raise_on_error=True, return_error=False, loglevel=logging.DEBUG, evars=None
):
    """Run shell command cmd"""
    command_str = " ".join(cmd)
    LOG.log(loglevel, "Running: %s", command_str)
    try:
        # Pass additional env variables via the 'evars' dictionary
        env = {**os.environ, **evars} if evars else {**os.environ}
        ret = subprocess.run(
            cmd, capture_output=True, encoding="utf-8", check=True, env=env
        )
        return ret
    except subprocess.CalledProcessError as error:
        LOG.debug(
            "Error running shell command:\n cmd:   '%s'\n stdout: %s\n stderr: %s",
            command_str,
            error.stdout,
            error.stderr,
        )
        if raise_on_error:
            raise error
        if return_error:
            return error
        return None


def df_from_csv_file(name, exit_on_error=True):
    """Read csv file into dataframe"""
    LOG.debug("Reading: %s", name)
    try:
        df = pd.read_csv(name, keep_default_na=False, dtype=str)
        df.reset_index(drop=True, inplace=True)
        return df
    except (pd.errors.EmptyDataError, pd.errors.ParserError) as error:
        if exit_on_error:
            LOG.fatal("Error reading csv file '%s':\n%s", name, error)
            sys.exit(1)
        LOG.debug("Error reading csv file '%s':\n%s", name, error)
        return None


def df_to_csv_file(df, name, loglevel=logging.INFO):
    """Write dataframe to csv file"""
    df.to_csv(
        path_or_buf=name, quoting=csv.QUOTE_ALL, sep=",", index=False, encoding="utf-8"
    )
    LOG.log(loglevel, "Wrote: %s", name)


def df_log(df, loglevel, tablefmt="presto"):
    """Log dataframe with given loglevel and tablefmt"""
    if LOG.level <= loglevel:
        if df.empty:
            return
        df = df.fillna("")
        table = tabulate(
            df, headers="keys", tablefmt=tablefmt, stralign="left", showindex=False
        )
        LOG.log(loglevel, "\n%s\n", table)


def filediff(file1, file2):
    """Return unified diff between `file1` and `file2` as a string"""
    f1 = Path(file1)
    f2 = Path(file2)
    if not f1.exists():
        LOG.error("Diff failed: '%s' does not exist", str(f1))
        return ""
    if not f2.exists():
        LOG.error("Diff failed: '%s' does not exist", str(f2))
        return ""
    f1_lines = f1.read_text(encoding="utf-8").splitlines()
    f2_lines = f2.read_text(encoding="utf-8").splitlines()
    diff = difflib.unified_diff(f1_lines, f2_lines, fromfile=file1, tofile=file2)
    return "\n".join(diff).strip(" \n\t")


################################################################################


class FlakeScanner:
    """Scan and report nix flake target vulnerabilities"""

    def __init__(self, flakeref):
        self.df_scan = None
        self.flakeref = flakeref
        LOG.info("Scanning '%s'", flakeref)
        self.tmpdir = Path(tempfile.mkdtemp())
        LOG.debug("Using tmpdir: %s", self.tmpdir)
        self.repodir = self.tmpdir / "repo"
        self.repodir.mkdir(parents=True, exist_ok=True)
        self._nix_clone_flakeref(flakeref)
        self.repo = git.Repo(self.repodir.as_posix())
        self.repo_head = self.repo.rev_parse("HEAD")
        LOG.info("Target repo HEAD at '%s'", self.repo_head)
        self.lockfile = None
        self.lockfile_bak = None
        self.flakefile = None
        self.flakefile_bak = None
        self._init_flakefiles()
        self.errors = {}

    def __del__(self):
        if self.tmpdir:
            LOG.debug("Removing tmpdir: %s", self.tmpdir)
            shutil.rmtree(self.tmpdir)

    def _nix_clone_flakeref(self, flakeref):
        cmd = f"nix flake clone {flakeref} --dest {self.repodir}"
        exec_cmd(cmd.split())

    def _init_flakefiles(self):
        # Backup the original flake.lock
        self.lockfile = self.repodir / "flake.lock"
        if not self.lockfile.exists():
            LOG.fatal("Missing flake.lock: %s", self.lockfile.resolve())
            sys.exit(1)
        self.lockfile_bak = self.tmpdir / "flake.lock"
        shutil.copy(self.lockfile, self.lockfile_bak)
        LOG.debug("%s:\n%s", self.lockfile, self.lockfile.read_text())
        # Backup the original flake.nix
        self.flakefile = self.repodir / "flake.nix"
        if not self.flakefile.exists():
            LOG.fatal("Missing flake.nix: %s", self.flakefile.resolve())
            sys.exit(1)
        self.flakefile_bak = self.tmpdir / "flake.nix"
        shutil.copy(self.flakefile, self.flakefile_bak)

    def scan_target(self, target, buildtime=True, nixprs=False, whitelist=None):
        """Scan given flake output target"""
        LOG.info("Scanning flake output '%s'", target)
        # Build the vulnxscan command. Note: '--nixprs' takes a long time
        # due to github rate limits. If the execution time becomes a problem,
        # consider dropping the '--nixprs'
        out = self.tmpdir / "vulnxscan.csv"
        cmd_vulnxscan = f"vulnxscan --triage --out={out}"
        if buildtime:
            cmd_vulnxscan += " --buildtime"
        if nixprs:
            cmd_vulnxscan += " --nixprs"
        if whitelist:
            cmd_vulnxscan += f" --whitelist={whitelist}"
        # First scan:
        # Before lockfile update
        LOG.info("Scanning current vulnerabilities")
        self._reset_lock()
        self._read_scan_results(cmd_vulnxscan, target, "current")
        # Second scan:
        # Update lockfile to get latest updates from the pinned channel
        self._reset_lock()
        self._update_repo_lock()
        LOG.info("Scanning vulnerabilities after lockfile update")
        self._read_scan_results(cmd_vulnxscan, target, "lock_updated")
        # Third scan:
        # Update lockfile to get latest updates from nixos-unstable
        self._reset_lock()
        self._update_repo_lock(nixpkgs_url="github:NixOS/nixpkgs/nixos-unstable")
        LOG.info("Scanning vulnerabilities after updating from nixos-unstable")
        self._read_scan_results(cmd_vulnxscan, target, "nix_unstable")

    def report(self, outdir):
        """Report scan results to console and `outdir`"""
        outdir.mkdir(parents=True, exist_ok=True)
        rawout = outdir / "data.csv"
        df_ref = None
        if rawout.exists():
            df_ref = df_from_csv_file(rawout.as_posix())
        df_targets = self.df_scan[["flakeref", "target"]].drop_duplicates()
        newstr = ""
        for scan_target in df_targets.itertuples():
            flakeref = scan_target.flakeref
            target = scan_target.target
            target_path = self._report_target(outdir, flakeref, target, df_ref)
            relative_target_path = os.path.relpath(target_path, outdir)
            newstr += f"* [Vulnerability Report: '{target}']({relative_target_path})\n"
        template = _data_file("templates/ghaf_landing.md")
        if not template.exists():
            LOG.fatal("Missing landing template '%s'", template.resolve().as_posix())
            sys.exit(1)
        marker = "TARGET_REPORTS"
        LOG.debug(marker)
        landing_str = template.read_text(encoding="utf-8")
        landing_str = landing_str.replace(marker, newstr)
        readme_target = outdir / "README.md"
        readme_target.write_text(landing_str)
        df_to_csv_file(self.df_scan, rawout.as_posix())

    def _report_target(self, outdir, flakeref, target, df_ref):
        LOG.debug("%s#%s", flakeref, target)
        template = _data_file("templates/ghaf_target.md")
        if not template.exists():
            LOG.fatal("Missing report template '%s'", template.resolve().as_posix())
            sys.exit(1)
        target_report = outdir / f"{target}.md"
        report_str = template.read_text(encoding="utf-8")
        df = self.df_scan.copy()
        df_target = df[(df["target"] == target) & (df["flakeref"] == flakeref)]
        if "whitelist" in df_target.columns:
            df_target = df_target[df_target["whitelist"] == "False"]
        if df_ref is not None:
            df = df_ref
            df_ref = df[(df["target"] == target) & (df["flakeref"] == flakeref)]
            if "whitelist" in df_ref.columns:
                df_ref = df_ref[df_ref["whitelist"] == "False"]
        marker = "TARGET_NAME"
        LOG.debug(marker)
        newstr = f"{flakeref}#{target}"
        report_str = report_str.replace(marker, newstr)
        marker = "GHAF_HEAD"
        LOG.debug(marker)
        newstr = f"{self.repo_head}"
        report_str = report_str.replace(marker, newstr)
        marker = "FIXED_IN_NIXPKGS"
        LOG.debug(marker)
        df = self._diff_scans(df_target, "current", "lock_updated")
        newstr = self._read_error(target, ["current", "lock_updated"])
        newstr = newstr if newstr else self._df_to_report_tbl(df)
        report_str = report_str.replace(marker, newstr)
        marker = "FIXED_IN_NIX_UNSTABLE"
        LOG.debug(marker)
        df = self._diff_scans(df_target, "lock_updated", "nix_unstable")
        newstr = self._read_error(target, ["lock_updated", "nix_unstable"])
        newstr = newstr if newstr else self._df_to_report_tbl(df)
        report_str = report_str.replace(marker, newstr)
        marker = "NEW_SINCE_LAST_RUN"
        LOG.debug(marker)
        if df_ref is None or df_ref.empty:
            newstr = self._read_error(target, ["current"])
            newstr = newstr if newstr else self._df_to_report_tbl(pd.DataFrame())
        else:
            df = df_target
            df_left = df[df["pintype"] == "current"]
            csv_left = self.tmpdir / "left.csv"
            df_to_csv_file(df_left, csv_left, logging.DEBUG)
            df = df_ref
            df_right = df[df["pintype"] == "current"]
            csv_right = self.tmpdir / "right.csv"
            df_to_csv_file(df_right, csv_right, logging.DEBUG)
            df = self._csvdiff(csv_left, csv_right)
            newstr = self._read_error(target, ["current"])
            newstr = newstr if newstr else self._df_to_report_tbl(df)
        report_str = report_str.replace(marker, newstr)
        marker = "CURRENT_VULNS"
        LOG.debug(marker)
        df = df_target
        df = df[df["pintype"] == "current"]
        newstr = self._read_error(target, ["current"])
        newstr = newstr if newstr else self._df_to_report_tbl(df)
        report_str = report_str.replace(marker, newstr)
        marker = "ONLY_WHITELISTED"
        LOG.debug(marker)
        newstr = "```No whitelisted vulnerabilities```"
        df = self.df_scan.copy()
        if "whitelist" in df.columns:
            df = df[df["whitelist"] != "False"]
            newstr = self._df_to_report_tbl(df, up_ver=False)
        report_str = report_str.replace(marker, newstr)
        # Write the target report
        target_report.write_text(report_str)
        return target_report

    def _diff_scans(self, df, left_pin, right_pin):
        LOG.debug("'%s' diff '%s'", left_pin, right_pin)
        df_left = df[df["pintype"] == left_pin]
        tmp_left_csv = self.tmpdir / "left.csv"
        df_to_csv_file(df_left, tmp_left_csv, logging.DEBUG)
        df_right = df[df["pintype"] == right_pin]
        tmp_right_csv = self.tmpdir / "right.csv"
        df_to_csv_file(df_right, tmp_right_csv, logging.DEBUG)
        return self._csvdiff(tmp_left_csv, tmp_right_csv)

    def _csvdiff(self, csv_left, csv_right):
        LOG.debug("")
        out = self.tmpdir / "csvdiff.csv"
        shutil.rmtree(out, ignore_errors=True)
        uids = "vuln_id,package"
        if not csv_left.exists():
            LOG.debug("Missing csv_left: '%s'", csv_left)
            return pd.DataFrame()
        if not csv_right.exists():
            LOG.debug("Missing csv_right: '%s'", csv_right)
            return pd.DataFrame()
        left = csv_left.resolve().as_posix()
        right = csv_right.resolve().as_posix()
        cmd = ["csvdiff", left, right, f"--cols={uids}", f"--out={out}"]
        ret = exec_cmd(cmd, raise_on_error=False)
        if ret is None or not out.exists():
            LOG.debug("Missing csvdiff out: '%s'", out)
            return pd.DataFrame()
        df = df_from_csv_file(out, exit_on_error=False)
        if df is None:
            LOG.debug("Failed reading csvdiff out: '%s'", out)
            return pd.DataFrame()
        df = df.astype(str)
        return df[df["diff"].str.contains("left_only")]

    def _df_to_report_tbl(self, df, up_ver=True):
        LOG.debug("")
        if df.empty:
            return "```No vulnerabilities```"
        # Sort by the following columns
        sort_cols = ["severity", "sortcol", "package", "version_local", "vuln_id"]
        if not set(sort_cols).issubset(df.columns):
            return "\n```Error: missing required columns```\n"
        df = df.sort_values(by=sort_cols, ascending=False)
        # Truncate version strings
        df["version_local"] = df["version_local"].str.slice(0, 16)
        # Report table will have the following columns
        report_cols = ["vuln_id", "package", "severity", "version_local"]
        # Optionally add the following upstream versions
        if up_ver and "version_nixpkgs" in df:
            ver_rename = "nix_unstable"
            report_cols.append(ver_rename)
            df[ver_rename] = df["version_nixpkgs"].str.slice(0, 16)
        if up_ver and "version_upstream" in df:
            ver_rename = "upstream"
            report_cols.append(ver_rename)
            df[ver_rename] = df["version_upstream"].str.slice(0, 16)
        # Add the 'comment' column
        df["comment"] = df.apply(_reformat_comment, axis=1)
        report_cols.append("comment")
        # Convert vuln_id to a hyperlink
        df["vuln_id"] = df.apply(_reformat_vuln_id, axis=1)
        # Add PR search links
        if "nixpkgs_pr" in df.columns:
            df["comment"] = df.apply(_reformat_pr_search, axis=1)
        # Select only the report_cols
        df = df[report_cols]
        df = df.drop_duplicates(keep="first")
        # Format dataframe to markdown table
        table = tabulate(
            df, headers="keys", tablefmt="github", stralign="left", showindex=False
        )
        return f"\n{table}\n"

    def _read_error(self, target, pintypes):
        LOG.debug("")
        for pintype in pintypes:
            error_key = f"{target}_{pintype}"
            if error_key in self.errors:
                return f"{self.errors[error_key]}"
        return None

    def _reset_lock(self):
        # Reset possible earlier changes to the flake.nix and lockfile
        shutil.copy(self.lockfile_bak, self.lockfile)
        shutil.copy(self.flakefile_bak, self.flakefile)

    def _evaluate_target_drv(self, target, pintype):
        eval_target = f"{str(self.repodir)}#{target}.drvPath"
        var = {"NIXPKGS_ALLOW_INSECURE": "1"}
        cmd = f"nix eval {eval_target} --no-eval-cache --impure"
        ret = exec_cmd(cmd.split(), raise_on_error=False, return_error=True, evars=var)
        if ret is None or ret.returncode != 0:
            LOG.warning("Error evaluating %s", eval_target)
            self.errors[f"{target}_{pintype}"] = (
                f"```Error evaluating '{target}' on {pintype}```<br /><br />\n"
                "For more details, see: https://github.com/tiiuae/ghafscan/actions"
            )
            return None
        drv_path = Path(str(ret.stdout).strip('"\n\t '))
        LOG.info("Target '%s' evaluates to derivation: %s", target, drv_path)
        return drv_path

    def _update_repo_lock(self, nixpkgs_url=None):
        LOG.info("Updating: %s", self.lockfile)
        if nixpkgs_url:
            # Update the nixpkgs.url reference in flake.nix
            flake_text = self.flakefile.read_text()
            # Match e.g. 'nixpkgs.url = "github:nixos/nixpkgs/nixos-23.05";'
            pattern = r"(nixpkgs\.url *= *)[^;]+"
            repl = rf'\1"{nixpkgs_url}"'
            # Replace pattern with repl in flake_text
            flake_text_new = re.sub(pattern, repl, flake_text)
            self.flakefile.write_text(flake_text_new)
            diffstr = filediff(str(self.flakefile_bak), str(self.flakefile))
            if not diffstr:
                LOG.warning(
                    "Replacing nixpkgs.url in flake.nix did not result any changes, "
                    "maybe it's already pinned to '%s'?",
                    nixpkgs_url,
                )
                LOG.debug("%s contents:\n%s", self.flakefile, flake_text)
        # Update the lockfile
        cmd = f"nix flake lock {str(self.repodir)} --update-input nixpkgs"
        exec_cmd(cmd.split())
        diffstr = filediff(str(self.lockfile_bak), str(self.lockfile))
        if diffstr:
            LOG.info("Updated lockfile:\n%s", diffstr)

    def _read_scan_results(self, cmd, target, pintype):
        out_triage = self.tmpdir / "vulnxscan.triage.csv"
        shutil.rmtree(out_triage, ignore_errors=True)
        drv_path = self._evaluate_target_drv(target, pintype)
        if drv_path is None:
            return
        cmd = f"{cmd} {str(drv_path)}"
        ret = exec_cmd(cmd.split())
        LOG.debug("vulnxscan ==>\n\n%s\n\n<== vulnxscan\n", ret.stderr)
        if not out_triage.exists():
            LOG.warning("vulnxscan triage output not found: %s", out_triage)
            return
        df = df_from_csv_file(out_triage, exit_on_error=False)
        if df is None:
            LOG.warning("Invalid vulnxscan output '%s'", out_triage)
            return
        # Add the following columns to the beginning of df
        df.insert(0, "pintype", pintype)
        df.insert(0, "flakeref", self.flakeref)
        df.insert(0, "target", target)
        self.df_scan = pd.concat([self.df_scan, df], ignore_index=True)


################################################################################

# Helpers


def _reformat_vuln_id(row):
    if not row.vuln_id or not row.url:
        return ""
    # Return vuln_id as markdown hyperlink that points links to row.url
    return f"[{row.vuln_id}]({row.url})"


def _reformat_comment(row):
    if not hasattr(row, "whitelist_comment") or not row.whitelist_comment:
        return ""
    comment = str(row.whitelist_comment)
    # Replace urls in the comment entry with markdown hyperlinks
    pattern = r"(https?://\S+\w/?)"
    comment_mod = re.sub(pattern, r"[link](\1)", comment)
    return comment_mod


def _reformat_pr_search(row):
    if not hasattr(row, "nixpkgs_pr") or not row.nixpkgs_pr:
        if hasattr(row, "comment"):
            return row.comment
        return ""
    # Replace urls in nixpkgs_pr entry with markdown hyperlinks
    pattern = r"(https?://\S+\w/?)"
    pr_search = re.sub(pattern, r"[PR](\1)", row.nixpkgs_pr)
    pr_search = " ".join(pr_search.split())
    if pr_search:
        pr_search = f" *[{', '.join(pr_search.split(' '))}]*"
    if row.comment:
        pr_search = f"{row.comment} {pr_search}"
    return pr_search


def _data_file(fname):
    """Return the path to a data file."""
    return Path(os.path.join(os.path.split(__file__)[0], fname))


################################################################################

# Main


def main():
    """main entry point"""
    args = _getargs()
    _set_log_verbosity(args.verbose)
    # Fail early if the following commands are not in PATH
    exit_unless_command_exists("nix")
    exit_unless_command_exists("vulnxscan")
    exit_unless_command_exists("csvdiff")
    scanner = FlakeScanner(args.flakeref)
    whitelist = args.whitelist
    if whitelist is not None and not whitelist.exists():
        LOG.warning("Ignoring inaccessible whitelist: %s", whitelist.as_posix())
        whitelist = None
    for target in args.target:
        scanner.scan_target(target[0], nixprs=True, whitelist=whitelist)
    scanner.report(args.outdir)


if __name__ == "__main__":
    main()

################################################################################
