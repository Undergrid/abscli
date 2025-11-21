import argparse
import shutil
import sys
from typing import Optional, List

from _duckdb import BinderException

from AudioBookShelfClient import *

_VERSION = "0.0.2"

class StripQuotesAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if isinstance(values, str):
            values = values.strip("'\"")
        elif isinstance(values, list):
            values = [v.strip("'\"") for v in values]
        setattr(namespace, self.dest, values)


def main():
    args = setup_parser()
    abscli(args)

def setup_parser():
    common_parser = argparse.ArgumentParser(add_help=False, exit_on_error=True)
    common_parser.add_argument("--server", type=str, required=True, help="Path to config file")

    lib_opt_parser = argparse.ArgumentParser(add_help=False, exit_on_error=True, parents=[common_parser])
    lib_opt_parser_lib = lib_opt_parser.add_mutually_exclusive_group(required=False)
    lib_opt_parser_lib.add_argument("--library", type=str, help="Name of the library to query")
    lib_opt_parser_lib.add_argument("--all", action='store_true', help="Run the command on all libraries")

    lib_req_parser = argparse.ArgumentParser(add_help=False, exit_on_error=True, parents=[common_parser])
    lib_req_parser_lib = lib_req_parser.add_mutually_exclusive_group(required=True)
    lib_req_parser_lib.add_argument("--library", type=str, help="Name of the library to query")
    lib_req_parser_lib.add_argument("--all", action='store_true', help="Run the command on all libraries")

    parser = argparse.ArgumentParser(description="abscli is an unofficial command line AudioBookShelf API Client", exit_on_error=True)
    parser.add_argument("--version", action="version", version=f"%(prog)s {_VERSION}")
    subparsers = parser.add_subparsers(dest="command")

    list_parser = subparsers.add_parser("list", help="List libraries, series, collections, or books", parents=[lib_opt_parser])
    list_parser.add_argument("type", type=str, choices=["libraries", "series", "collections", "books", "genres"])
    list_parser.add_argument("--seperator", type=str, required=False, help="Seperator character(s) used in output", default=None, action=StripQuotesAction)
    list_parser.add_argument("--with-id", action='store_true', required=False, help="Include ID in output (genres do not have an ID)", default=False)
    filter_group = list_parser.add_argument_group("filter")
    filter_group.add_argument("--filter", type=str, required=False, help="Apply a filter", metavar='VALUE')
    filter_group.add_argument("--exact", action='store_true', required=False, help="Perform an exact match", default=False)
    filter_group.add_argument("--field", type=str, required=False, help="When filtering books, specify the field to match", action=StripQuotesAction)

    search_parent_parser = argparse.ArgumentParser(parents=[lib_req_parser], add_help=False)
    search_parent_parser_group = search_parent_parser.add_argument_group("searching")
    search_parent_parser_group.add_argument("--where", type=str, required=True, help="SQL Like Where clause", metavar='CLAUSE')
    search_parent_parser_group.add_argument("--sort", type=str, required=False, help="Field to sort results by")
    search_parent_parser_group.add_argument("--direction", type=str, required=False, help="Sort Direction", default="asc", choices=["asc", "desc"])
    search_parent_parser_group.add_argument("--display", type=str, required=False, nargs="+", help="Fields to display", default=None, metavar='COLUMN')

    search_parser = subparsers.add_parser("search", help="Search for books", parents=[search_parent_parser])

    create_parser = subparsers.add_parser("create", help="Create a new item", parents=[search_parent_parser])
    create_parser.add_argument("type", type=str, choices=['collection'])
    create_parser.add_argument("--name", type=str, required=True, help="Name of the collection to create")
    create_parser.add_argument("--dryrun", action='store_true', required=False, help="Dry run, do not create the collection", default=False)

    update_parser = subparsers.add_parser("update", help="Update or Create an item", parents=[search_parent_parser])
    update_parser.add_argument("type", type=str, choices=['collection'])
    update_parser.add_argument("--name", type=str, required=True, help="Name of the collection to add the books to")
    update_parser.add_argument("--dryrun", action='store_true', required=False, help="Dry run, do not update the collection", default=False)

    info_parser = subparsers.add_parser("info", help="Get information about the server", parents=[lib_req_parser])
    info_parser.add_argument("type", type=str, choices=["fields"])

    args = parser.parse_args()
    return args

class abscli:
    def __init__(self, args):
        self.config = Config(args.server)
        self.libraries = None
        self.collections = None
        self.collections_library_id = None
        self.series = None
        self.books = None
        self.books_library_id = None
        self.filters = None
        self.filters_library_id = None

        try:
            match args.command:
                case "list":
                    self.perform_list(args)
                case "search":
                    self.perform_search(args)
                case "info":
                    self.perform_info(args)
                case "create":
                    self.perform_create(args)
                case "update":
                    self.perform_update(args)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
#        except AttributeError as e:
#            print(f"Error: A required property has not been found on a data object, it is possible an update has changed the data structure in audiobookself ", file=sys.stderr)
#            print(f"Required property: {e.name}", file=sys.stderr)
#            print(f"Available properties: {', '.join([item for item in dir(e.obj) if not item.startswith('_')])}", file=sys.stderr)
        except BinderException as e:
            print(f"Error: {e}", file=sys.stderr)

    def __load_libraries(self):
        if self.libraries is None:
            self.libraries = Libraries(self.config.url, self.config.api_key)

    def __load_collections(self, library_id: str):
        if library_id and self.collections_library_id != library_id:
            self.collections = None
            self.collections_library_id = library_id

        if self.collections is None:
            self.collections = Collections(self.config.url, self.config.api_key, library_id, self.libraries)

    def __load_books(self, library_id: str):
        if library_id and self.books_library_id != library_id:
            self.books = None
            self.series = None
            self.books_library_id = library_id

        if self.books is None:
            self.books = Books(self.config.url, self.config.api_key, library_id)

    def __load_series(self):
        if self.books is not None and self.series is None:
            self.series = Series(self.books)

    def __load_filters(self, library_id: str):
        if library_id and self.filters_library_id != library_id:
            self.filters = None
            self.filters_library_id = library_id

        if self.filters is None:
            self.filters = Filters(self.config.url, self.config.api_key, library_id)

    def perform_list(self, args):
        self.__load_libraries()
        libraries = None
        if args.all:
            libraries = self.libraries.get_all()
        elif args.library:
            library = self.libraries.get_by_name(args.library)
            if not library:
                print(f"Error: Library '{args.library}' not found", file=sys.stderr)
                sys.exit(1)
            libraries = [library] if library else None

        if libraries:
            for library in libraries:
                if args.all:
                    print(f"\n\nLibrary: {library.name}")
                    print("-" * shutil.get_terminal_size().columns)
                self.__do_list(args, library)
        else:
            self.__do_list(args)

    def __do_list(self, args, library: Optional[Library] = None):
        data = None
        with_id = args.with_id
        fields: Optional[List[str]] = ['name', "id" if with_id else None]
        filter_field = 'name'

        match args.type:
            case "libraries":
                data = self.libraries.get_all_summary()
            case "series":
                self.__load_filters(library.id)
                data = self.filters.get_series()
            case "collections":
                self.__load_collections(library.id if library else None)
                data = self.collections.get_all_summary()
                data.sort(key=lambda x: x['name'])
                if not library:
                    fields.insert(1, "library")
            case "books":
                try:
                    self.__load_books(library.id)
                    data = self.books.get_all()
                    filter_field = args.field
                    fields = ['media.metadata.title', 'media.metadata.authorName', "id" if with_id else None]
                except NoBooksException as e:
                    print(f"{e}")
                    return
            case "genres":
                self.__load_filters(library.id)
                data = self.filters.get_genres()
                fields = ['name']

        if args.filter:
            data = Utils.apply_filter(data, args.filter, args.exact, filter_field)
        if data:
            Utils.print(data, fields, args.seperator)
        elif args.all:
            print(f"Library with ID '{library.id}': No matches found")

    def __do_search(self, args, display: bool = True, library: Optional[Library] = None):
        if not library:
            self.__load_libraries()
            library = self.libraries.get_by_name(args.library)
        self.__load_books(library.id)

        columns = ['media.metadata.title', 'media.metadata.authorName', "id"]

        where = Utils.replace_shortcuts(args.where)
        sort = Utils.replace_shortcuts(args.sort) or Utils.replace_shortcuts('_TITLE')
        if args.display:
            columns = [Utils.replace_shortcuts(item, False) for item in args.display]
        try:
            result = self.books.where(where, sort)
        except NoBooksException as e:
            print(f"{e}")
            return None, None

        if result:
            if display:
                Utils.print(result, columns)
            return where, result
        elif display:
            print(f"Library with ID '{library.id}': No matches found")
        return where, None

    def perform_search(self, args):
        self.__load_libraries()
        libraries = None
        if args.all:
            libraries = self.libraries.get_all()
        elif args.library:
            library = self.libraries.get_by_name(args.library)
            if not library:
                print(f"Error: Library '{args.library}' not found", file=sys.stderr)
                sys.exit(1)
            libraries = [library] if library else None

        if libraries:
            for library in libraries:
                if args.all:
                    print(f"\n\nLibrary: {library.name}")
                    print("-" * shutil.get_terminal_size().columns)
                self.__do_search(args, True, library)
        else:
            self.__do_search(args, True)


    def perform_create(self, args):
        columns = ['media.metadata.title', 'media.metadata.authorName', "id"]
        if args.display:
            columns = [Utils.replace_shortcuts(item) for item in args.display]

        self.__load_libraries()
        library = self.libraries.get_by_name(args.library)
        self.__load_collections(library.id)
        if self.collections.exists(args.name):
            print(f"Error: Collection '{args.name}' already exists", file=sys.stderr)
            sys.exit(2)
        where, items = self.__do_search(args, False)
        if not items or len(items) == 0:
            print(f"Error: No books found for collection '{args.name}'", file=sys.stderr)
            return
        try:
            describe = f"Auto-created by abscli from query: '{where}'"
            self.collections.create(args.name, describe, library.id, items, dryrun=args.dryrun)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        print(f"Collection '{args.name}' created successfully with the following {len(items)} items:\n")
        Utils.print(items, columns)

    def perform_update(self, args):
        columns = ['media.metadata.title', 'media.metadata.authorName', "id"]
        if args.display:
            columns = [Utils.replace_shortcuts(item) for item in args.display]

        self.__load_libraries()
        library = self.libraries.get_by_name(args.library)
        self.__load_collections(library.id)
        where, items = self.__do_search(args, False)
        if not items or len(items) == 0:
            print(f"Error: No books found for collection '{args.name}'", file=sys.stderr)
            return

        describe = f"Auto-created by abscli from query: '{where}'"
        action = "updated"
        try:
            updated = self.collections.update(args.name, describe, library.id, items, dryrun=args.dryrun)
            if updated and len(updated) == len(items):
                action = "created"
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        if not updated:
            print(f"Collection '{args.name}' not {action}, no new books were found")
        else:
            print(f"Collection '{args.name}' {action} successfully with the following {len(updated)} items:\n")
            Utils.print(updated, columns)

    def perform_info(self, args):
        if args.type == "fields":
            self.__load_libraries()
            library = self.libraries.get_by_name(args.library)
            self.__load_books(library.id)
            data = [{'name': item, 'shortcut': Utils.find_shortcut(item)} for item in self.books.get_fields()]
            data.insert(0, {'name': 'Field', 'shortcut': 'Shortcut'})
            data.insert(1, {'name': '=====', 'shortcut': '============'})
            Utils.print(data, ['name', 'shortcut'])

if __name__ == "__main__":
    main()