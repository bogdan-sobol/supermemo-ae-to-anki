import os
import shutil
import random
import genanki
import anki_models
from config import CORE_DECK_NAME

class AnkiCollectionBuilder:
    def __init__(self, decks_with_items):
        self.decks_with_items = decks_with_items

        self.media_counter = 0 # gives filenames unique ids
        self.copied_media: dict[str, dict] = {}

        self.decks = []
        self.paths_to_used_media = []

        self.FILENAME_CHAR_LIMIT = 100

        main_deck = genanki.Deck(
            self.get_unquie_id(),
            CORE_DECK_NAME
        )
        self.decks.append(main_deck)
    

    def process_filename(self, filename: str):
        special_chars = ['.', ',', '-', '?', '(', ')', ':', '|', '/', '\\', '*', '"', '\'', '<', '>']

        new_filename = filename.lower()
        for special_char in special_chars:
            new_filename = new_filename.replace(special_char, ' ')

        new_filename_split = new_filename.split()
        new_filename = '_'.join(new_filename_split)
        
        counter = str(self.media_counter)
        new_filename = f'AdvEng_{counter.zfill(5)}_{new_filename}'

        new_filename = new_filename[:self.FILENAME_CHAR_LIMIT]

        self.media_counter += 1

        return new_filename


    def make_item_media_copies(self, item, branch_name: str):
        """Copies media to the tmp folder with proper filenames"""
        updated_item = item

        for index, media in enumerate(item[branch_name]):
            # avoid creating duplicates
            copied_file = self.copied_media.get(media['file_path'], None)

            if copied_file is not None:
                updated_item[branch_name][index]['filename'] = copied_file['filename']
                updated_item[branch_name][index]['file_path'] = copied_file['file_path']
                continue

            _, file_ext = os.path.splitext(media['file_path'])

            updated_filename = self.process_filename(media['filename'])
            updated_filename += file_ext

            # copy media to the tmp folder
            path_to_tmp_folder = os.path.join(os.getcwd(), 'tmp')
            shutil.copy(media['file_path'], path_to_tmp_folder)

            path_to_copy = os.path.join(path_to_tmp_folder, os.path.basename(media['file_path']))

            # renames the copy
            updated_path = os.path.join(path_to_tmp_folder, updated_filename)
            shutil.move(path_to_copy, updated_path)

            self.copied_media[media['file_path']] = {
                'file_path': updated_path,
                'filename': updated_filename
            }

            updated_item[branch_name][index]['file_path'] = updated_path
            updated_item[branch_name][index]['filename'] = updated_filename
        
        return updated_item


    def process_item_media(self, item):
        updated_item = self.make_item_media_copies(item, 'images')
        updated_item = self.make_item_media_copies(updated_item, 'sounds')

        return updated_item

    @staticmethod
    def get_unquie_id():
        return random.randrange(1 << 30, 1 << 31)


    def make_standard_note(self, item):
        note = genanki.Note(
            model=anki_models.standard_adveng_model,
            fields=[
                item['ordinal']
            ]
        )

        front = item['front']
        back = item['back']
        
        for index in range(len(item['sounds'])):
            sound = item['sounds'][index]

            ankified_sound = f'[sound:{sound['filename']}]'
            ankified_sound = '<br>' + ankified_sound

            if sound['is_back_only']:
                back += ankified_sound
            else:
                front += ankified_sound

            self.paths_to_used_media.append(sound['file_path'])

        for index in range(len(item['images'])):
            image = item['images'][index]

            ankified_image = f'<img src="{image['filename']}">'
            ankified_image = '<br>' + ankified_image

            if image['is_back_only']:
                back += ankified_image
            else:
                front += ankified_image

            self.paths_to_used_media.append(image['file_path'])

        note.fields.append(front)
        note.fields.append(back)
        note.fields.append(item['sm_path'])

        return note


    def make_spelling_note(self, item):
        note = genanki.Note(
            model=anki_models.spelling_adveng_model,
            fields=[
                item['ordinal']
            ]
        )

        front = item['front']        
        extra = ''
        
        for index in range(len(item['sounds'])):
            sound = item['sounds'][index]

            ankified_sound = f'[sound:{sound['filename']}]'
            ankified_sound = '<br>' + ankified_sound

            if sound['is_back_only']:
                extra += ankified_sound
            else:
                front += ankified_sound

            self.paths_to_used_media.append(sound['file_path'])

        for index in range(len(item['images'])):
            image = item['images'][index]

            ankified_image = f'<img src="{image['filename']}">'
            ankified_image = '<br>' + ankified_image

            if image['is_back_only']:
                extra += ankified_image
            else:
                front += ankified_image

            self.paths_to_used_media.append(image['file_path'])

        note.fields.append(front)
        note.fields.append(item['back'])
        note.fields.append(extra)
        note.fields.append(item['sm_path'])

        return note


    def item_to_note(self, item, deck_name):
        if deck_name == 'Spelling':
            note = self.make_spelling_note(item)
        else:
            note = self.make_standard_note(item)

        return note


    def generate_decks(self):
        for deck_name, list_of_items in self.decks_with_items.items():
            deck = genanki.Deck(
                self.get_unquie_id(),
                f'{CORE_DECK_NAME}::{deck_name}'
            )
            self.decks.append(deck)

            for item in list_of_items:
                item = self.process_item_media(item)

                note = self.item_to_note(item, deck_name)

                deck.add_note(note)

        package = genanki.Package(self.decks)

        # remove path duplicates
        self.paths_to_used_media = list(set(self.paths_to_used_media))

        for path_to_media in self.paths_to_used_media:
            package.media_files.append(path_to_media)

        package.write_to_file("output/output.apkg")
