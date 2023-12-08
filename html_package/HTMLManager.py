class HTMLManager:
    def __init__(self):

        with open("html_package/page.html", "r") as file:
            self.html_template = file.read()
        self.directories = []
        self.files = []

    def add_directory(self, name):
        self.directories.append(name)

    def add_file(self, name):
        self.files.append(name)

    def generate_html(self) -> str:
        directory_html = '\n'.join(f'<p>{directory}</p>' for directory in self.directories)
        file_html = '\n'.join(f'<li>{file}</li>' for file in self.files)

        # Replace the placeholder comments with the actual directory and file HTML
        html = self.html_template.replace('<!-- Directories will go here -->', directory_html)
        html = html.replace('<!-- Files will go here -->', file_html)

        return html
