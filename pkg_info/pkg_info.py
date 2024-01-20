import concurrent.futures
from argparse import Namespace
from dataclasses import dataclass, field
from operator import attrgetter
from pathlib import Path
from stat import ST_SIZE
from subprocess import check_output
from typing import Iterable, Optional

from loguru import logger

DEFAULT_MAX_WORKERS = 10

OUTPUT_FORMATS = ["sqlite3", "json", "tsv", "csv"]


@dataclass
class PackageInfo:
    name: str
    version: Optional[str] = ""
    desc: str = ""
    size: int = field(init=False, default=-1)
    size_human: str = field(init=False, default="")
    error: Optional[str] = ""

    def set_size(self, value):
        self.size = value
        self.size_human = f"{self.size/(2**20):.2f} MiB"

    def as_tsv(self):
        return "\t".join(map(str, (self.size_human, self.name, self.version, self.desc, self.error)))


def _get_package_size(package_name: str) -> int:
    logger.info("Checking size of {!r}", package_name)
    size = 0
    for f in map(Path, check_output(["dpkg", "-L", package_name]).decode().splitlines()):
        try:
            if f.is_file() and not f.is_symlink():
                logger.trace("package_name={}, f={}", package_name, f)
                try:
                    size += f.stat()[ST_SIZE]
                except Exception as exc:
                    logger.trace("Unable to get file size of {} ({})", f, exc)
        except Exception as exc:
            logger.warning("Error when accessing {}: {}", f, exc)
    return size


def _update_size(packages: Iterable[PackageInfo], max_workers: int = DEFAULT_MAX_WORKERS) -> Iterable[PackageInfo]:
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(_get_package_size, info.name): info for info in packages}
        for future in concurrent.futures.as_completed(futures):
            info = futures[future]
            try:
                package_size: PackageInfo = future.result()
            except Exception as exc:
                info.error = exc
                logger.error("An error for {}: {}", info.name, exc)
            else:
                info.set_size(package_size)
                logger.success("Got size for {!r}: {}", info.name, info.size)
            yield info


def _get_packages():
    for line in check_output(["dpkg", "-l"]).decode().splitlines():
        logger.trace("line={!r}", line)
        try:
            status, name, version, _, desc = line.strip().split(maxsplit=4)
        except ValueError:
            continue
        if not status == "ii":
            continue
        info = PackageInfo(name, version, desc)
        logger.debug("info={}", info)
        yield info


# def add_size_human(d):
#     d.update(size_human=f"{d['size']/(2**20):.2f} MiB")
#     return d


def show_package_info(args: Namespace) -> None:
    def _include(s: PackageInfo) -> bool:
        return args.INCLUDE.search(s.name) if args.INCLUDE else True

    found_packages = filter(_include, _get_packages())
    package_info = list(_update_size(found_packages, args.max_workers))
    total = PackageInfo("total")
    total.set_size(sum(p.size for p in package_info))
    logger.info("Total is: {}", total.size_human)
    for p in sorted(package_info, key=attrgetter('name')):
        print(p.as_tsv())
    print(total.as_tsv())
