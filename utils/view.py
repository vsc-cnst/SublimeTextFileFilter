import sublime
from .logging import CustomLogger
from .utils import stringify

from .enums import FoldingTypes, HighlightTypes

##
##
## keys for view.settings 
##
##

VIEW_SETTINGS_IS_FILTER_ACTIVE = 'file_filter.view_settings.is_filter_active'
VIEW_SETTINGS_CURRENT_REGEX = 'file_filter.view_settings.current_regex'
VIEW_SETTINGS_REGEX_HISTORY = 'file_filter.view_settings.regex_history'
VIEW_SETTINGS_CURRENT_FOLDING_TYPE = 'file_filter.view_settings.current_folding_type'
VIEW_SETTINGS_CURRENT_HIGHLIGHT_TYPE = 'file_filter.view_settings.current_highlight_type'


VIEW_SETTINGS_STATUS_BAR_REGEX = 'file_filter.view_settings.status_bar.regex'
VIEW_SETTINGS_STATUS_BAR_FOLDING_STYLE = 'file_filter.view_settings.status_bar.folding_style'
VIEW_SETTINGS_STATUS_BAR_HIGHLIGHT_STYLE = 'file_filter.view_settings.status_bar.highlight_style'
VIEW_SETTINGS_STATUS_BAR_TOTAL_MATCHES = 'file_filter.view_settings.status_bar.total_matches'
VIEW_SETTINGS_HIGHLIGHTED_REGIONS = 'file_filter.view_settings.highlighted_regions'



def set_current_regex(log, view: sublime.View, settings: sublime.Settings, regex: str) -> str:
    return view.settings().set(VIEW_SETTINGS_CURRENT_REGEX, regex)


def get_current_regex(log, view: sublime.View, settings: sublime.Settings) -> str:
    return view.settings().get(VIEW_SETTINGS_CURRENT_REGEX, None)


def get_folding_type(log, view: sublime.View, settings: sublime.Settings) -> FoldingTypes:
    return set_folding_type(log, view, settings)


def set_folding_type(log, view: sublime.View, settings: sublime.Settings, folding_type=None) -> FoldingTypes:
    log.debug(folding_type)
    
    try:

        if folding_type is None:
            raise ValueError(f"'{stringify(folding_type)}' is not valid. using fallback value")
        elif isinstance(folding_type, str):
            folding_type = FoldingTypes[folding_type]
        elif isinstance(folding_type, FoldingTypes):
            folding_type = folding_type
        else:
            raise ValueError("Invalid folding_type format")
    except Exception as e:
        folding_type = FoldingTypes[view.settings().get(VIEW_SETTINGS_CURRENT_FOLDING_TYPE, settings.get('default_folding_type', FoldingTypes.line.name))]

    log.info(f"folding_type set to '{folding_type.name}'")
    view.settings().set(VIEW_SETTINGS_CURRENT_FOLDING_TYPE, folding_type.name)

    return folding_type


def get_highlight_type(log, view: sublime.View, settings: sublime.Settings) -> HighlightTypes:
    log.debug(settings)
    return set_highlight_type(log, view, settings)


def set_highlight_type(log, view: sublime.View, settings: sublime.Settings, highlight_type=None) -> HighlightTypes:
    log.debug(settings, highlight_type)
    
    try:

        if highlight_type is None:
            raise ValueError(f"'{stringify(highlight_type)}' is not valid. using fallback value")
        elif isinstance(highlight_type, str):
            highlight_type = HighlightTypes[highlight_type]
        elif isinstance(highlight_type, HighlightTypes):
            highlight_type = highlight_type
        else:
            raise ValueError("Invalid highlight_type format")

    except Exception as e:
        highlight_type = HighlightTypes[view.settings().get(VIEW_SETTINGS_CURRENT_HIGHLIGHT_TYPE, settings.get('default_highlight', {}).get('type', HighlightTypes.solid.name))]

    log.info(f"highlight_type set to '{highlight_type.name}'")
    view.settings().set(VIEW_SETTINGS_CURRENT_HIGHLIGHT_TYPE, highlight_type.name)

    return highlight_type


def clear(log, view: sublime.View, unfold_regions=True, remove_highlights=True, center_viewport_on_carret=False):
    log.debug('')

    view.settings().erase(VIEW_SETTINGS_CURRENT_REGEX)
    
    if unfold_regions == True:
        view.unfold(sublime.Region(0, view.size()))
        
    if remove_highlights == True:
        view.erase_regions(VIEW_SETTINGS_HIGHLIGHTED_REGIONS)

    #center view at coursor position
    if center_viewport_on_carret == True:
        view.show_at_center(sublime.Region(0,0) if len(view.sel()) == 0 else view.sel()[0].begin(), False)
    
    view.settings().erase(VIEW_SETTINGS_IS_FILTER_ACTIVE)


def filter(log: CustomLogger, view: sublime.View, regex, folding_type, highlight_type):
    log.info("start view filter")
    log.info("filter", folding_type=folding_type,highlight_type=highlight_type,regex=regex)

    if not regex:
        log.warning("No regex")
        return

    clear(log, view)

    view.settings().set(VIEW_SETTINGS_IS_FILTER_ACTIVE, True)
    view.settings().set(VIEW_SETTINGS_CURRENT_REGEX, regex)

    view_size = view.size()

    matches_regions = view.find_all(regex)
    total_matches_regions = len(matches_regions)

    # status_bar_settings = SETTINGS.get('status_bar', {})

    regions_to_fold = []

    if folding_type is not FoldingTypes.highlight_only and total_matches_regions > 0:

        temp_fold_regions = [sublime.Region(0, 0)] + matches_regions + [sublime.Region(view_size, view_size)]
        fold_regions = [ sublime.Region(prev.end(), curr.begin()) for prev, curr in zip(temp_fold_regions, temp_fold_regions[1:])]
        
        first_fold = fold_regions[0]
        last_fold = fold_regions[-1]
        
        log.debug(fold_regions)

        # fold lines with no match
        for fold in fold_regions:

            log.trace(f'.current fold: {fold}.')
            if fold == first_fold :
                log.trace(f'is first fold')
            if fold == last_fold :
                log.trace(f'is last fold')

            if fold.size() <= 0 or fold.begin() >= fold.end():
                log.trace(f'Invalidfold size. continue..')
                continue

            a = view.full_line(fold.begin())
            b = view.full_line(fold.end())

            log.trace(f'line a: {a}, line b:{b}')

            if a == b:
                log.trace(f'a == b. same line')
                first = sublime.Region(fold.begin(), fold.begin())
                middle = fold
                last = sublime.Region(fold.end(),fold.end()) 
            else:
                first = sublime.Region(fold.begin(), a.end())
                middle = sublime.Region(a.end(),b.begin())
                last = sublime.Region(b.begin(),fold.end())  

            log.trace(f'first {first}, middle {middle}, last {last}')

            if folding_type == FoldingTypes.match_only:

                if fold is first_fold:
                    regions_to_fold.append(calc_span(log, view, [first, middle], remove_last_char=True))
                    regions_to_fold.append(calc_span(log, view, last))
                elif a == b:
                    regions_to_fold.append(calc_span(log, view, [middle], remove_last_char=False))
                else:
                    regions_to_fold.append(calc_span(log, view, [first,middle], remove_last_char=True))
                    regions_to_fold.append(calc_span(log, view, last))

            elif folding_type is FoldingTypes.line:

                if fold is first_fold:
                    regions_to_fold.append(calc_span(log, view, [first, middle], remove_last_char=True))
                if fold is last_fold and a!=b:
                    regions_to_fold.append(calc_span(log, view, [middle, last]))
                elif a != b:
                    middle.a = middle.a - 1
                    regions_to_fold.append(calc_span(log, view, [middle], remove_last_char=True))


            elif folding_type is FoldingTypes.before_only:

                if fold is first_fold:
                    regions_to_fold.append(calc_span(log, view, [first, last], remove_last_char=False))
                elif a != b:
                   regions_to_fold.append(calc_span(log, view, [middle, last], remove_last_char=False))
                else:
                    regions_to_fold.append(calc_span(log, view, [last], remove_last_char=False))

            elif folding_type is FoldingTypes.after_only:

                if fold is last_fold:
                    regions_to_fold.append(calc_span(log, view, fold))
                else:
                    regions_to_fold.append(calc_span(log, view, [first, middle], remove_last_char=True))

    #print("======== regions_to_fold")
    #print([r for r in regions_to_fold if bool(r)])
    #print("========")
    
    log.debug(regions_to_fold=[r for r in regions_to_fold if bool(r)])
    
    ## fold regions
    view.fold([r for r in regions_to_fold if bool(r)])

    if highlight_type is not HighlightTypes.none:
        view.add_regions(
            key = VIEW_SETTINGS_HIGHLIGHTED_REGIONS  # Key for the highlighted regions
            , regions = matches_regions  # List of regions to highlight
            , scope = 'highlight'  # Scope name (use a predefined or custom scope)
            , icon = ''  # No icon
            , flags = highlight_type.value
            , annotations = [] # annotations
            , annotation_color = "#32a852" # color
        )
        
    return regions_to_fold


# def highlight(log, view: sublime.View, expression, matches_regions):
    
#     log.debug(expression=expression, matches_regions=[r for r in regions_to_fold if bool(r)])
    

#     for match in matches_regions:
#         if highlight_type is not HighlightTypes.none:
#             view.add_regions(
#                 key = VIEW_SETTINGS_HIGHLIGHTED_REGIONS  # Key for the highlighted regions
#                 , regions = matches_regions  # List of regions to highlight
#                 , scope = 'highlight'  # Scope name (use a predefined or custom scope)
#                 , icon = ''  # No icon
#                 , flags = highlight_type.value
#                 , annotations = [] # annotations
#                 , annotation_color = "#32a852" # color
#             )
        


def calc_span(log, view: sublime.View, source, remove_last_char=False):
        log.debug(remove_last_char)
        
        if type(source) is list:
            a = min([ r.a for r in source])
            b = max([ r.b for r in source]) - (1 if remove_last_char else 0)
        else:
            a = source.a
            b = source.b - (1 if remove_last_char else 0)

        if b <= a:
            log.debug(f"from {source} NOT folding {(a, b)}, remove_last_char: {remove_last_char}")
            return False
        
        log.debug(f"from {source} folding {(a, b)}, remove_last_char: {remove_last_char}")

        return sublime.Region(a, b)


def add_to_history(logger, view: sublime.View, item):
    history = view.settings().get(VIEW_SETTINGS_REGEX_HISTORY, [])
    logger.debug(history_before=history)
    history.insert(0, item)
    history = [h for h in history if bool(h)][:100]
    view.settings().set(VIEW_SETTINGS_REGEX_HISTORY, history)
    logger.debug(history_after=history)
