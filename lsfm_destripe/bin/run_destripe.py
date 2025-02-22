#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This sample script will get deployed in the bin directory of the
users' virtualenv when the parent module is installed using pip.
"""

import argparse
import logging
import sys
import traceback

from pathlib import Path
from aicsimageio.writers import OmeTiffWriter
from lsfm_destripe import DeStripe, get_module_version

###############################################################################

log = logging.getLogger()
logging.basicConfig(
    level=logging.INFO, format="[%(levelname)4s:%(lineno)4s %(asctime)s] %(message)s"
)

###############################################################################


class Args(argparse.Namespace):

    DEFAULT_FIRST = 10
    DEFAULT_SECOND = 20

    def __init__(self):
        # Arguments that could be passed in through the command line
        self.first = self.DEFAULT_FIRST
        self.second = self.DEFAULT_SECOND
        self.debug = False
        #
        self.__parse()

    def __parse(self):
        p = argparse.ArgumentParser(
            prog="run_destripe",
            description="run destripe for LSFM images",
        )

        p.add_argument(
            "-v",
            "--version",
            action="version",
            version="%(prog)s " + get_module_version(),
        )
        p.add_argument(
            "--input",
            action="store",
            dest="data_path",
            type=str,
        )
        p.add_argument(
            "--isVertical",
            action="store",
            dest="isVertical",
            default=True,
            type=bool,
        )
        p.add_argument(
            "--dangleOffset",
            action="store",
            dest="angleOffset",
            default=[0],
            type=list,
        )
        p.add_argument(
            "--losseps",
            action="store",
            dest="losseps",
            default=10,
            type=float,
        )
        p.add_argument(
            "--qr",
            action="store",
            dest="qr",
            default=0.5,
            type=float,
        )
        p.add_argument(
            "--resampleRatio",
            action="store",
            dest="resampleRatio",
            default=2,
            type=int,
        )
        p.add_argument(
            "--KGF",
            action="store",
            dest="KGF",
            default=29,
            type=int,
        )
        p.add_argument(
            "--KGFh",
            action="store",
            dest="KGFh",
            default=29,
            type=int,
        )
        p.add_argument(
            "--HKs",
            action="store",
            dest="HKs",
            default=0.5,
            type=float,
        )
        p.add_argument(
            "-s" "--sampling_in_MSEloss",
            action="store",
            dest="sampling_in_MSEloss",
            default=2,
            type=int,
        )
        p.add_argument(
            "--isotropic_hessian",
            action="store",
            dest="isotropic_hessian",
            default=True,
            type=bool,
        )
        p.add_argument(
            "--lambda_tv",
            action="store",
            dest="lambda_tv",
            default=0.5,
            type=float,
        )
        p.add_argument(
            "--lambda_hessian",
            action="store",
            dest="lambda_hessian",
            default=0.5,
            type=float,
        )
        p.add_argument("--inc", action="store", dest="inc", default=16, type=int)
        p.add_argument(
            "--n_epochs", action="store", dest="n_epochs", default=300, type=int
        )
        p.add_argument(
            "--deg",
            action="store",
            dest="deg",
            default=29,
            type=float,
        )
        p.add_argument(
            "--Nneighbors",
            action="store",
            dest="Nneighbors",
            default=16,
            type=int,
        )
        p.add_argument(
            "--fast_GF",
            action="store",
            dest="fast_GF",
            default=False,
            type=bool,
        )
        p.add_argument(
            "--require_global_correction",
            action="store",
            dest="require_global_correction",
            default=True,
            type=bool,
        )
        p.add_argument(
            "-m" "--mask_name",
            action="store",
            dest="mask_name",
            type=str,
        )
        p.add_argument(
            "--debug",
            action="store_true",
            dest="debug",
            help=argparse.SUPPRESS,
        )
        p.parse_args(namespace=self)


###############################################################################


def main():
    try:
        args = Args()
        dbg = args.debug

        input = Path(args.input)
        if input.is_file():
            exe = DeStripe(
                input,
                args.isVertical,
                args.angleOffset,
                args.losseps,
                args.qr,
                args.resampleRatio,
                args.KGF,
                args.KGFh,
                args.HKs,
                args.sampling_in_MSELoss,
                args.isotropic_hessian,
                args.lambda_tv,
                args.lambda_hessian,
                args.inc,
                args.n_epochs,
                args.Nneighbors,
                args.deg,
                args.require_global_correction,
                args.fast_GF,
                args.mask_name,
            )
            out = exe.train()
            OmeTiffWriter.save(out, args.out_path, dim_order="ZYX")
        elif input.is_dir():
            filenames = sorted(input.glob("*"))
            for fn in filenames:
                exe = DeStripe(
                    fn,
                    args.isVertical,
                    args.angleOffset,
                    args.losseps,
                    args.qr,
                    args.resampleRatio,
                    args.KGF,
                    args.KGFh,
                    args.HKs,
                    args.sampling_in_MSELoss,
                    args.isotropic_hessian,
                    args.lambda_tv,
                    args.lambda_hessian,
                    args.inc,
                    args.n_epochs,
                    args.Nneighbors,
                    args.deg,
                    args.require_global_correction,
                    args.fast_GF,
                    args.mask_name,
                )
                out = exe.train()
                OmeTiffWriter.save(
                    out, Path(args.out_path) / f"{fn.stem}_out.tiff", dim_order="ZYX"
                )

    except Exception as e:
        log.error("=============================================")
        if dbg:
            log.error("\n\n" + traceback.format_exc())
            log.error("=============================================")
        log.error("\n\n" + str(e) + "\n")
        log.error("=============================================")
        sys.exit(1)


###############################################################################
# Allow caller to directly run this module (usually in development scenarios)

if __name__ == "__main__":
    main()
