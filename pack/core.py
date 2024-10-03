import json
import re

from ffmpeg import FFmpeg, Progress  # type: ignore
from rich.progress import Progress as ProgressBar

from .constants import BitrateUnit, Constants
from .helpers import add_affixes


def _get_bitrate(path: str, unit: BitrateUnit = BitrateUnit.KBPS) -> tuple[int, int]:
    """
    Get the bitrate values of a video [bitrate video, bitrate audio] in BitrateUnit.
    Args:
        path (str): The path to the video file.
        unit (BitrateUnit): The unit to use for the bitrate values. Default is BitrateUnit.KBPS.

    Returns:
        tuple[int, int]: A tuple containing the bitrate values for the video file in the specified unit.
    """
    ffprobe = FFmpeg(executable="ffprobe").input(
        path,
        print_format="json",
        show_streams=None,
    )
    media = json.loads(ffprobe.execute())
    bv = int(media["streams"][0]["bit_rate"])
    ba = int(media["streams"][1]["bit_rate"])
    return (int(bv / unit.value), int(ba / unit.value))


def _get_duration(path: str) -> float:
    """
    Get the duration of a video file using FFmpeg.
    Args:
        path (str): The path to the video file.

    Returns:
        float: The duration of the video in seconds.
    """
    ffprobe = FFmpeg(executable="ffprobe").input(
        path,
        print_format="json",
        show_streams=None,
    )
    media = json.loads(ffprobe.execute())
    duration = media["streams"][0]["duration"]
    return float(duration)


def _get_progress_percentage(progress: Progress, duration: float) -> float:
    """
    Calculate the progress percentage of a video file using FFmpeg.

    Args:
        progress (Progress): The progress object returned by FFmpeg.
        duration (float): The duration of the source video file in seconds.

    Returns:
        float: The progress percentage as a float between 0 and 100.
    """
    current_time = progress.time.total_seconds()
    return round(current_time / duration * 100)


def compress_video(
    input_file: str,
    output_file: str | None = None,
    overwrite: bool = False,
    bitrate_factor: float = 1.0,
):
    """
    Compress a video file using FFmpeg and display the progress in a terminal.

    Args:
        input_file (str): The path to the input video file.
        output_file (str | None): The path to the output file. If not provided,
                                  a suffix '_compressed' will be added to the input file name.
        overwrite (bool): If True, overwrites the output file if it already exists.
                         If False, the process will stop if the output file exists.
    """

    if output := output_file:
        pass
    else:
        output = add_affixes(input_file, suffix=Constants.COMPRESSED_SUFFIX)

    bv, ba = _get_bitrate(input_file, BitrateUnit.KBPS)

    extra_options: dict[str, str] = {}

    if bitrate_factor < 1.0:
        extra_options["b:v"] = f"{bv*bitrate_factor}k"
        extra_options["b:a"] = f"{ba*bitrate_factor}k"

    ffmpeg = (
        FFmpeg()
        .option("y" if overwrite else "n")
        .input(input_file)
        .output(
            output,
            extra_options,
            vcodec="h264",
            acodec="aac",
        )
    )

    with ProgressBar() as progress_bar:
        task = progress_bar.add_task("", total=100, completed=0)

        duration = _get_duration(input_file)

        @ffmpeg.on("progress")
        def on_progress(progress: Progress):
            percentage = _get_progress_percentage(progress, duration)
            progress_bar.update(task, completed=percentage)

        @ffmpeg.on("completed")
        def on_completed():
            progress_bar.update(task, completed=100)

        @ffmpeg.on("stderr")
        def on_stderr(line):
            # This pattern checks for errors like "File 'input_compressed.mp4' already exists."
            # Such errors may occur on Linux, but not on macOS, even when using the "-n" flag with ffmpeg.
            # For more context, refer to: https://github.com/ivansaul/compress-video/pull/3
            pattern = r".*File.*already exists.*"
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                progress_bar.update(task, completed=100)

        ffmpeg.execute()
