# supermemo-ae-to-anki

This Python script converts the "Advanced English" collection from a SuperMemo XML export into an Anki-compatible package (`.apkg`). It preserves the hierarchical deck structure, card content, and associated media files (images and sounds).

## Features

*   **Parses SuperMemo XML:** Accurately reads and interprets the structure of `SuperMemoCollection` XML exports.
*   **Hierarchical Decks:** Recreates the SuperMemo topic hierarchy as a main deck with corresponding sub-decks in Anki.
*   **Media Handling:** Processes, renames, and bundles all referenced image and sound files into the final Anki package.
*   **Custom Note Types:** Generates two distinct Anki note types:
    *   **Standard:** A basic front/back card for most items.
    *   **Spelling:** A card with a type-in field for spelling-focused items.
*   **Content Preservation:** Migrates question text, answer text, and embedded media, assigning them to the correct card fields.

## How It Works

The conversion process is handled in two main stages:

1.  **Parsing (`xml_parser.py`):** The script first reads the `.xml` file to map out the collection's structure. It recursively traverses the topic tree to locate all nodes containing flashcard "Items" and extracts the content for each card (question, answer, media references, etc.).

2.  **Building (`anki_builder.py`):** Using the parsed data, the script builds the Anki package with the `genanki` library.
    *   It creates a deck for each main category found in the XML.
    *   It converts each SuperMemo item into an Anki note using the appropriate model (Standard or Spelling).
    *   It copies all referenced media files, sanitizes their filenames to prevent conflicts, and embeds the correct `<img>` and `[sound]` tags into the Anki cards.
    *   Finally, it bundles all decks, notes, and media into a single `output.apkg` file.

## Requirements

*   Python 3.x
*   `genanki` library
*   An XML export of your SuperMemo collection (e.g., `adveng2018.xml`).
*   The associated `elements` folder from SuperMemo, containing all media files referenced in the XML.

## Usage

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/bogdan-sobol/supermemo-ae-to-anki.git
    cd supermemo-ae-to-anki
    ```

2.  **Install dependencies:**
    ```sh
    pip install genanki
    ```

3.  **Prepare your files:**
    *   Place your SuperMemo XML export in the root directory and name it `adveng2018.xml`.
    *   Place the entire `elements` folder from your SuperMemo collection into the root directory. The script relies on the file paths within this folder matching the paths in the XML file.

4.  **Run the script:**
    ```sh
    python main.py
    ```

5.  **Import to Anki:**
    *   The script will generate `output/output.apkg`.
    *   Open Anki and go to `File > Import...` to import the new package.

## Configuration

You can customize the output by modifying the following files:

*   **`config.py`**: Change the `CORE_DECK_NAME` variable to set a different name for the main Anki deck. You can also edit `DEFAULT_CARD_CSS` to apply custom styling to your cards.
*   **`anki_models.py`**: Modify the card templates (`qfmt`, `afmt`) and fields for the "Standard" and "Spelling" note types.

## License

This project is licensed under the GNU General Public License v3.0. See the `LICENSE` file for more details.
