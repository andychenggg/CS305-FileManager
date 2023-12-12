class HTMLManager:
    def __init__(self):
        with open("html_package/page.html", "r") as file:
            self.html_template = file.read()
        self.directories = []
        self.files = []
        self.current_path = '/'
        self.back_path = '/'

    def add_directory(self, name):
        self.directories.append(name)

    def add_file(self, name):
        self.files.append(name)

    def generate_html(self) -> str:
        # Generate the HTML for the directories and files
        directory_html = '\n'.join(f'<li><a href="{directory}">\n'
                                   f'<svg class="icon" aria-hidden="true">\n'
                                   f'    <use xlink:href="#icon-folder"></use>\n'
                                   f'</svg>\n'
                                   f'    <span>{directory}</span></a></li>\n'
                                   for directory in self.directories)
        #
        directory_html = f'<li><a href="{self.current_path}/"\n' \
                         '    <svg class="icon" aria-hidden="true">\n' \
                         '        <use xlink:href="#icon-folder"></use>\n' \
                         '    </svg>\n' \
                         '    <span>.</span></a></li>\n' + directory_html
        directory_html = f'<li><a href="{self.back_path}/"\n' \
                         '    <svg class="icon" aria-hidden="true">\n' \
                         '        <use xlink:href="#icon-folder"></use>\n' \
                         '    </svg>\n' \
                         '    <span>..</span></a></li>\n' + directory_html
        file_html = '\n'.join(f'<li><a href="{file}">\n'
                              f'<svg class="icon" aria-hidden="true">\n'
                              f'    <use xlink:href="#icon-file"></use>\n'
                              f'</svg>\n'
                              f'    <span>{file}</span></a></li>\n'
                              for file in self.files)
        # Replace the placeholder comments with the actual directory and file HTML
        html = self.html_template.replace('<!-- Directories will go here -->', directory_html)
        html = html.replace('<!-- Files will go here -->', file_html)

        return html
