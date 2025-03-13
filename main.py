# Entry point of an application

from views.cli_menu import ShowMenu


def main() -> None:
    """Initialize and start the application."""

    app = ShowMenu()
    app.menu()


if __name__ == "__main__":
    main()