from typing import Optional

import typer
from ffmpeg import FFmpegError  # type: ignore
from rich import print
from rich.console import Console
from typing_extensions import Annotated

from .constants import Constants
from .core import compress_video
from .helpers import delete_path, is_dir, is_ffmpeg_installed, is_file
from .utils import list_unprocessed_videos

app = typer.Typer(rich_markup_mode="rich")
console = Console()


@app.command(epilog=Constants.EPILOG)
def main(
    input: Annotated[
        str,
        typer.Argument(
            show_default=False,
            help=Constants.INPUT_HELP_TEXT,
        ),
    ],
    output: Annotated[
        Optional[str],
        typer.Option(
            show_default=True,
            help=Constants.OUTPUT_HELP_TEXT,
        ),
    ] = None,
    overwrite: Annotated[
        bool,
        typer.Option(
            show_default=True,
            help=Constants.OVERWRITE_HELP_TEXT,
        ),
    ] = False,
    delete_original: Annotated[
        bool,
        typer.Option(
            help=Constants.DELETE_ORIGINAL_HELP_TEXT,
        ),
    ] = False,
    bitrate_factor: Annotated[
        float,
        typer.Option(
            show_default=True,
            help=Constants.BITRATE_FACTOR_HELP_TEXT,
        ),
    ] = 1.0,
    debug: Annotated[
        bool,
        typer.Option(
            help=Constants.DEBUG_HELP_TEXT,
            rich_help_panel=Constants.UTILS_PANEL_TEXT,
        ),
    ] = False,
):
    """
    [green]Simple CLI app[/green] for compressing videos :sparkles:
    """

    if not is_ffmpeg_installed():
        print(Constants.FFMPEG_NOT_INSTALLED)
        raise typer.Exit()

    if is_file(input):
        try:
            console.print(
                "⠹ Processing...",
                f"[{input}]",
                style="green",
                markup=False,
            )
            compress_video(
                input_file=input,
                output_file=output,
                overwrite=overwrite,
                bitrate_factor=bitrate_factor,
            )
            if delete_original:
                delete_path(input)
        except FFmpegError as e:
            error_message: str = e.message
            if debug:
                error_message += f"\n{e.arguments}"
            print(f"[bold red]{error_message}[/bold red]")
        except Exception as e:
            error_message: str = Constants.UNKNOWN_ERROR_MESSAGE  # type: ignore
            if debug:
                error_message += f"\n{e}"
            print(f"[bold red]{error_message}[/bold red]")
        else:
            raise typer.Exit()

    if is_dir(input):
        videos = list_unprocessed_videos(input, Constants.COMPRESSED_SUFFIX)
        if not videos:
            print("[green]There are not videos to process... 🚀[/green]")
            raise typer.Exit()

        for index, video_path in enumerate(videos, start=1):
            try:
                console.print(
                    f"[⠹ Processing...][{index}/{len(videos)}]",
                    f"[{video_path}]",
                    style="green",
                    markup=False,
                )
                compress_video(
                    input_file=video_path,
                    overwrite=overwrite,
                    bitrate_factor=bitrate_factor,
                )
                if delete_original:
                    delete_path(video_path)
            except FFmpegError as e:
                error_message: str = e.message  # type: ignore
                if debug:
                    error_message += f"\n{e.arguments}"
                print(f"[bold red]{error_message}[/bold red]")
            except Exception as e:
                error_message: str = Constants.UNKNOWN_ERROR_MESSAGE  # type: ignore
                if debug:
                    error_message += f"\n{e}"
                print(f"[bold red]{error_message}[/bold red]")
        raise typer.Exit()
