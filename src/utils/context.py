import os


class Context:
    current_dir = os.path.dirname(os.path.abspath(__file__))

    class _Context:
        def __init__(self, input_folder, output_folder):
            self.INPUT = os.path.join(Context.current_dir, "..", input_folder)
            self.OUTPUT = os.path.join(Context.current_dir, "..", output_folder)


# Create class variables and assign their metadata
Context.MAIN = Context._Context(input_folder="models", output_folder="data")
Context.TEST_EVENT = Context._Context(
    input_folder="tests/data/events/input", output_folder="tests/data/events/output"
)
Context.TEST_CONTRACT = Context._Context(
    input_folder="tests/data/events/input", output_folder="tests/data/events/output"
)
