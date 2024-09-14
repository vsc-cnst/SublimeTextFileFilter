import sublime # type: ignore

def create_preview(
    main: (str, str) = None,
    sub_items: list = []
):
    # Prepare content for the main item, if provided
    main_html = f'<div class="item"><span>{main[0]}</span>&nbsp;<span>{main[1]}</span></div>' if main else ''

    # Prepare content for sub-items
    sub_items_html = ''.join(
        f'<div class="item"><span>{item[0]}</span>&nbsp;<span><i>{item[1]}</i></span></div>'
        for item in sub_items
    )

    return sublime.Html(f"""
<html>
<head>
<style>
    .container {{
        overflow: hidden;
        margin: 0px;
        padding: 0px;
        box-sizing: border-box;
    }}
    .main-container {{
        font-size: 15px;
        font-weight: bold;
        padding-bottom: 1px;
        overflow-x: auto; /* Add horizontal scrollbar if needed */
        white-space: nowrap; /* Prevent wrapping */
    }}
    .sub-container {{
        font-size: 10px;
        overflow-x: auto; /* Add horizontal scrollbar if needed */
        white-space: nowrap; /* Prevent wrapping */
    }}
    .item {{
        display: inline-block;
        margin-right: 10px;
    }}
</style>
</head>
<body>
    <div class="container main-container">
        {main_html}
    </div>
    <div class="container sub-container">
        {sub_items_html}
    </div>
</body>
</html>
""")
