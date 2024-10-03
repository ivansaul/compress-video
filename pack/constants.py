from enum import Enum


class Constants:
    EPILOG = "Made with [red]:heart:[/red] by [blue]@ivansaul[/blue]"
    INPUT_HELP_TEXT = "The input can be a file or a directory. If a directory is provided, all videos in the directory will be processed."
    OUTPUT_HELP_TEXT = "The output file to save the compressed video."
    DEBUG_HELP_TEXT = "Enable debugging."
    DELETE_ORIGINAL_HELP_TEXT = "Delete the original video after compression."
    OVERWRITE_HELP_TEXT = "Overwrite existing output file."
    BITRATE_FACTOR_HELP_TEXT = "The bitrate factor [0.0 <1.0] to use for the output video. Higher values will result in higher quality but higher file sizes."
    UTILS_PANEL_TEXT = "Customization and Utils"
    ERROR_MESSAGE = "An error occurred while compressing the video 💥."
    UNKNOWN_ERROR_MESSAGE = "An unknown error occurred 💥."
    FFMPEG_NOT_INSTALLED = "[bold red]ffmpeg is not installed! 💥[/bold red]"
    SUPPORTED_VIDEO_FORMATS = (".mp4", ".mov", ".avi", ".mkv", ".webm")
    COMPRESSED_SUFFIX = "_compressed"
    FFMPEG_FILE_ALREADY_EXISTS_ERROR_PATTERN = r".*File.*already exists.*"


class BitrateUnit(Enum):
    """
    Enum for bitrate units.
    - bps: bits per second
    - kbps: kilobits per second
    - mbps: megabits per second
    """

    BPS = 1
    KBPS = 1000
    MBPS = 1000000
