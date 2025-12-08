from genanki import Model
from config import DEFAULT_CARD_CSS

standard_adveng_model = Model(
        1354561124,
        'AdvEng: Standard',
        fields=[
            {'name': 'Ordinal'},
            {'name': 'Front'},
            {'name': 'Back'},
            {'name': 'SM_Path'}
        ],
        templates=[
            {
                'name': 'AdvEng: Standard Template',
                'qfmt': '{{Front}}',
                'afmt': '{{Front}}<hr id="answer">{{Back}}'
            }
        ],
        css=DEFAULT_CARD_CSS
)

spelling_adveng_model = Model(
    1391062134,
    'AdvEng: Spelling',
    fields=[
        {'name': 'Ordinal'},
        {'name': 'Front'},
        {'name': 'Answer'},
        {'name': 'Extra'},
        {'name': 'SM_Path'}
    ],
    templates=[
        {
            'name': 'AdvEng: Spelling Template',
            'qfmt': '{{Front}}{{type:Answer}}',
            'afmt': '{{Front}}<hr id="answer">{{type:Answer}}{{Extra}}'
        }
    ],
    css=DEFAULT_CARD_CSS
)