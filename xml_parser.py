import xml.etree.ElementTree as ET

class XMLCollectionParser:
    def __init__(self, path_to_xml: str):
        # TODO: add xml path validation
        tree = ET.parse(path_to_xml)
        root = tree.getroot()

        print(f'root name: {root.tag}')
        if root.tag != 'SuperMemoCollection':
            print("Bad XML")
            exit()

        self.collection_element = root.find('SuperMemoElement')

        if self.collection_element is None:
            print('Couldnt find collection element')
            exit()


    def parse_collection_structure(self):
        self.core_categories = {}

        for sm_element in self.collection_element.findall('SuperMemoElement'):
            el_type = sm_element.find('Type')
            if el_type is None:
                continue
            el_type = el_type.text

            if el_type != 'Topic':
                continue

            el_title = sm_element.find('Title')
            if el_title is None:
                continue
            el_title = el_title.text

            self.core_categories[el_title] = {
                'deck_name': el_title,
                'xml_element': sm_element,
                'paths_to_nodes': []
            }
        
        # TMP
        print('\ncore categories:')
        for category in self.core_categories.values():
            print(category['deck_name'])

    @staticmethod
    def find_paths_to_topics_with_items(xml_element, path_to_topic: str):
        paths = []

        # find all topic_element children of the xml element
        topics = []
        this_topic_has_items = False

        for sm_element in xml_element.findall('SuperMemoElement'):
            el_type = sm_element.find('Type')

            if el_type is None:
                continue

            if el_type.text == 'Topic':
                topics.append(sm_element)
            
            elif el_type.text == 'Item':
                this_topic_has_items = True

        # if no topics inside = it's a node with items
        if not topics:
            return [path_to_topic]
        
        for topic_element in topics:
            el_title = topic_element.find('Title')

            if el_title is None:
                continue
            
            topic_name = el_title.text

            updated_path_to_topic = f'{path_to_topic}::{topic_name}'
            
            paths_to_topics_with_items = XMLCollectionParser.find_paths_to_topics_with_items(
                topic_element, updated_path_to_topic
            )

            if paths_to_topics_with_items is None:
                continue

            for path in paths_to_topics_with_items:
                if path not in paths:
                    paths.append(path)

        # if current topic element has items
        if this_topic_has_items:
            paths.append(path_to_topic)

        return paths


    def define_paths_to_topics_with_items(self):
        for category in self.core_categories.values():
            category_name = category['deck_name'] # alias
            paths_to_nodes = self.find_paths_to_topics_with_items(category['xml_element'], category_name)

            self.core_categories[category_name]['paths_to_nodes'] = paths_to_nodes

        # # TMP
        # print('\npaths to nodes:\n')
        # for category in self.core_categories.values():
        #     print(f'deck name: {category['deck_name']}')

        #     for path in category['paths_to_nodes']:
        #         print(path)
        #     print()


    def find_topic_element_using_path(self, path: str):
        path_elements = path.split('::')

        # follow the path
        element_pointer = self.collection_element
        for topic_name in path_elements:
            for sm_element in element_pointer.findall('SuperMemoElement'):
                el_type = sm_element.find('Type')
                if el_type is None:
                    continue

                el_title = sm_element.find('Title')
                if el_title is None:
                    continue

                if el_type.text != 'Topic':
                    continue
                
                if el_title.text == topic_name:
                    element_pointer = sm_element
                    break
            # TMP
            else:
                print('\nCouldnt follow the path...')
                exit()

        return element_pointer


    def find_xml_item_elements(self):
        self.paths_to_xml_items: dict[str, list] = {}

        all_paths_to_topics_with_items = []
        for category in self.core_categories.values():
            for path in category['paths_to_nodes']:
                all_paths_to_topics_with_items.append(path)

        for path_to_topic_with_items in all_paths_to_topics_with_items:
            topic_element = self.find_topic_element_using_path(path_to_topic_with_items)

            # edge case: not all topics with items are nodes
            topics_inside_topic = []

            for sm_element in topic_element.findall('.//SuperMemoElement'):
                el_type = sm_element.find('Type')
                if el_type is None:
                    continue

                if el_type.text == 'Item':
                    if path_to_topic_with_items in self.paths_to_xml_items:
                        self.paths_to_xml_items[path_to_topic_with_items].append(sm_element)
                    else:
                        self.paths_to_xml_items[path_to_topic_with_items] = [sm_element]

                elif el_type.text == 'Topic':
                    topics_inside_topic.append(sm_element)

            if len(topics_inside_topic) == 0:
                continue

            for topic_element in topics_inside_topic:
                for sm_element in topic_element.findall('.//SuperMemoElement'):
                    el_type = sm_element.find('Type')

                    if el_type is None:
                        continue

                    if el_type.text == 'Item':
                        if sm_element in self.paths_to_xml_items[path_to_topic_with_items]:
                            self.paths_to_xml_items[path_to_topic_with_items].remove(sm_element)

    # TMP
    def count_item_elements(self):
        # total items in the collection: 44850
        # advanced english items = 39601
        # grammar items = 2573
        # pronunciation items = 1959
        # spelling items = 717

        total_count = 0

        for list_of_items in self.paths_to_xml_items.values():
            total_count += len(list_of_items)
            
        print(f'\ntotal: {total_count}')

        categories_count: dict[str, int] = {}
        # TODO: remove
        # for category in self.core_categories.values():
        #     categories_count[category['deck_name']] = 0

        for path_to_items, list_of_items in self.paths_to_xml_items.items():
            item_category_name = path_to_items.split('::').pop(0)
            item_count = len(list_of_items)

            if item_category_name in categories_count:
                categories_count[item_category_name] += item_count
            else:
                categories_count[item_category_name] = item_count

        # TMP
        print('\ncategories count:')
        for category_name, item_count in categories_count.items():
            print(f'{category_name}: {item_count}')
        print()

    # TMP
    @staticmethod
    def count_items(deck_with_items):
        print()
        total_count = 0
        for deck_name, list_of_items in deck_with_items.items():
            print(f'{deck_name}: {len(list_of_items)}')
            total_count += len(list_of_items)
        
        print(f'\ntotal count: {total_count}')

    # TMP
    def find_duplicates(self):
        founded_item_ids = []
        for list_of_items in self.paths_to_xml_items.values():
            for sm_element in list_of_items:
                founded_item_ids.append(sm_element.find('ID').text)

        print(f'founded IDs count: {len(founded_item_ids)}')
        
        unique_ids = []
        duplicate_ids = []

        for item_id in founded_item_ids:
            if item_id in unique_ids:
                duplicate_ids.append(item_id)
            else:
                unique_ids.append(item_id)

        print(f'founded duplciates {len(duplicate_ids)}')

        if len(duplicate_ids) == 0:
            exit()

        print('\nduplicate items:')
        for sm_element in self.collection_element.findall('.//SuperMemoElement'):
            el_type = sm_element.find('Type')
            if el_type is None:
                continue
            el_type = el_type.text

            if el_type != 'Item':
                continue

            el_id = sm_element.find('ID')
            if el_id is None:
                continue
            el_id = el_id.text

            if el_id not in duplicate_ids:
                continue

            el_content = sm_element.find('Content')
            if el_content is None:
                continue

            print(f'ID: {el_id}')

            print(f'Q: {el_content.find('Question').text}')            
            print(f'A: {el_content.find('Answer').text}')
            print()

    # TMP
    def find_missing_elements_by_id(self):
        founded_item_ids = {}
        for list_of_items in self.paths_to_xml_items.values():
            for sm_element in list_of_items:
                founded_item_ids[sm_element.find('ID').text] = sm_element

        print(f'founded IDs count: {len(founded_item_ids)}')
        
        all_item_ids = {}

        for sm_element in self.collection_element.findall('.//SuperMemoElement'):
            el_type = sm_element.find('Type')

            if el_type is None:
                continue

            if el_type.text == 'Item':
                all_item_ids[sm_element.find('ID').text] = sm_element

        print(f'all IDs count: {len(all_item_ids)}')

        not_founded_ids = []
        for el_id in all_item_ids.keys():
            if el_id not in founded_item_ids.keys():
                not_founded_ids.append(el_id)

        print(f'not founded ids count: {len(not_founded_ids)}')

        print('\nnot founded items:')
        for el_id in not_founded_ids:
            not_founded_item = all_item_ids[el_id]
            el_content = not_founded_item.find('Content')
            print(f'ID: {el_id}')

            question = el_content.find('Question')

            if question is None:
                print('Q: None')
            else:
                print(f'Q: {question.text}')

            answer = el_content.find('Answer')

            if answer is None:
                print('A: None')
            else:
                print(f'A: {answer.text}')
            print()

    @staticmethod
    def parse_item_media(xml_media_elements):
        media = []

        for media_element in xml_media_elements:
            file_path = media_element.find('URL').text
            filename = media_element.find('Name').text

            is_back_only = media_element.find('Answer')

            # if no such XML tag = media is shown on the front (default)
            if is_back_only is not None:
                is_back_only = True
            else:
                is_back_only = False
            
            media.append({
                'file_path': file_path,
                'filename': filename,
                'is_back_only': is_back_only
            })
        
        return media


    def parse_item_element(self, item_element, sm_path_to_item: str):
        if item_element is None:
            return None
        
        ordinal = item_element.find('Ordinal')
        if ordinal is None:
            return None
        ordinal = ordinal.text
        
        item_content = item_element.find('Content')
        if item_content is None:
            return None
        
        front = item_content.find('Question')
        if front is None:
            return None
        front = front.text

        back = item_content.find('Answer')
        if back is None:
            return None
        back = back.text

        sound_elements = item_content.findall('Sound')
        sounds = self.parse_item_media(sound_elements)

        image_elements = item_content.findall('Image')
        images = self.parse_item_media(image_elements)

        parsed_item = {
            'ordinal': ordinal,
            'front': front,
            'back': back,
            'sounds': sounds,
            'images': images,
            'sm_path': sm_path_to_item
        }

        return parsed_item


    def get_decks_with_items(self):
        decks_with_items: dict[str, list] = {}

        # category names and deck names are the same
        for deck_name in self.core_categories.keys():
            decks_with_items[deck_name] = []

        for sm_path_to_item, list_of_items in self.paths_to_xml_items.items():
            deck_name = sm_path_to_item.split('::').pop(0)

            for xml_item_element in list_of_items:
                parsed_item = self.parse_item_element(xml_item_element, sm_path_to_item)

                if parsed_item is None:
                    continue

                decks_with_items[deck_name].append(parsed_item)

        return decks_with_items
