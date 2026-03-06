.PHONY: build clean

build:
	uv sync --group build
	uv run pyinstaller --windowed --name "FixKeynote" --add-data "src/fix_keynote/rebuild_template.applescript:." src/fix_keynote/cli.py -y
	cp -R dist/FixKeynote.app ~/Desktop/FixKeynote.app
	@echo "Build complete! FixKeynote.app has been copied to your Desktop."

clean:
	rm -rf build dist *.spec
