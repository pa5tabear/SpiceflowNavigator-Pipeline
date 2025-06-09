from .workflow import WorkflowManager


def main():
    manager = WorkflowManager("https://example.com/feed")
    manager.run()


if __name__ == "__main__":
    main()
