from typing import Dict, Any, List, Optional

class Utils:

    REPLACEMENTS = {
        '_MEDIAID': 'media.id',
        '_TITLE': 'media.metadata.title',
        '_SHORTTITLE': 'media.metadata.titleIgnorePrefix',
        '_SUBTITLE': 'media.metadata.subtitle',
        '_AUTHOR': 'media.metadata.authorName',
        '_AUTHORLF': 'media.metadata.authorNameLF',
        '_NARRATOR': 'media.metadata.narratorName',
        '_SERIES': 'media.metadata.seriesName',
        '_GENRES': 'media.metadata.genres',
        '_PUBLISHYEAR': 'media.metadata.publishedYear',
        '_PUBLISHDATE': 'media.metadata.publishedDate',
        '_PUBLISHER': 'media.metadata.publisher',
        '_DESCRIPTION': 'media.metadata.description',
        '_ISBN': 'media.metadata.isbn',
        '_ASIN': 'media.metadata.asin',
        '_LANGUAGE': 'media.metadata.language',
        '_EXPLICIT': 'media.metadata.explicit',
        '_ABRIDGED': 'media.metadata.abridged',
        '_COVER': 'media.coverPath',
        '_TAGS': 'media.tags',
        '_TRACKS': 'media.numTracks',
        '_FILES': 'media.numAudioFiles',
        '_CHAPTERS': 'media.numChapters',
        '_DURATION': 'media.duration',
        '_SIZE': 'media.size',
        '_FORMAT': 'media.ebookFormat',
    }

    KEYWORDS = ['SELECT', 'FROM', 'WHERE', 'ORDER', 'BY', 'ASC', 'DESC', 'LIMIT', 'OFFSET']

    @staticmethod
    def apply_filter(data: List[Dict[str, Any]], filter: str, exact: bool = False, field: str = 'name') -> List[Dict[str, Any]]:
        field = Utils.replace_shortcuts(field, False)
        if exact:
            return [item for item in data if filter == item.get(field, '')]
        else:
            return [item for item in data if filter in item.get(field, '')]

    @staticmethod
    def print_summary(data: List[Dict[str, Any]], with_guid: bool = False, field: str = 'name', seperator: str = None):
        if data:
            max_name_length = 0
            if with_guid and not seperator:
                max_name_length = max(len(item.get(field, 'Unknown')) for item in data if isinstance(item, dict))
            for item in data:
                if isinstance(item, dict):
                    if with_guid and not seperator:
                        print(f"{item.get(field, 'Unknown'):<{max_name_length}}  {{{item.get('id', 'Unknown')}}}")
                    elif with_guid and seperator:
                        print(f"{item.get(field, 'Unknown')}{seperator}{{{item.get('id', 'Unknown')}}}")
                    else:
                        print(f"{item.get(field, 'Unknown')}")
                elif isinstance(item, str):
                    print(f"{item}")

    @staticmethod
    def print(data: List[Dict[str, Any]], fields=None, seperator: str = None):
        if fields is None:
            fields = ['name', 'id']

        if seperator:
            for item in data:
                print(seperator.join(str(item.get(field, 'Unknown')) for field in fields if field in item))
        else:
            # Calculate max widths in a single pass
            max_widths = [0] * len(fields)
            for item in data:
                for i, field in enumerate(fields):
                    if field in item:
                        max_widths[i] = max(max_widths[i], len(str(item.get(field, 'Unknown'))))

            # Print with alignment
            for item in data:
                parts = []
                for i, field in enumerate(fields):
                    if field in item:
                        parts.append(f"{str(item.get(field, 'Unknown')):<{max_widths[i]}}")
                print("  ".join(parts))

    @staticmethod
    def replace_shortcuts(text: str, quote: bool = True) -> Optional[str]:
        if not text:
            return None

        words = text.split()
        result = []
        unknown = []
        for word in words:
            if word.startswith('_'):
                if word in Utils.REPLACEMENTS:
                    result.append(("\"" if quote else "") + Utils.REPLACEMENTS[word] + ("\"" if quote else ""))
                else:
                    unknown.append(word)
            else:
                result.append(word)
        if unknown:
            raise ValueError(f"Warning: Unknown shortcuts: {', '.join(unknown)}")
        return ' '.join(result)

    @staticmethod
    def has_keywords(text: str) -> bool:
        if not text:
            intersection_set = set(Utils.KEYWORDS).intersection(set(text.upper().split()))
            return len(intersection_set) > 0
        return False

    @staticmethod
    def find_shortcut(text: str) -> Optional[str]:
        for key, value in Utils.REPLACEMENTS.items():
            if text == value:
                return key
        return None
