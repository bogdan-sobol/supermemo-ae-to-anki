from xml_parser import XMLCollectionParser
from anki_builder import AnkiCollectionBuilder

def main():
    xml_parser = XMLCollectionParser('adveng2018.xml')
    xml_parser.parse_collection_structure()
    xml_parser.define_paths_to_topics_with_items()
    xml_parser.find_xml_item_elements()

    decks_with_items = xml_parser.get_decks_with_items()

    anki_builder = AnkiCollectionBuilder(decks_with_items)
    anki_builder.generate_decks()

    # TODO: make css styling so images fit on the screen properly
    # TODO: clean up memory after parsing items
    # TODO: implement phonetics


if __name__ == '__main__':
    main()